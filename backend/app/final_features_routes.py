import os
"""Features 10-12: restricted teacher/admin workflow, evidence-based achievements, publication QA."""
import json, sqlite3, hashlib, threading
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from .auth.routes import get_current_user
from .admin_routes import require_admin
from .study_suite_routes import connect as study_connect, correct
from .quality_routes import load, assessment

router=APIRouter(prefix='/api/final-features',tags=['final-features'])
DB = Path(os.environ["MATHWEB_DATA_DIR"]) / "final_features.sqlite3" if os.environ.get("MATHWEB_DATA_DIR") else Path(__file__).resolve().parents[2] / "database" / "final_features.sqlite3"
def now(): return datetime.now(timezone.utc).isoformat()
_init_lock = threading.Lock()
_initialized_databases = set()

def conn():
 DB.parent.mkdir(parents=True, exist_ok=True)
 c = sqlite3.connect(DB, timeout=15)
 c.row_factory = sqlite3.Row
 c.execute('PRAGMA busy_timeout=15000')
 try:
  stat = DB.stat()
  key = (str(DB.resolve()), stat.st_dev, stat.st_ino)
  if key not in _initialized_databases or stat.st_size == 0:
   with _init_lock:
    if key not in _initialized_databases or stat.st_size == 0:
     c.execute('PRAGMA journal_mode=WAL')
     c.executescript("""CREATE TABLE IF NOT EXISTS teacher_lessons(id INTEGER PRIMARY KEY,title TEXT NOT NULL,topic TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'draft',created_by INTEGER NOT NULL,created_at TEXT NOT NULL,reviewed_at TEXT);
     CREATE TABLE IF NOT EXISTS teacher_assignments(id INTEGER PRIMARY KEY,title TEXT NOT NULL,topic TEXT NOT NULL,due_at TEXT,created_by INTEGER NOT NULL,created_at TEXT NOT NULL);
     CREATE TABLE IF NOT EXISTS teacher_targets(assignment_id INTEGER NOT NULL,user_id INTEGER NOT NULL,PRIMARY KEY(assignment_id,user_id));
     CREATE TABLE IF NOT EXISTS teacher_feedback(id INTEGER PRIMARY KEY,assignment_id INTEGER NOT NULL,user_id INTEGER NOT NULL,body TEXT NOT NULL,created_at TEXT NOT NULL);
     CREATE TABLE IF NOT EXISTS qa_runs(id INTEGER PRIMARY KEY,created_at TEXT NOT NULL,report TEXT NOT NULL);
     CREATE INDEX IF NOT EXISTS idx_teacher_targets_user ON teacher_targets(user_id,assignment_id);
     CREATE INDEX IF NOT EXISTS idx_teacher_feedback_user ON teacher_feedback(user_id,id DESC);
     CREATE INDEX IF NOT EXISTS idx_teacher_lessons_status ON teacher_lessons(status,id DESC);""")
     c.execute("PRAGMA user_version=402")
     c.commit()
     _initialized_databases.add(key)
  return c
 except Exception:
  c.close()
  raise

def admin(auth):return require_admin(auth)
def learner(auth):return int(get_current_user(auth)['id'])
class Lesson(BaseModel):
 title:str=Field(min_length=3,max_length=160)
 topic:str=Field(min_length=1,max_length=120)
 body:str=Field(min_length=30,max_length=30000)
class Assignment(BaseModel):
 title:str=Field(min_length=3,max_length=160)
 topic:str=Field(min_length=1,max_length=120)
 due_at:str|None=None
 user_ids:list[int]=Field(min_length=1,max_length=200)
class Feedback(BaseModel):
 user_id:int
 body:str=Field(min_length=1,max_length=2000)
@router.post('/admin/lessons')
def create_lesson(req:Lesson,authorization:str|None=Header(default=None)):
 a=admin(authorization)
 with conn() as c:
  cur=c.execute('INSERT INTO teacher_lessons(title,topic,body,created_by,created_at) VALUES(?,?,?,?,?)',(req.title,req.topic,req.body,a['id'],now()))
  return {'id':cur.lastrowid,'status':'draft','note':'Nội dung phải qua kiểm duyệt trước khi công khai'}
@router.get('/admin/lessons')
def list_lessons(authorization:str|None=Header(default=None)):
 admin(authorization)
 with conn() as c:return {'lessons':[dict(r) for r in c.execute('SELECT * FROM teacher_lessons ORDER BY id DESC LIMIT 200')]}
@router.post('/admin/lessons/{lesson_id}/approve')
def approve(lesson_id:int,authorization:str|None=Header(default=None)):
 admin(authorization)
 with conn() as c:
  r=c.execute('SELECT * FROM teacher_lessons WHERE id=?',(lesson_id,)).fetchone()
  if not r:raise HTTPException(404,'Không tìm thấy bài học')
  if len(r['body'].strip())<30:raise HTTPException(422,'Nội dung quá ngắn')
  c.execute("UPDATE teacher_lessons SET status='approved',reviewed_at=? WHERE id=?",(now(),lesson_id))
 return {'approved':True,'note':'Phê duyệt thủ công; chưa có chứng minh tự động tính đúng toán học'}
@router.get('/lessons')
def published():
 with conn() as c:return {'lessons':[dict(r) for r in c.execute("SELECT id,title,topic,body FROM teacher_lessons WHERE status='approved' ORDER BY id DESC LIMIT 200")]}
