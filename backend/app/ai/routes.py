from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Header
from pydantic import BaseModel, Field
from .config import MAX_COUNT, MAX_TOPICS
from .engine.service import AIQuestionService
from .engine.battle import battle_manager
from .engine.super_bank import SUPER_BANK_STATS
from .archive import archive_questions
from database.database import get_connection
from ..auth.routes import get_current_user

router=APIRouter(prefix="/api/ai",tags=["AI Question Engine"])
service=AIQuestionService()

TIER_DIFFICULTY = {
    "foundation": "easy", "so_cap": "easy", "sơ cấp": "easy",
    "provincial": "expert", "mo_rong": "expert", "mở rộng": "expert",
    "national": "hell", "quoc_gia": "hell", "chuyên sâu": "hell",
}

def effective_difficulty(req: "QuestionRequest") -> str:
    tier = (req.learning_tier or "").strip().lower()
    return TIER_DIFFICULTY.get(tier, req.difficulty)


def apply_learner_personalization(req: "QuestionRequest", authorization: str | None) -> None:
    """Apply saved per-learner difficulty and workload preferences to practice requests."""
    if not authorization or req.learning_tier:
        return
    try:
        user = get_current_user(authorization)
        conn = get_connection()
        try:
            row = conn.execute("SELECT preferred_difficulty,difficulty_adjustment,question_count_scale FROM learner_personalization WHERE user_id=?", (user["id"],)).fetchone()
        finally:
            conn.close()
        if not row:
            return
        aliases = {"nền tảng":"easy", "trung cấp":"medium", "nâng cao":"hard", "foundation":"easy", "expert":"expert"}
        preferred = str(row["preferred_difficulty"] or "auto")
        if preferred != "auto":
            req.difficulty = aliases.get(preferred.casefold(), preferred)
        else:
            order = ["easy", "medium", "hard", "expert", "hell"]
            current = str(req.difficulty or "medium").casefold()
            if current in order:
                req.difficulty = order[max(0, min(len(order)-1, order.index(current)+int(row["difficulty_adjustment"] or 0)))]
        req.count = max(1, min(MAX_COUNT, round(req.count * float(row["question_count_scale"] or 1.0))))
    except Exception:
        # Personalization is an enhancement, not a reason to break practice for a valid user.
        return


def annotate_tier(result: dict, req: "QuestionRequest") -> dict:
    tier = (req.learning_tier or "foundation").strip().lower()
    labels = {
        "foundation": "Sơ cấp · Toàn bộ kiến thức chương trình THPT",
        "so_cap": "Sơ cấp · Toàn bộ kiến thức chương trình THPT",
        "sơ cấp": "Sơ cấp · Toàn bộ kiến thức chương trình THPT",
        "provincial": "Mở rộng · Ôn luyện học sinh giỏi cấp tỉnh",
        "mo_rong": "Mở rộng · Ôn luyện học sinh giỏi cấp tỉnh",
        "mở rộng": "Mở rộng · Ôn luyện học sinh giỏi cấp tỉnh",
        "national": "Chuyên sâu · Ôn luyện học sinh giỏi cấp quốc gia",
        "quoc_gia": "Chuyên sâu · Ôn luyện học sinh giỏi cấp quốc gia",
        "chuyên sâu": "Chuyên sâu · Ôn luyện học sinh giỏi cấp quốc gia",
    }
    result["learning_tier"] = tier
    result["tier_label"] = labels.get(tier, "Theo độ khó đã chọn")
    for q in result.get("questions", []):
        if isinstance(q, dict):
            q["learning_tier"] = tier
            q["tier_label"] = result["tier_label"]
    for problem in result.get("problems", []):
        if isinstance(problem, dict):
            problem["learning_tier"] = tier
            problem["tier_label"] = result["tier_label"]
            for q in problem.get("parts", []):
                if isinstance(q, dict):
                    q["learning_tier"] = tier
                    q["tier_label"] = result["tier_label"]
    return result

class QuestionRequest(BaseModel):
    grade:int=Field(ge=10,le=12)
    topics:list[str]=Field(min_length=1,max_length=MAX_TOPICS)
    count:int=Field(default=10,ge=1,le=MAX_COUNT)
    difficulty:str="medium"
    learning_tier:str|None=None
    question_type:str="mixed"
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
def questions(req:QuestionRequest, authorization: str | None = Header(default=None)):
    apply_learner_personalization(req, authorization)
    try:
        if req.problem_mode:
            result=service.generate_problem_set(req.grade,req.topics,req.count,effective_difficulty(req),req.problem_parts,req.history,req.game_id)
        else:
            result=service.generate_set(req.grade,req.topics,req.count,effective_difficulty(req),req.question_type,req.history,req.game_id)
        try: archive_questions(req.grade, req.topics, result.get("questions", []), game_id=req.game_id or "", source="AI runtime · /questions")
        except Exception: pass  # Archiving must never take down a practice request.
        return annotate_tier(result, req)
    except (ValueError,RuntimeError) as e: raise HTTPException(400,str(e))

@router.post("/problems")
def problems(req:QuestionRequest, authorization: str | None = Header(default=None)):
    apply_learner_personalization(req, authorization)
    try:
        result=service.generate_problem_set(req.grade,req.topics,req.count,effective_difficulty(req),req.problem_parts,req.history,req.game_id)
        try: archive_questions(req.grade, req.topics, result.get("questions", []), game_id=req.game_id or "", source="AI runtime · /problems")
        except Exception: pass
        return annotate_tier(result, req)
    except (ValueError,RuntimeError) as e: raise HTTPException(400,str(e))

