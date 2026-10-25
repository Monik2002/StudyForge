import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from studyforge.config import settings
from studyforge.db import Base, engine, get_db
from studyforge.models import User, Course, Source, QuestionSet, Question, Attempt, AttemptResponse
from studyforge.ai import generate_questions, validate_question, extract_document_content, AIProviderError

app=FastAPI(title="StudyForge API",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto"); bearer=HTTPBearer(auto_error=False)
@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)
@app.get("/health")
def health(): return {"status":"ok","environment":settings.app_env}
def current_user(creds:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db)):
    if not creds: raise HTTPException(401,"Authentication required")
    try: uid=jwt.decode(creds.credentials,settings.jwt_secret,algorithms=["HS256"]).get("sub")
    except JWTError: raise HTTPException(401,"Invalid or expired token")
    user=db.get(User,uid) if uid else None
    if not user: raise HTTPException(401,"Invalid or expired token")
    return user
def token(user):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub":user.id,"exp":exp},settings.jwt_secret,algorithm="HS256")
def owned(model,id,user,db):
    obj=db.scalar(select(model).where(model.id==id,model.owner_user_id==user.id))
    if not obj: raise HTTPException(404,"Resource not found")
    return obj
def get_set(id,user,db):
    obj=db.execute(select(QuestionSet).options(joinedload(QuestionSet.questions)).where(QuestionSet.id==id,QuestionSet.owner_user_id==user.id)).unique().scalar_one_or_none()
    if not obj: raise HTTPException(404,"Question set not found")
    return obj
def qdict(q,answers=True):
    d={"id":q.id,"key":q.id,"ordinal":q.ordinal,"qtype":q.qtype,"stem":q.stem,"options":q.options}
    if answers:d.update(correct_option_ids=q.correct_option_ids,explanation=q.explanation,difficulty=q.difficulty,topic_tags=q.topic_tags,source_excerpt=q.source_excerpt)
    return d
def setdict(s): return {"id":s.id,"course_id":s.course_id,"source_id":s.source_id,"title":s.title,"status":s.status,"model_id":s.model_id,"created_at":s.created_at,"questions":[qdict(q) for q in sorted(s.questions,key=lambda x:x.ordinal)]}
def get_attempt(id,user,db):
    a=db.execute(select(Attempt).options(joinedload(Attempt.responses)).where(Attempt.id==id,Attempt.owner_user_id==user.id)).unique().scalar_one_or_none()
    if not a:raise HTTPException(404,"Attempt not found")
    return a
def attemptdict(a):
    rs={r.question_key:r for r in a.responses}
    questions=[]
    for q in a.question_snapshot:
        response=rs.get(q["key"])
        questions.append({
            "id":q["key"],"key":q["key"],"ordinal":q["ordinal"],"qtype":q["qtype"],
            "stem":q["stem"],"options":q["options"],
            "selected_option_ids":response.selected_option_ids if response else [],
            "is_flagged":response.is_flagged if response else False,
        })
    return {"id":a.id,"mode":a.mode,"status":a.status,"started_at":a.started_at,"expires_at":a.expires_at,"duration_seconds":a.duration_seconds,
    "questions":questions}
def finalize(db,a,expired=False):
    rs={r.question_key:r for r in a.responses}; earned=0
    for q in a.question_snapshot:
        r=rs.get(q["key"]); selected=set(r.selected_option_ids if r else [])
        correct=selected==set(q["correct_option_ids"])
        if r:r.is_correct=correct;r.awarded_points=1 if correct else 0
        earned+=int(correct)
    a.max_points=float(len(a.question_snapshot));a.score_points=float(earned)
    a.percentage=round(earned/len(a.question_snapshot)*100,2) if a.question_snapshot else 0
    a.passed=a.percentage>=a.passing_score;a.status="expired" if expired else "submitted";a.submitted_at=datetime.now(timezone.utc)
def resultdict(a):
    rs={r.question_key:r for r in a.responses}; qs=[]
    for q in a.question_snapshot:
        r=rs.get(q["key"]);sel=r.selected_option_ids if r else []
        qs.append({**q,"selected_option_ids":sel,"is_correct":set(sel)==set(q["correct_option_ids"])})
    return {"id":a.id,"mode":a.mode,"status":a.status,"score_points":a.score_points or 0,"max_points":a.max_points or 0,"percentage":a.percentage or 0,"passed":bool(a.passed),"submitted_at":a.submitted_at,"questions":qs}

class AuthIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=10,max_length=128)
class CourseIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);description:str=""
class SourceIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);content:str=Field(min_length=50)
class GenerateIn(BaseModel):
    title:str=Field(min_length=1,max_length=200);question_count:int=Field(default=10,ge=1,le=40)
    question_types:list[str]=Field(default_factory=lambda:["single_choice"]);difficulty:str="mixed"
class StartIn(BaseModel):
    duration_minutes:int=Field(default=30,ge=1,le=240);passing_score:float=Field(default=70,ge=0,le=100)
class AnswerIn(BaseModel):
    selected_option_ids:list[str]=Field(default_factory=list);is_flagged:bool=False

@app.post("/api/v1/auth/register",status_code=201)
def register(x:AuthIn,db:Session=Depends(get_db)):
    email=x.email.lower()
    if db.scalar(select(User).where(User.email==email)):raise HTTPException(409,"Email already registered")
    u=User(email=email,password_hash=pwd.hash(x.password));db.add(u);db.commit();db.refresh(u)
    return {"access_token":token(u),"token_type":"bearer"}
@app.post("/api/v1/auth/login")
def login(x:AuthIn,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==x.email.lower()))
    if not u or not pwd.verify(x.password,u.password_hash):raise HTTPException(401,"Invalid email or password")
    return {"access_token":token(u),"token_type":"bearer"}
@app.get("/api/v1/auth/me")
def me(u:User=Depends(current_user)):return {"id":u.id,"email":u.email}
@app.get("/api/v1/courses")
def courses(db:Session=Depends(get_db),u:User=Depends(current_user)):
    return [{"id":c.id,"title":c.title,"description":c.description,"created_at":c.created_at} for c in db.scalars(select(Course).where(Course.owner_user_id==u.id).order_by(Course.created_at.desc()))]