@router.post('/admin/assignments')
def create_assignment(req:Assignment,authorization:str|None=Header(default=None)):
 a=admin(authorization)
 if req.due_at:
  try:datetime.fromisoformat(req.due_at.replace('Z','+00:00'))
  except ValueError:raise HTTPException(422,'due_at phải là ISO 8601')
 from database.database import get_connection
 with get_connection() as users:
  valid={r[0] for r in users.execute('SELECT id FROM users WHERE id IN ('+','.join('?' for _ in req.user_ids)+')',req.user_ids)}
 if len(valid)!=len(set(req.user_ids)):raise HTTPException(422,'Có tài khoản không tồn tại')
 with conn() as c:
  cur=c.execute('INSERT INTO teacher_assignments(title,topic,due_at,created_by,created_at) VALUES(?,?,?,?,?)',(req.title,req.topic,req.due_at,a['id'],now()))
  c.executemany('INSERT INTO teacher_targets VALUES(?,?)',[(cur.lastrowid,i) for i in valid]);return {'id':cur.lastrowid,'recipients':len(valid)}
@router.get('/assignments')
def my_assignments(authorization:str|None=Header(default=None)):
 user=learner(authorization)
 with conn() as c:return {'assignments':[dict(r) for r in c.execute('SELECT a.* FROM teacher_assignments a JOIN teacher_targets t ON t.assignment_id=a.id WHERE t.user_id=? ORDER BY a.id DESC',(user,))]}
@router.post('/admin/assignments/{assignment_id}/feedback')
def feedback(assignment_id:int,req:Feedback,authorization:str|None=Header(default=None)):
 admin(authorization)
 with conn() as c:
  if not c.execute('SELECT 1 FROM teacher_targets WHERE assignment_id=? AND user_id=?',(assignment_id,req.user_id)).fetchone():raise HTTPException(404,'Người học không thuộc bài giao')
  c.execute('INSERT INTO teacher_feedback(assignment_id,user_id,body,created_at) VALUES(?,?,?,?)',(assignment_id,req.user_id,req.body,now()))
 return {'saved':True}
@router.get('/feedback')
def my_feedback(authorization:str|None=Header(default=None)):
 user=learner(authorization)
 with conn() as c:return {'feedback':[dict(r) for r in c.execute('SELECT assignment_id,body,created_at FROM teacher_feedback WHERE user_id=? ORDER BY id DESC',(user,))]}
@router.get('/achievements')
def achievements(authorization:str|None=Header(default=None)):
 user=learner(authorization)
 with study_connect() as c:
  exams=c.execute('SELECT score,question_ids,answers FROM exams WHERE user_id=? AND submitted IS NOT NULL',(user,)).fetchall()
  reviews=c.execute('SELECT interval_days,last_correct FROM reviews WHERE user_id=?',(user,)).fetchall()
  solved=sum(len(json.loads(e['question_ids'])) for e in exams)
  badges=[]
  if exams:badges.append({'id':'first_exam','title':'Bài thi đầu tiên'})
  if len(exams)>=5:badges.append({'id':'five_exams','title':'Kiên trì luyện tập'})
  if any(e['score']>=9 for e in exams):badges.append({'id':'high_score','title':'Kết quả xuất sắc'})
  if sum(r['interval_days']>=7 and r['last_correct'] for r in reviews)>=5:badges.append({'id':'retention','title':'Ôn tập bền vững'})
  return {'completed_exams':len(exams),'questions_attempted':solved,'review_items':len(reviews),'badges':badges,'xp_awarded_by_this_module':0,'note':'Huy hiệu được tính từ dữ liệu thật, không tự cộng XP hoặc thay thế chỉ số thành thạo'}
@router.get('/quality/report')
def qa_report(authorization:str|None=Header(default=None)):
 admin(authorization)
 topics,lessons=load();issues=[];ids=set()
 for t in topics:
  tid=t.get('id')
  if tid in ids:issues.append({'type':'duplicate_topic','topic':tid})
  ids.add(tid)
  result=assessment(t,lessons.get(tid,{}) if isinstance(lessons,dict) else {})
  if result['missing_sections']:issues.append({'type':'missing_lesson_sections','topic':tid,'sections':result['missing_sections']})
 with study_connect() as c:
  questions=c.execute('SELECT * FROM questions').fetchall()
  seen=set()
  for q in questions:
   fingerprint=hashlib.sha256((q['topic']+'|'+q['prompt'].strip().casefold()).encode()).hexdigest()
   if fingerprint in seen:issues.append({'type':'duplicate_question','question_id':q['id']})
   seen.add(fingerprint)
   if not q['prompt'].strip() or not q['solution'].strip():issues.append({'type':'incomplete_question','question_id':q['id']})
   if q['verified'] and not str(q['answer']).strip():issues.append({'type':'missing_answer','question_id':q['id']})
 report={'checked_at':now(),'topics_checked':len(topics),'questions_checked':len(questions),'issues':issues,'passed':not issues,'limitations':'Chưa chứng minh được đáp án và lời giải bằng toán học, chưa kiểm thử toàn bộ frontend và đồ thị kiến thức.'}
 with conn() as c:c.execute('INSERT INTO qa_runs(created_at,report) VALUES(?,?)',(report['checked_at'],json.dumps(report,ensure_ascii=False)))
 return report
