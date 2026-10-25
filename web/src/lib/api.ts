const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export type Option={id:string;text:string};
export type Question={id?:string;key?:string;ordinal:number;qtype:string;stem:string;options:Option[];correct_option_ids?:string[];explanation?:string;difficulty?:string;topic_tags?:string[];source_excerpt?:string;selected_option_ids?:string[];is_flagged?:boolean};
export type Course={id:string;title:string;description:string;created_at:string};
export type QuestionSet={id:string;course_id:string;source_id:string|null;title:string;status:string;model_id:string;created_at:string;questions:Question[]};
export type Attempt={id:string;mode:string;status:string;started_at:string;expires_at:string|null;duration_seconds:number|null;questions:Question[]};
export type Result={id:string;mode:string;status:string;score_points:number;max_points:number;percentage:number;passed:boolean;submitted_at:string|null;questions:(Question&{selected_option_ids:string[];is_correct:boolean})[]};
export function getToken(){return typeof window==="undefined"?null:localStorage.getItem("sf_token")}
export function setToken(t:string){localStorage.setItem("sf_token",t)}
export function clearToken(){localStorage.removeItem("sf_token")}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const h=new Headers(options.headers);const t=getToken();if(t)h.set("Authorization",`Bearer ${t}`);if(options.body&&!h.has("Content-Type"))h.set("Content-Type","application/json");
 let r:Response;try{r=await fetch(`${API}${path}`,{...options,headers:h,cache:"no-store"})}catch{throw new Error("Could not reach the API. Check that the backend is running.")}
 if(!r.ok){let m=`Request failed (${r.status})`;try{const b=await r.json();m=typeof b.detail==="string"?b.detail:m}catch{}throw new Error(m)}return r.json()
}

export async function uploadFile<T>(path:string,file:File,title?:string):Promise<T>{
 const h=new Headers();const t=getToken();if(t)h.set("Authorization",`Bearer ${t}`);const body=new FormData();body.append("file",file);if(title)body.append("title",title);
 let r:Response;try{r=await fetch(`${API}${path}`,{method:"POST",headers:h,body,cache:"no-store"})}catch{throw new Error("Could not reach the API. Check that the backend is running.")}
 if(!r.ok){let m=`Request failed (${r.status})`;try{const b=await r.json();m=typeof b.detail==="string"?b.detail:m}catch{}throw new Error(m)}return r.json()
}