@app.post("/api/v1/courses",status_code=201)
def create_course(x:CourseIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    c=Course(owner_user_id=u.id,title=x.title.strip(),description=x.description);db.add(c);db.commit();db.refresh(c)
    return {"id":c.id,"title":c.title,"description":c.description,"created_at":c.created_at}
@app.post("/api/v1/courses/{cid}/sources/text",status_code=201)
def source(cid:str,x:SourceIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    owned(Course,cid,u,db)
    if len(x.content)>settings.max_source_chars:raise HTTPException(413,"Notes exceed configured character limit")
    text=x.content.strip();s=Source(course_id=cid,owner_user_id=u.id,title=x.title,content=text,content_sha256=hashlib.sha256(text.encode()).hexdigest());db.add(s);db.commit();db.refresh(s)
    return {"id":s.id,"course_id":cid,"title":s.title,"content_sha256":s.content_sha256,"created_at":s.created_at}
@app.post("/api/v1/courses/{cid}/sources/upload", status_code=201)
async def upload_source(cid: str, file: UploadFile = File(...), title: str | None = Form(default=None), db: Session = Depends(get_db), u: User = Depends(current_user)):
    """Upload notes. PDF/images use a vision model; DOCX/TXT/MD are extracted locally."""
    owned(Course, cid, u, db)
    filename = (file.filename or "upload").replace("\\", "/").split("/")[-1]
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    supported = {"pdf", "docx", "txt", "md", "markdown", "png", "jpg", "jpeg", "webp"}
    if suffix not in supported:
        raise HTTPException(415, "Unsupported file type. Upload PDF, DOCX, TXT, Markdown, PNG, JPG, or WEBP.")
    data = await file.read(20 * 1024 * 1024 + 1)
    await file.close()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "File exceeds the 20 MB upload limit.")
    if not data:
        raise HTTPException(422, "The uploaded file is empty.")
    mime_by_suffix = {"pdf":"application/pdf", "docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "txt":"text/plain", "md":"text/markdown", "markdown":"text/markdown", "png":"image/png", "jpg":"image/jpeg", "jpeg":"image/jpeg", "webp":"image/webp"}
    mime = mime_by_suffix[suffix]
    try:
        if suffix in {"txt", "md", "markdown"}:
            content = data.decode("utf-8-sig")
        elif suffix == "docx":
            from docx import Document
            import io
            doc = Document(io.BytesIO(data))
            chunks = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                chunks.extend(" | ".join(cell.text.strip() for cell in row.cells) for row in table.rows)
            # Include embedded diagrams/screenshots when present. Limit image count to
            # bound cost and processing time for large documents.
            import zipfile, mimetypes
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                media_names = [n for n in archive.namelist() if n.startswith("word/media/") and not n.endswith("/")][:12]
                for image_name in media_names:
                    image_data = archive.read(image_name)
                    image_mime = mimetypes.guess_type(image_name)[0]
                    if image_mime in {"image/png", "image/jpeg", "image/webp"}:
                        description = extract_document_content(image_name, image_data, image_mime)
                        chunks.append("\n[Visual content from embedded image " + image_name.rsplit("/", 1)[-1] + "]\n" + description)
            content = "\n".join(chunks)
        else:
            content = extract_document_content(filename, data, mime)
    except UnicodeDecodeError:
        raise HTTPException(422, "Text file must use UTF-8 encoding.")
    except AIProviderError as e:
        raise HTTPException(502, str(e))
    except Exception as e:
        raise HTTPException(422, f"Could not read this document ({type(e).__name__}). Try exporting it as PDF or DOCX.")
    content = content.strip()
    if len(content) < 50:
        raise HTTPException(422, "Not enough readable content was found in this file.")
    if len(content) > settings.max_source_chars:
        content = content[:settings.max_source_chars]
    source_title = (title or filename).strip()[:200]
    s = Source(course_id=cid, owner_user_id=u.id, title=source_title, content=content, content_sha256=hashlib.sha256(content.encode()).hexdigest())
    db.add(s); db.commit(); db.refresh(s)
    return {"id":s.id,"course_id":cid,"title":s.title,"filename":filename,"content_sha256":s.content_sha256,"created_at":s.created_at,"extraction":"vision" if suffix in {"pdf","png","jpg","jpeg","webp"} else "text"}

@app.get("/api/v1/courses/{cid}/question-sets")
def list_sets(cid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    owned(Course,cid,u,db)
    sets=db.execute(select(QuestionSet).options(joinedload(QuestionSet.questions)).where(QuestionSet.course_id==cid,QuestionSet.owner_user_id==u.id).order_by(QuestionSet.created_at.desc())).unique().scalars()
    return [setdict(s) for s in sets]
@app.post("/api/v1/sources/{sid}/question-sets",status_code=201)
def generate(sid:str,x:GenerateIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    s=owned(Source,sid,u,db)
    if not x.question_types or not set(x.question_types)<={"single_choice","multiple_select","true_false"}:raise HTTPException(422,"Invalid question types")
    try:
        raw,model=generate_questions(s.content,x.title,x.question_count,x.question_types,x.difficulty)
        if len(raw)!=x.question_count:raise ValueError("Model returned unexpected question count")
        qs=[validate_question(q,i+1) for i,q in enumerate(raw)]
    except (AIProviderError,ValueError) as e:raise HTTPException(502,f"Question generation failed: {e}")
    qset=QuestionSet(course_id=s.course_id,source_id=s.id,owner_user_id=u.id,title=x.title,status="draft",model_id=model,generation_config=x.model_dump())
    db.add(qset);db.flush()
    for q in qs:db.add(Question(question_set_id=qset.id,ordinal=q["ordinal"],qtype=q["qtype"],stem=q["stem"],options=q["options"],correct_option_ids=q["correct_option_ids"],explanation=q["explanation"],difficulty=q["difficulty"],topic_tags=q["topic_tags"],source_excerpt=q["source_excerpt"]))
    db.commit();return setdict(get_set(qset.id,u,db))
@app.get("/api/v1/question-sets/{sid}")
def read_set(sid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):return setdict(get_set(sid,u,db))
@app.post("/api/v1/question-sets/{sid}/approve")
def approve(sid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    s=get_set(sid,u,db)
    if s.status!="draft":raise HTTPException(409,"Only draft sets can be approved")
    for q in s.questions:
        ids={o["id"] for o in q.options}
        if not q.correct_option_ids or not set(q.correct_option_ids)<=ids:raise HTTPException(422,f"Question {q.ordinal} has invalid answer IDs")
        if q.qtype in {"single_choice","true_false"} and len(q.correct_option_ids)!=1:raise HTTPException(422,"Invalid answer count")
    s.status="approved";s.approved_at=datetime.now(timezone.utc);db.commit();return setdict(get_set(sid,u,db))
def start(sid,mode,x,db,u):
    s=get_set(sid,u,db)
    if s.status!="approved":raise HTTPException(409,"Approve question set first")
    now=datetime.now(timezone.utc);duration=x.duration_minutes*60 if mode=="exam" else None
    snap=[{"key":q.id,"ordinal":q.ordinal,"qtype":q.qtype,"stem":q.stem,"options":q.options,"correct_option_ids":q.correct_option_ids,"explanation":q.explanation,"source_excerpt":q.source_excerpt,"topic_tags":q.topic_tags} for q in sorted(s.questions,key=lambda q:q.ordinal)]
    a=Attempt(owner_user_id=u.id,course_id=s.course_id,question_set_id=s.id,mode=mode,status="in_progress",question_snapshot=snap,duration_seconds=duration,started_at=now,expires_at=now+timedelta(seconds=duration) if duration else None,passing_score=x.passing_score)
    db.add(a);db.commit();db.refresh(a);return attemptdict(a)
@app.post("/api/v1/question-sets/{sid}/practice-attempts",status_code=201)
def practice(sid:str,x:StartIn,db:Session=Depends(get_db),u:User=Depends(current_user)):return start(sid,"practice",x,db,u)
@app.post("/api/v1/question-sets/{sid}/exam-attempts",status_code=201)
def exam(sid:str,x:StartIn,db:Session=Depends(get_db),u:User=Depends(current_user)):return start(sid,"exam",x,db,u)
@app.get("/api/v1/attempts/{aid}")
def get_active(aid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    a=get_attempt(aid,u,db)
    if a.status!="in_progress":raise HTTPException(409,"Attempt finalized; use results endpoint")
    if a.mode=="exam" and a.expires_at and datetime.now(timezone.utc)>=a.expires_at:
        finalize(db,a,True);db.commit();raise HTTPException(409,"Exam time expired and was finalized")
    return attemptdict(a)
@app.put("/api/v1/attempts/{aid}/responses/{key}")
def save(aid:str,key:str,x:AnswerIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    a=get_attempt(aid,u,db)
    if a.status!="in_progress":raise HTTPException(409,"Attempt finalized")
    if a.mode=="exam" and a.expires_at and datetime.now(timezone.utc)>=a.expires_at:
        finalize(db,a,True);db.commit();raise HTTPException(409,"Exam expired")
    q=next((q for q in a.question_snapshot if q["key"]==key),None)
    if not q:raise HTTPException(404,"Question not found")
    if not set(x.selected_option_ids)<={o["id"] for o in q["options"]}:raise HTTPException(422,"Invalid option IDs")
    r=db.scalar(select(AttemptResponse).where(AttemptResponse.attempt_id==aid,AttemptResponse.question_key==key))
    if not r:r=AttemptResponse(attempt_id=aid,question_key=key);db.add(r)
    r.selected_option_ids=x.selected_option_ids;r.is_flagged=x.is_flagged;r.answered_at=datetime.now(timezone.utc);db.commit()
    return {"saved":True}
@app.post("/api/v1/attempts/{aid}/responses/{key}/check")
def check(aid:str,key:str,x:AnswerIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    a=get_attempt(aid,u,db)
    if a.mode!="practice":raise HTTPException(403,"Immediate feedback is only available in practice mode")
    if a.status!="in_progress":raise HTTPException(409,"Attempt finalized")
    q=next((q for q in a.question_snapshot if q["key"]==key),None)
    if not q:raise HTTPException(404,"Question not found")
    return {"question_key":key,"is_correct":set(x.selected_option_ids)==set(q["correct_option_ids"]),"correct_option_ids":q["correct_option_ids"],"explanation":q["explanation"],"source_excerpt":q["source_excerpt"]}
@app.post("/api/v1/attempts/{aid}/submit")
def submit(aid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    a=get_attempt(aid,u,db)
    if a.status=="in_progress":
        expired=bool(a.mode=="exam" and a.expires_at and datetime.now(timezone.utc)>=a.expires_at)
        finalize(db,a,expired);db.commit()
    return resultdict(get_attempt(aid,u,db))
@app.get("/api/v1/attempts/{aid}/results")
def results(aid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    a=get_attempt(aid,u,db)
    if a.status not in {"submitted","expired"}:raise HTTPException(409,"Submit before viewing results")
    return resultdict(a)
@app.get("/api/v1/courses/{cid}/progress")
def progress(cid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
    owned(Course,cid,u,db); ats=list(db.scalars(select(Attempt).where(Attempt.course_id==cid,Attempt.owner_user_id==u.id,Attempt.status.in_(["submitted","expired"]))))
    ps=[a.percentage for a in ats if a.percentage is not None]
    return {"completed_attempts":len(ps),"average_percentage":round(sum(ps)/len(ps),2) if ps else None,"best_percentage":max(ps) if ps else None}
