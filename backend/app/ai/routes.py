from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from .config import MAX_COUNT, MAX_TOPICS
from .engine.service import AIQuestionService
from .engine.battle import battle_manager
from .engine.super_bank import SUPER_BANK_STATS

router=APIRouter(prefix="/api/ai",tags=["AI Question Engine"])
service=AIQuestionService()

class QuestionRequest(BaseModel):
    grade:int=Field(ge=10,le=12)
    topics:list[str]=Field(min_length=1,max_length=MAX_TOPICS)
    count:int=Field(default=10,ge=1,le=MAX_COUNT)
    difficulty:str="medium"
    question_type:str="multiple_choice"
    history:list[dict]=Field(default_factory=list)
    game_id:str|None=None
    problem_mode:bool=False
    problem_parts:int=Field(default=4,ge=2,le=6)

class AnswerRequest(BaseModel):
    answer: object

class BattleTopicsRequest(BaseModel):
    player_topics:list[str]=Field(max_length=MAX_TOPICS)
    opponent_topics:list[str]=Field(max_length=MAX_TOPICS)

class BattleCreateRequest(BaseModel):
    player1:str
    player2:str
    grade:int=Field(ge=10,le=12)
    player1_topics:list[str]=Field(min_length=1,max_length=MAX_TOPICS)
    player2_topics:list[str]=Field(min_length=1,max_length=MAX_TOPICS)

@router.get("/health")
def health(): return {"ok":True,"service":"ai-question-engine","version":"6.0-super-bank-plus-problem-generator"}

@router.get("/bank/stats")
def bank_stats():
    return {"legacy": "preserved", "super_bank": SUPER_BANK_STATS, "problem_archetypes": "20+ reusable structures"}

@router.get("/knowledge")
def knowledge(grade:int|None=None): return service.topics(grade)

@router.get("/knowledge/{topic_id}")
def knowledge_detail(topic_id:str):
    item=service.knowledge.get(topic_id)
    if not item: raise HTTPException(404,"topic_not_found")
    return item

@router.post("/questions")
def questions(req:QuestionRequest):
    try:
        if req.problem_mode:
            return service.generate_problem_set(req.grade,req.topics,req.count,req.difficulty,req.problem_parts,req.history,req.game_id)
        return service.generate_set(req.grade,req.topics,req.count,req.difficulty,req.question_type,req.history,req.game_id)
    except (ValueError,RuntimeError) as e: raise HTTPException(400,str(e))

@router.post("/problems")
def problems(req:QuestionRequest):
    try: return service.generate_problem_set(req.grade,req.topics,req.count,req.difficulty,req.problem_parts,req.history,req.game_id)
    except (ValueError,RuntimeError) as e: raise HTTPException(400,str(e))

@router.post("/practice/session")
def practice_session(req:QuestionRequest):
    try:
        if req.problem_mode:
            result=service.generate_problem_set(req.grade,req.topics,req.count,req.difficulty,req.problem_parts,req.history,req.game_id)
        else:
            result=service.generate_set(req.grade,req.topics,req.count,req.difficulty,req.question_type,req.history,req.game_id)
        result["mode"]="practice"
        return result
    except (ValueError,RuntimeError) as e: raise HTTPException(400,str(e))

@router.post("/questions/{question_id}/answer")
def answer(question_id:str,req:AnswerRequest):
    try: return service.answer(question_id,req.answer)
    except KeyError: raise HTTPException(404,"question_expired_or_not_found")

@router.post("/battle/topics")
def battle_topics(req:BattleTopicsRequest):
    common=service.battle_topics(req.player_topics,req.opponent_topics)
    return {"matched":bool(common),"common_topics":common,"max_topics":MAX_TOPICS}

@router.post("/battle/create")
def battle_create(req:BattleCreateRequest):
    common=service.battle_topics(req.player1_topics,req.player2_topics)
    if not common: raise HTTPException(409,"no_common_topics")
    room=battle_manager.create(req.player1,req.player2,common,req.grade)
    return {"battle_id":room["id"],"topics":common,"grade":req.grade,"status":room["status"]}

@router.websocket("/battle/ws/{battle_id}/{user_id}")
async def battle_ws(websocket:WebSocket,battle_id:str,user_id:str):
    room=battle_manager.get(battle_id)
    if not room or user_id not in room["players"]:
        await websocket.close(code=1008); return
    await websocket.accept()
    battle_manager.attach(battle_id,user_id,websocket)
    await battle_manager.broadcast(battle_id,{"type":"player_joined","user_id":user_id,"status":room["status"]})
    try:
        while True:
            msg=await websocket.receive_json()
            # The authoritative question/answer scoring stays on HTTP service.
            await battle_manager.broadcast(battle_id,{"type":"battle_event","from":user_id,"data":msg})
    except WebSocketDisconnect:
        room["players"][user_id]=None
        await battle_manager.broadcast(battle_id,{"type":"player_left","user_id":user_id})
