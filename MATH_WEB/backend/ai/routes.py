from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, model_validator

from .config import DIFFICULTIES, MAX_COUNT, MAX_TOPICS, QUESTION_TYPES
from .engine.battle import battle_manager
from .engine.difficulty import normalize
from .engine.service import AIQuestionService


router = APIRouter(prefix="/api/ai", tags=["AI Question Engine"])
service = AIQuestionService()


class QuestionRequest(BaseModel):
    grade: int = Field(ge=10, le=12)
    topics: list[str] | None = Field(default=None, max_length=MAX_TOPICS)
    topic: str | None = None
    count: int = Field(default=10, ge=1, le=MAX_COUNT)
    difficulty: str = "medium"
    question_type: str = "multiple_choice"
    history: list[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def fill_topics(self):
        if not self.topics and self.topic:
            self.topics = [self.topic]
        if not self.topics:
            raise ValueError("topics is required")
        return self


class AnswerRequest(BaseModel):
    answer: object


class BattleTopicsRequest(BaseModel):
    player_topics: list[str] = Field(default_factory=list, max_length=MAX_TOPICS)
    opponent_topics: list[str] = Field(default_factory=list, max_length=MAX_TOPICS)


class BattleCreateRequest(BaseModel):
    player1: str = Field(min_length=1, max_length=100)
    player2: str = Field(min_length=1, max_length=100)
    grade: int = Field(ge=10, le=12)
    player1_topics: list[str] = Field(min_length=1, max_length=MAX_TOPICS)
    player2_topics: list[str] = Field(min_length=1, max_length=MAX_TOPICS)


@router.get("/health")
def health():
    return {"ok": True, "service": "ai-question-engine", "version": "3.0"}


@router.get("/knowledge")
def knowledge(grade: int | None = None):
    if grade is not None and grade not in (10, 11, 12):
        raise HTTPException(400, "grade must be 10, 11 or 12")
    return service.topics(grade)


@router.get("/knowledge/{topic_id}")
def knowledge_detail(topic_id: str):
    item = service.knowledge.get(topic_id)
    if not item:
        raise HTTPException(404, "topic_not_found")
    return item


@router.post("/questions")
def questions(req: QuestionRequest):
    difficulty = normalize(req.difficulty)
    if difficulty not in DIFFICULTIES:
        raise HTTPException(400, "invalid_difficulty")
    if req.question_type not in QUESTION_TYPES:
        raise HTTPException(400, "invalid_question_type")
    try:
        return service.generate_set(
            req.grade,
            req.topics or [],
            req.count,
            difficulty,
            req.question_type,
            req.history,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc))


@router.post("/practice/session")
def practice_session(req: QuestionRequest):
    result = questions(req)
    result["mode"] = "practice"
    return result


@router.post("/questions/{question_id}/answer")
def answer(question_id: str, req: AnswerRequest):
    try:
        return service.answer(question_id, req.answer)
    except KeyError:
        raise HTTPException(404, "question_expired_or_not_found")


@router.post("/battle/topics")
def battle_topics(req: BattleTopicsRequest):
    common = service.battle_topics(req.player_topics, req.opponent_topics)
    return {
        "matched": bool(common),
        "common_topics": common,
        "max_topics": MAX_TOPICS,
    }


@router.post("/battle/create")
def battle_create(req: BattleCreateRequest):
    common = service.battle_topics(req.player1_topics, req.player2_topics)
    if not common:
        raise HTTPException(409, "no_common_topics")
    room = battle_manager.create(req.player1, req.player2, common, req.grade)
    return {
        "battle_id": room["id"],
        "topics": common,
        "grade": req.grade,
        "status": room["status"],
    }


@router.websocket("/battle/ws/{battle_id}/{user_id}")
async def battle_ws(websocket: WebSocket, battle_id: str, user_id: str):
    room = battle_manager.get(battle_id)
    if not room or user_id not in room["players"]:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    battle_manager.attach(battle_id, user_id, websocket)
    await battle_manager.broadcast(
        battle_id,
        {"type": "player_joined", "user_id": user_id, "status": room["status"]},
    )

    try:
        while True:
            payload = await websocket.receive_json()
            await battle_manager.broadcast(
                battle_id,
                {"type": "battle_event", "from": user_id, "data": payload},
            )
    except WebSocketDisconnect:
        room["players"][user_id] = None
        await battle_manager.broadcast(
            battle_id,
            {"type": "player_left", "user_id": user_id},
        )
