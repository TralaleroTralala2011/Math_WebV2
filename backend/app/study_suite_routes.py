"""Verified question bank, timed practice exams and spaced review.
Only curated and independently checked items are published. No claims of full coverage.
"""
import json, random, secrets, sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from .auth.routes import get_current_user

router=APIRouter(prefix='/api/study-suite', tags=['study-suite'])
DB=Path(__file__).resolve().parents[2]/'database'/'study_suite.sqlite3'
CATALOG=Path(__file__).resolve().parents[2]/'learn-assets'/'topics.json'
NOW=lambda:datetime.now(timezone.utc)
# All items below have manually checked answers; this is an initial small bank, not 150-topic coverage.
SEED=[
('ham_so_bac_hai','vertex','Tìm hoành độ đỉnh của y=x²-6x+2.','3','Với a=1,b=-6, x=-b/(2a)=3.',2),
('ham_so_bac_hai','roots','Giải phương trình x²-5x+6=0. Chọn nghiệm lớn hơn.','3','(x-2)(x-3)=0, nghiệm lớn hơn là 3.',2),
('ham_so_bac_hai','evaluation','Cho f(x)=x²-4x+1. Tính f(2).','-3','f(2)=4-8+1=-3.',1),
('dao_ham','power_rule','Cho f(x)=x³. Tính f\'(2).','12','f\'(x)=3x², suy ra f\'(2)=12.',2),
('dao_ham','tangent_slope','Tính hệ số góc tiếp tuyến của y=x²+2x tại x=1.','4','y\'=2x+2, tại x=1 bằng 4.',2),
('gioi_han','polynomial','Tính lim(x→2) (x²+3).','7','Đa thức liên tục, thay x=2 được 7.',1),
('nguyen_ham_tich_phan','definite_integral','Tính tích phân từ 0 đến 2 của 3x² dx.','8','Nguyên hàm x³, giá trị 8-0=8.',2),
('phuong_trinh','linear','Giải 5x-7=18.','5','5x=25 nên x=5.',1),
('phuong_trinh','fractions','Giải (x+1)/2=4.','7','x+1=8 nên x=7.',1),
]
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB,timeout=15); c.row_factory=sqlite3.Row
 c.execute('PRAGMA journal_mode=WAL')
 c.executescript("""CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY,topic TEXT NOT NULL,kind TEXT NOT NULL,prompt TEXT NOT NULL,answer TEXT NOT NULL,solution TEXT NOT NULL,difficulty INTEGER NOT NULL,source TEXT NOT NULL,verified INTEGER NOT NULL DEFAULT 0,UNIQUE(topic,kind,prompt));
 CREATE TABLE IF NOT EXISTS exams(id TEXT PRIMARY KEY,user_id INTEGER NOT NULL,started TEXT NOT NULL,deadline TEXT NOT NULL,submitted TEXT,score REAL,answers TEXT,question_ids TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS reviews(user_id INTEGER NOT NULL,question_id INTEGER NOT NULL,interval_days INTEGER NOT NULL,ease REAL NOT NULL,due TEXT NOT NULL,last_correct INTEGER NOT NULL,PRIMARY KEY(user_id,question_id));""")
 for topic,kind,prompt,answer,solution,difficulty in SEED:
  c.execute('INSERT OR IGNORE INTO questions(topic,kind,prompt,answer,solution,difficulty,source,verified) VALUES(?,?,?,?,?,?,?,1)',(topic,kind,prompt,answer,solution,difficulty,'MATH_WEB curated starter bank'))
 c.commit();return c
def uid(auth):
 u=get_current_user(auth)
 if not u: raise HTTPException(401,'Cần đăng nhập')
 return int(u['id'])
def norm(x):
 try:return float(str(x).strip().replace(',','.'))
 except (ValueError,TypeError):return None
def correct(given,expected):
 a,b=norm(given),norm(expected)
 return a is not None and b is not None and abs(a-b)<1e-8*max(1,abs(b))
def public(q):return {k:q[k] for k in ('id','topic','kind','prompt','difficulty')}
@router.get('/bank')
def bank(topic: str|None=None):
 with connect() as c:
  rows=c.execute('SELECT topic,kind,difficulty,COUNT(*) AS count FROM questions WHERE verified=1 AND (? IS NULL OR topic=?) GROUP BY topic,kind,difficulty ORDER BY topic,kind',(topic,topic)).fetchall()
  total=c.execute('SELECT COUNT(*) FROM questions WHERE verified=1').fetchone()[0]
 return {'verified_questions':total,'groups':[dict(r) for r in rows],'coverage':'limited_curated_seed','note':'Chỉ thống kê câu hỏi đã kiểm chứng; chưa phủ hết 150 chủ đề.'}
class Start(BaseModel):
 topic: str|None=None
 minutes:int=Field(default=15,ge=1,le=180)
 count:int=Field(default=5,ge=1,le=50)
