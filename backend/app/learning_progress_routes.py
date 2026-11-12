import os
"""Authenticated diagnostic mastery and prerequisite-aware recommendations.
Only server-graded diagnostic questions influence verified mastery. No XP awarded.
"""
import json, random, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from .auth.routes import get_current_user
from .quality_routes import EDGES

router = APIRouter(prefix="/api/learning-progress", tags=["learning-progress"])
TOPICS_PATH = Path(__file__).resolve().parents[2] / "learn-assets/topics.json"
DB = Path(os.environ["MATHWEB_DATA_DIR"]) / "learning_progress.sqlite3" if os.environ.get("MATHWEB_DATA_DIR") else Path(__file__).resolve().parents[2] / "database" / "learning_progress.sqlite3"

def topics():
    return json.loads(TOPICS_PATH.read_text(encoding="utf-8"))

def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(DB, timeout=10)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("CREATE TABLE IF NOT EXISTS diagnostics (user_id INTEGER NOT NULL, topic_id TEXT NOT NULL, question_id TEXT NOT NULL, correct INTEGER NOT NULL, difficulty INTEGER NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY(user_id,question_id))")
    return c

# Controlled, mathematically verified diagnostic templates. The coverage is intentionally limited.
DIAGNOSTICS = {
 "ham_so": [("f(x)=2x+3. Tính f(4).",11,1),("f(x)=3x-2. Tính f(-1).",-5,2)],
 "phuong_trinh": [("Giải 2x+3=11. Tìm x.",4,1),("Giải 3x-7=8. Tìm x.",5,2)],
 "phuong_trinh_he": [("Giải x+5=12. Tìm x.",7,1),("Giải 4x-3=9. Tìm x.",3,2)],
 "ham_so_bac_hai": [("y=x²-4x+1. Hoành độ đỉnh là bao nhiêu?",2,2),("y=2x²+8x-1. Hoành độ đỉnh là bao nhiêu?",-2,3)],
 "gioi_han": [("Tính giới hạn x→2 của (x+3).",5,1),("Tính giới hạn x→1 của (x²+2x).",3,2)],
 "dao_ham": [("f(x)=x². Tính f'(3).",6,1),("f(x)=3x²-2x. Tính f'(2).",10,2)],
 "nguyen_ham_tich_phan": [("Tính tích phân từ 0 đến 2 của 2x dx.",4,2),("Tính tích phân từ 0 đến 1 của 3x² dx.",1,3)],
}

class Answer(BaseModel):
    question_id: str = Field(min_length=3,max_length=100)
    answer: float = Field(ge=-1e12,le=1e12)

def current(auth):
    u=get_current_user(auth)
    return int(u['id'])

def catalog(topic_id):
    if topic_id not in {t['id'] for t in topics()}:
        raise HTTPException(404,'Chủ đề không tồn tại')

@router.get('/diagnostic/{topic_id}')
def diagnostic(topic_id: str, authorization: str | None = Header(default=None)):
    current(authorization)
    catalog(topic_id)
    questions=DIAGNOSTICS.get(topic_id)
    if not questions:
        return {'topic_id':topic_id,'supported':False,'questions':[], 'note':'Chưa có bộ câu hỏi chẩn đoán được kiểm chứng cho chủ đề này.'}
    return {'topic_id':topic_id,'supported':True,'questions':[{'id':f'{topic_id}:{i}', 'text':q,'difficulty':d} for i,(q,_,d) in enumerate(questions)]}

@router.post('/answer')
def answer(req: Answer, authorization: str | None = Header(default=None)):
    user=current(authorization)
    try:
        topic_id, index=req.question_id.rsplit(':',1)
        q,expected,difficulty=DIAGNOSTICS[topic_id][int(index)]
        if req.question_id != f'{topic_id}:{int(index)}': raise ValueError()
    except (KeyError, ValueError, IndexError):
        raise HTTPException(422,'Câu hỏi không hợp lệ')
    correct=abs(req.answer-expected)<1e-8
    with conn() as c:
        # One result per question per user prevents repeated submissions from inflating mastery.
        c.execute('INSERT OR IGNORE INTO diagnostics VALUES (?,?,?,?,?,?)',(user,topic_id,req.question_id,int(correct),difficulty,datetime.now(timezone.utc).isoformat()))
        row=c.execute('SELECT correct FROM diagnostics WHERE user_id=? AND question_id=?',(user,req.question_id)).fetchone()
    return {'correct':bool(row[0]),'expected':expected,'recorded':True,'note':'Kết quả đầu tiên được lưu; làm lại không cộng điểm thành thạo.'}

def progress(user):
    with conn() as c:
        rows=c.execute('SELECT topic_id,correct,difficulty FROM diagnostics WHERE user_id=?',(user,)).fetchall()
    by={}
    for t,ok,d in rows:
        z=by.setdefault(t,{'weighted':0,'weight':0,'attempted':0})
        z['weighted']+=ok*d; z['weight']+=d; z['attempted']+=1
    result={}
    for t,v in by.items():
        available=len(DIAGNOSTICS.get(t,[]))
        score=round(100*v['weighted']/v['weight']) if v['weight'] else 0
        status='đang học' if v['attempted']<available else ('thành thạo sơ bộ' if score>=80 else 'cần ôn tập')
        result[t]={'score':score,'attempted':v['attempted'],'available':available,'status':status,'confidence':'limited_diagnostic'}
    return result

@router.get('/overview')
def overview(authorization: str | None = Header(default=None)):
    user=current(authorization); data=progress(user)
    return {'topics':[{'id':t['id'],'title':t['title'],'grade':t['grade'],**data.get(t['id'],{'score':None,'attempted':0,'available':len(DIAGNOSTICS.get(t['id'],[])),'status':'chưa học','confidence':'no_evidence'})} for t in topics()], 'note':'Điểm chỉ dựa trên bộ chẩn đoán nhỏ đã xác minh, không đại diện toàn bộ năng lực.'}

@router.get('/path')
def path(authorization: str | None = Header(default=None)):
    user=current(authorization); data=progress(user); all_topics={t['id']:t for t in topics()}
    suggestions=[]
    for topic, prerequisites in EDGES.items():
        if topic not in all_topics: continue
        missing=[p for p in prerequisites if p in all_topics and (p not in data or data[p]['score']<80 or data[p]['attempted']<len(DIAGNOSTICS.get(p,[])))]
        if missing:
            suggestions.append({'target':topic,'target_title':all_topics[topic]['title'],'prerequisites':[{'id':p,'title':all_topics[p]['title'],'status':data.get(p,{}).get('status','chưa học')} for p in missing], 'reason':'Kiến thức tiên quyết chưa có bằng chứng thành thạo'})
    return {'recommendations':suggestions,'coverage':'partial_curated_prerequisites','note':'Lộ trình gợi ý sơ bộ, không phải đánh giá năng lực đầy đủ.'}