@router.post("/practice/session")
def practice_session(req:QuestionRequest, authorization: str | None = Header(default=None)):
    apply_learner_personalization(req, authorization)
    try:
        if req.problem_mode:
            result=service.generate_problem_set(req.grade,req.topics,req.count,effective_difficulty(req),req.problem_parts,req.history,req.game_id)
        else:
            result=service.generate_set(req.grade,req.topics,req.count,effective_difficulty(req),req.question_type,req.history,req.game_id)
        result["mode"]="practice"
        try: archive_questions(req.grade, req.topics, result.get("questions", []), game_id=req.game_id or "", source="AI runtime · practice session")
        except Exception: pass
        return annotate_tier(result, req)
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
def battle_create(req:BattleCreateRequest, authorization: str | None = Header(default=None)):
    # Legacy AI rooms also require a real logged-in participant. The primary
    # Battle flow uses /api/matchmaking, but this route must not allow an
    # anonymous request to create unlimited rooms for arbitrary user IDs.
    current = get_current_user(authorization)
    with get_connection() as conn:
        def resolve(value: str):
            value = str(value).strip()
            row = conn.execute(
                "SELECT id FROM users WHERE CAST(id AS TEXT)=? OR player_id=? COLLATE NOCASE OR username=? COLLATE NOCASE LIMIT 1",
                (value, value, value),
            ).fetchone()
            return str(row["id"]) if row else None
        player1, player2 = resolve(req.player1), resolve(req.player2)
    if not player1 or not player2 or player1 == player2:
        raise HTTPException(422, "Battle yêu cầu hai người chơi hợp lệ, khác nhau.")
    if str(current["id"]) not in (player1, player2):
        raise HTTPException(403, "Bạn không thuộc phòng Battle này.")
    common=service.battle_topics(req.player1_topics,req.player2_topics)
    if not common: raise HTTPException(409,"no_common_topics")
    room=battle_manager.create(player1,player2,common,req.grade)
    return {"battle_id":room["id"],"topics":common,"grade":req.grade,"status":room["status"]}

# The primary battle UI uses the SQLite matchmaking system, not the older
# in-memory AI demonstration rooms. Keep both routes compatible, but enforce
# the login token AND match membership before allowing WebSocket traffic.
_active_match_sockets: dict[str, dict[int, WebSocket]] = {}


def _socket_match_details(battle_id: str, user_id: int):
    if battle_id.isdecimal() and len(battle_id) <= 10:
        conn = get_connection()
        try:
            match = conn.execute(
                "SELECT player1_id, player2_id, status FROM matches WHERE id=?",
                (int(battle_id),),
            ).fetchone()
            if match and user_id in (int(match["player1_id"]), int(match["player2_id"])):
                return {"kind": "matchmaking", "status": match["status"]}
        except Exception:
            pass
        finally:
            conn.close()
    room = battle_manager.get(battle_id)
    if room and str(user_id) in room["players"]:
        return {"kind": "legacy", "status": room["status"]}
    return None


@router.websocket("/battle/ws/{battle_id}/{user_id}")
async def battle_ws(websocket: WebSocket, battle_id: str, user_id: str):
    from ..auth.routes import get_current_user
    try:
        token = websocket.query_params.get("token", "")
        user = get_current_user(f"Bearer {token}")
        if str(user["id"]) != user_id:
            raise ValueError("WebSocket user does not match token")
        details = _socket_match_details(battle_id, int(user["id"]))
        if not details:
            raise ValueError("WebSocket user is not a participant of this match")
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    uid = int(user["id"])
    participants = _active_match_sockets.setdefault(battle_id, {})
    participants[uid] = websocket
    if details["kind"] == "legacy":
        battle_manager.attach(battle_id, user_id, websocket)

    async def send_authoritative_state():
        state = _socket_match_details(battle_id, uid)
        if not state:
            await websocket.close(code=1008)
            return
        packet = {"type": "state", "status": state["status"]}
        if state["kind"] == "matchmaking":
            # This is only a projection of the already stored, server-scored
            # answers. Never trust client-submitted progress/winner values.
            from ..matchmaking.routes import get_match_progress
            progress = get_match_progress(int(battle_id), f"Bearer {token}")
            other = progress["opponent"]
            packet["progress"] = {
                "correct": other["correct"], "wrong": other["wrong"],
                "blank": other["blank"], "answered": other["current"],
                "total": progress["total"],
                "finished": progress["status"] == "FINISHED",
                "time": other.get("time", 0),
            }
        await websocket.send_json(packet)

    try:
        await send_authoritative_state()
        for other_id, other_ws in list(participants.items()):
            if other_id != uid:
                try:
                    await other_ws.send_json({"type": "player_joined", "user_id": user_id})
                except Exception:
                    pass
        while True:
            incoming = await websocket.receive_json()
            if not isinstance(incoming, dict):
                continue
            event = str(incoming.get("type", "")).lower()
            if event not in {"sync", "progress", "finished"}:
                continue
            await send_authoritative_state()
            if event in {"progress", "finished"}:
                # Inform other clients to re-sync; no client-provided answers,
                # winner or scores are rebroadcast.
                for other_id, other_ws in list(participants.items()):
                    if other_id != uid:
                        try:
                            await other_ws.send_json({"type": "sync"})
                        except Exception:
                            pass
    except WebSocketDisconnect:
        pass
    except Exception:
        # A broken socket must not terminate other players' sessions.
        pass
    finally:
        if participants.get(uid) is websocket:
            participants.pop(uid, None)
            for other_ws in list(participants.values()):
                try:
                    await other_ws.send_json({"type": "player_left", "user_id": user_id})
                except Exception:
                    pass
        if not participants:
            _active_match_sockets.pop(battle_id, None)
        room = battle_manager.get(battle_id)
        if room and room["players"].get(user_id) is websocket:
            room["players"][user_id] = None