@router.post('/exams')
def start(req:Start,authorization:str|None=Header(default=None)):
 user=uid(authorization)
 with connect() as c:
  rows=c.execute('SELECT * FROM questions WHERE verified=1 AND (? IS NULL OR topic=?)',(req.topic,req.topic)).fetchall()
  if not rows:raise HTTPException(404,'Chưa có câu hỏi được kiểm chứng cho chủ đề này')
  chosen=random.sample(rows,min(req.count,len(rows)))
  exam_id=secrets.token_urlsafe(18); start=NOW(); deadline=start+timedelta(minutes=req.minutes)
  c.execute('INSERT INTO exams(id,user_id,started,deadline,question_ids) VALUES(?,?,?,?,?)',(exam_id,user,start.isoformat(),deadline.isoformat(),json.dumps([r['id'] for r in chosen])))
 return {'exam_id':exam_id,'deadline':deadline.isoformat(),'questions':[public(r) for r in chosen],'actual_count':len(chosen),'requested_count':req.count}
def exam_for(c,exam_id,user):
 row=c.execute('SELECT * FROM exams WHERE id=? AND user_id=?',(exam_id,user)).fetchone()
 if not row:raise HTTPException(404,'Không tìm thấy bài thi')
 return row
@router.get('/exams/{exam_id}')
def get_exam(exam_id:str,authorization:str|None=Header(default=None)):
 user=uid(authorization)
 with connect() as c:
  exam=exam_for(c,exam_id,user);ids=json.loads(exam['question_ids']);rows=[c.execute('SELECT * FROM questions WHERE id=?',(i,)).fetchone() for i in ids]
  data={'exam_id':exam_id,'deadline':exam['deadline'],'submitted':bool(exam['submitted']),'questions':[public(r) for r in rows if r]}
  if exam['submitted']:data['result']=results(rows,json.loads(exam['answers']))
 return data
class Submit(BaseModel):
 answers:dict[str,str]=Field(default_factory=dict)
def results(rows,answers):
 details=[]
 for r in rows:
  val=answers.get(str(r['id']),'');ok=correct(val,r['answer'])
  details.append({**public(r),'given':val,'correct':ok,'expected':r['answer'],'solution':r['solution']})
 return {'score':round(10*sum(d['correct'] for d in details)/len(details),2) if details else 0,'correct_count':sum(d['correct'] for d in details),'total':len(details),'details':details,'weak_topics':sorted({d['topic'] for d in details if not d['correct']})}
def schedule(c,user,qid,ok):
 old=c.execute('SELECT * FROM reviews WHERE user_id=? AND question_id=?',(user,qid)).fetchone()
 days=(min(60,max(1,round(old['interval_days']*old['ease']))) if old and ok else (1 if ok else 0))
 ease=min(2.8,max(1.3,(old['ease'] if old else 2.2)+(0.1 if ok else -0.25)))
 due=(NOW()+timedelta(days=days) if days else NOW()+timedelta(hours=8)).isoformat()
 c.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?) ON CONFLICT(user_id,question_id) DO UPDATE SET interval_days=excluded.interval_days,ease=excluded.ease,due=excluded.due,last_correct=excluded.last_correct',(user,qid,days,ease,due,int(ok)))
@router.post('/exams/{exam_id}/submit')
def submit(exam_id:str,req:Submit,authorization:str|None=Header(default=None)):
 user=uid(authorization)
 with connect() as c:
  exam=exam_for(c,exam_id,user)
  if exam['submitted']:raise HTTPException(409,'Bài thi đã nộp, không thể nộp lại')
  if NOW()>datetime.fromisoformat(exam['deadline']):raise HTTPException(409,'Đã hết giờ. Bài thi chưa được nộp; hãy liên hệ hệ thống để xử lý.')
  ids=json.loads(exam['question_ids']);rows=[c.execute('SELECT * FROM questions WHERE id=?',(i,)).fetchone() for i in ids]
  safe={str(i):req.answers.get(str(i),'')[:100] for i in ids}
  report=results(rows,safe)
  c.execute('UPDATE exams SET submitted=?,score=?,answers=? WHERE id=?',(NOW().isoformat(),report['score'],json.dumps(safe),exam_id))
  for d in report['details']:schedule(c,user,d['id'],d['correct'])
 return report
@router.get('/review')
def review(authorization:str|None=Header(default=None)):
 user=uid(authorization)
 with connect() as c:
  rows=c.execute('SELECT q.id,q.topic,q.kind,q.prompt,q.difficulty,r.due,r.last_correct FROM reviews r JOIN questions q ON q.id=r.question_id WHERE r.user_id=? AND r.due<=? ORDER BY r.last_correct ASC,r.due ASC LIMIT 30',(user,NOW().isoformat())).fetchall()
 return {'due':[dict(r) for r in rows],'note':'Lịch ôn được tạo từ câu đã làm trong phòng thi; không suy đoán các chủ đề chưa kiểm tra.'}
class ReviewAnswer(BaseModel):
 question_id:int
 answer:str=Field(max_length=100)
@router.post('/review/answer')
def review_answer(req:ReviewAnswer,authorization:str|None=Header(default=None)):
 user=uid(authorization)
 with connect() as c:
  row=c.execute('SELECT q.*,r.due FROM questions q JOIN reviews r ON r.question_id=q.id WHERE r.user_id=? AND q.id=?',(user,req.question_id)).fetchone()
  if not row:raise HTTPException(404,'Chưa có lịch ôn cho câu này')
  if datetime.fromisoformat(row['due'])>NOW():raise HTTPException(409,'Câu hỏi chưa đến hạn ôn')
  ok=correct(req.answer,row['answer']);schedule(c,user,req.question_id,ok)
 return {'correct':ok,'expected':row['answer'],'solution':row['solution']}
