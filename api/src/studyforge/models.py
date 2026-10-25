import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Boolean, Float, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from studyforge.db import Base
def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid.uuid4())
class User(Base):
    __tablename__="users"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    email: Mapped[str]=mapped_column(String(320),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Course(Base):
    __tablename__="courses"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    owner_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    title: Mapped[str]=mapped_column(String(200))
    description: Mapped[str]=mapped_column(Text,default="")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Source(Base):
    __tablename__="sources"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    course_id: Mapped[str]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE"),index=True)
    owner_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    title: Mapped[str]=mapped_column(String(200))
    content: Mapped[str]=mapped_column(Text)
    content_sha256: Mapped[str]=mapped_column(String(64))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class QuestionSet(Base):
    __tablename__="question_sets"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    course_id: Mapped[str]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE"),index=True)
    source_id: Mapped[str|None]=mapped_column(ForeignKey("sources.id",ondelete="SET NULL"),nullable=True)
    owner_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    title: Mapped[str]=mapped_column(String(200))
    status: Mapped[str]=mapped_column(String(20),default="draft")
    model_id: Mapped[str]=mapped_column(String(100),default="mock")
    generation_config: Mapped[dict]=mapped_column(JSON,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    approved_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    questions=relationship("Question",back_populates="question_set",cascade="all, delete-orphan")
class Question(Base):
    __tablename__="questions"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    question_set_id: Mapped[str]=mapped_column(ForeignKey("question_sets.id",ondelete="CASCADE"),index=True)
    ordinal: Mapped[int]=mapped_column(Integer)
    qtype: Mapped[str]=mapped_column(String(30))
    stem: Mapped[str]=mapped_column(Text)
    options: Mapped[list]=mapped_column(JSON,default=list)
    correct_option_ids: Mapped[list]=mapped_column(JSON,default=list)
    explanation: Mapped[str]=mapped_column(Text,default="")
    difficulty: Mapped[str]=mapped_column(String(20),default="medium")
    topic_tags: Mapped[list]=mapped_column(JSON,default=list)
    source_excerpt: Mapped[str]=mapped_column(Text,default="")
    __table_args__=(UniqueConstraint("question_set_id","ordinal",name="uq_set_ordinal"),)
    question_set=relationship("QuestionSet",back_populates="questions")
class Attempt(Base):
    __tablename__="assessment_attempts"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    owner_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    course_id: Mapped[str]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE"),index=True)
    question_set_id: Mapped[str]=mapped_column(ForeignKey("question_sets.id",ondelete="CASCADE"),index=True)
    mode: Mapped[str]=mapped_column(String(20))
    status: Mapped[str]=mapped_column(String(20),default="in_progress")
    question_snapshot: Mapped[list]=mapped_column(JSON)
    duration_seconds: Mapped[int|None]=mapped_column(Integer,nullable=True)
    started_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    expires_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    submitted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    score_points: Mapped[float|None]=mapped_column(Float,nullable=True)
    max_points: Mapped[float|None]=mapped_column(Float,nullable=True)
    percentage: Mapped[float|None]=mapped_column(Float,nullable=True)
    passed: Mapped[bool|None]=mapped_column(Boolean,nullable=True)
    passing_score: Mapped[float]=mapped_column(Float,default=70)
    responses=relationship("AttemptResponse",back_populates="attempt",cascade="all, delete-orphan")
class AttemptResponse(Base):
    __tablename__="attempt_responses"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    attempt_id: Mapped[str]=mapped_column(ForeignKey("assessment_attempts.id",ondelete="CASCADE"),index=True)
    question_key: Mapped[str]=mapped_column(String(36))
    selected_option_ids: Mapped[list]=mapped_column(JSON,default=list)
    is_flagged: Mapped[bool]=mapped_column(Boolean,default=False)
    answered_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    is_correct: Mapped[bool|None]=mapped_column(Boolean,nullable=True)
    awarded_points: Mapped[float|None]=mapped_column(Float,nullable=True)
    __table_args__=(UniqueConstraint("attempt_id","question_key",name="uq_attempt_question"),)
    attempt=relationship("Attempt",back_populates="responses")
