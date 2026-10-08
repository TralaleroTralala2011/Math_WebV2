from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..auth.routes import get_current_user

from .engine import (
    create_question,
    TOPICS,
    DIFFICULTIES
)

from .session import (
    create_question_session,
    get_question_session,
    decode_question_session,
    check_answer,
    get_public_session,
    expire_question_session,
    is_session_expired
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/questions",
    tags=["Questions"]
)


# =========================================================
# CONSTANTS
# =========================================================

MAX_GAME_ID_LENGTH = 100
MAX_SESSION_ID_LENGTH = 100
MAX_ANSWER_LENGTH = 500


# =========================================================
# REQUEST MODEL
# =========================================================

class AnswerRequest(BaseModel):

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_SESSION_ID_LENGTH
    )

    answer: str = Field(
        ...,
        min_length=1,
        max_length=MAX_ANSWER_LENGTH
    )


# =========================================================
# COMMON HELPERS
# =========================================================

def get_user_from_token(
    authorization: str | None
):
    """
    Lấy user hiện tại từ Authorization header.
    """

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    try:

        user = get_current_user(
            authorization
        )

    except HTTPException:

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Không thể xác định tài khoản."
        )

    if "id" not in user:

        raise HTTPException(
            status_code=401,
            detail="Thông tin tài khoản không hợp lệ."
        )

    return user


def normalize_topic(
    topic: str
) -> str:

    if not isinstance(topic, str):

        raise HTTPException(
            status_code=400,
            detail="Chủ đề không hợp lệ."
        )

    topic = topic.strip().lower()

    if not topic:

        raise HTTPException(
            status_code=400,
            detail="Chủ đề không được để trống."
        )

    return topic


def normalize_difficulty(
    difficulty: str
) -> str:

    if not isinstance(difficulty, str):

        raise HTTPException(
            status_code=400,
            detail="Độ khó không hợp lệ."
        )

    difficulty = difficulty.strip().lower()

    if not difficulty:

        raise HTTPException(
            status_code=400,
            detail="Độ khó không được để trống."
        )

    return difficulty


def validate_topic(
    topic: str
):

    if topic not in TOPICS:

        raise HTTPException(
            status_code=400,
            detail="Chủ đề không hợp lệ."
        )


def validate_difficulty(
    difficulty: str
):

    if difficulty not in DIFFICULTIES:

        raise HTTPException(
            status_code=400,
            detail="Độ khó không hợp lệ."
        )


def validate_game_id(
    game_id: str | None
):

    if game_id is None:

        return None

    game_id = game_id.strip()

    if not game_id:

        raise HTTPException(
            status_code=400,
            detail="Game ID không được để trống."
        )

    if len(game_id) > MAX_GAME_ID_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Game ID quá dài."
        )

    return game_id


def validate_session_id(
    session_id: str
) -> str:

    if not isinstance(session_id, str):

        raise HTTPException(
            status_code=400,
            detail="Session ID không hợp lệ."
        )

    session_id = session_id.strip()

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="Session ID không được để trống."
        )

    if len(session_id) > MAX_SESSION_ID_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Session ID không hợp lệ."
        )

    return session_id


def validate_answer(
    answer: str
) -> str:

    if not isinstance(answer, str):

        raise HTTPException(
            status_code=400,
            detail="Câu trả lời không hợp lệ."
        )

    answer = answer.strip()

    if not answer:

        raise HTTPException(
            status_code=400,
            detail="Câu trả lời không được để trống."
        )

    if len(answer) > MAX_ANSWER_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Câu trả lời quá dài."
        )

    return answer


def build_answered_result(
    row,
    session
):

    private_answer = session.get(
        "private_answer",
        {}
    )

    correct_answer = private_answer.get(
        "answer_text"
    )

    return {
        "status": "answered",

        "result": {
            "correct": bool(
                row["is_correct"]
            ),

            "selected_answer": row[
                "selected_answer"
            ],

            "correct_answer": correct_answer,

            "explanation": session.get(
                "explanation"
            ),

            "answered_at": session.get(
                "answered_at"
            )
        }
    }


# =========================================================
# GENERATE QUESTION
# =========================================================

@router.get("/generate")
def generate_question(
    topic: str,
    difficulty: str,
    game_id: str | None = None,
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    user = get_user_from_token(
        authorization
    )

    # =====================================================
    # NORMALIZE
    # =====================================================

    topic = normalize_topic(
        topic
    )

    difficulty = normalize_difficulty(
        difficulty
    )

    game_id = validate_game_id(
        game_id
    )

    # =====================================================
    # VALIDATE TOPIC
    # =====================================================

    validate_topic(
        topic
    )

    # =====================================================
    # VALIDATE DIFFICULTY
    # =====================================================

    validate_difficulty(
        difficulty
    )

    # =====================================================
    # GENERATE QUESTION
    # =====================================================

    try:

        question = create_question(
            topic=topic,
            difficulty=difficulty
        )

    except ValueError as error:

        print(
            "QUESTION GENERATION VALIDATION ERROR:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail="Không thể tạo câu hỏi với dữ liệu yêu cầu."
        )

    except Exception as error:

        print(
            "QUESTION GENERATION ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể tạo câu hỏi."
        )

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if not isinstance(question, dict):

        print(
            "QUESTION GENERATION ERROR: "
            "Generator did not return a dictionary."
        )

        raise HTTPException(
            status_code=500,
            detail="Dữ liệu câu hỏi không hợp lệ."
        )

    required_fields = [
        "question_id",
        "topic",
        "difficulty",
        "concept",
        "question",
        "choices",
        "answer",
        "answer_text",
        "explanation"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in question
    ]

    if missing_fields:

        print(
            "QUESTION GENERATION ERROR: "
            "Missing fields:",
            missing_fields
        )

        raise HTTPException(
            status_code=500,
            detail="Câu hỏi được tạo không đầy đủ dữ liệu."
        )

    # =====================================================
    # CREATE QUESTION SESSION
    # =====================================================

    try:

        session = create_question_session(
            user_id=user["id"],
            question=question,
            game_id=game_id
        )

    except ValueError as error:

        print(
            "QUESTION SESSION VALIDATION ERROR:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail="Không thể tạo phiên câu hỏi."
        )

    except Exception as error:

        print(
            "QUESTION SESSION ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể tạo phiên câu hỏi."
        )

    # =====================================================
    # RETURN PUBLIC SESSION
    # =====================================================

    return session


# =========================================================
# ANSWER QUESTION
# =========================================================

@router.post("/answer")
def answer_question(
    data: AnswerRequest,
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    user = get_user_from_token(
        authorization
    )

    # =====================================================
    # VALIDATE REQUEST
    # =====================================================

    session_id = validate_session_id(
        data.session_id
    )

    selected_answer = validate_answer(
        data.answer
    )

    # =====================================================
    # GET SESSION
    # =====================================================

    row = get_question_session(
        session_id=session_id,
        user_id=user["id"]
    )

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên câu hỏi."
        )

    # =====================================================
    # DECODE SESSION
    # =====================================================

    session = decode_question_session(
        row
    )

    if session is None:

        raise HTTPException(
            status_code=500,
            detail="Dữ liệu phiên câu hỏi không hợp lệ."
        )

    # =====================================================
    # PRE-CHECK STATUS
    # =====================================================

    status = session.get(
        "status"
    )

    if status == "answered":

        return build_answered_result(
            row,
            session
        )

    if status == "expired":

        raise HTTPException(
            status_code=410,
            detail="Phiên câu hỏi đã hết thời gian."
        )

    if status != "active":

        raise HTTPException(
            status_code=409,
            detail="Phiên câu hỏi không còn hoạt động."
        )

    # =====================================================
    # CHECK EXPIRATION
    # =====================================================

    expires_at = session.get(
        "expires_at"
    )

    try:

        if expires_at and is_session_expired(
            expires_at
        ):

            expire_question_session(
                session_id=session_id,
                user_id=user["id"]
            )

            raise HTTPException(
                status_code=410,
                detail="Phiên câu hỏi đã hết thời gian."
            )

    except HTTPException:

        raise

    except Exception as error:

        print(
            "QUESTION EXPIRATION CHECK ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể kiểm tra thời gian câu hỏi."
        )

    # =====================================================
    # CHECK ANSWER
    # =====================================================

    try:

        result = check_answer(
            session=session,
            selected_answer=selected_answer
        )

    except ValueError as error:

        message = str(
            error
        )

        lower_message = message.lower()

        # -------------------------------------------------
        # ALREADY ANSWERED
        # -------------------------------------------------

        if (
            "đã được trả lời"
            in lower_message
        ):

            raise HTTPException(
                status_code=409,
                detail=message
            )

        # -------------------------------------------------
        # EXPIRED
        # -------------------------------------------------

        if (
            "hết thời gian"
            in lower_message
            or "hết hạn"
            in lower_message
        ):

            raise HTTPException(
                status_code=410,
                detail=message
            )

        # -------------------------------------------------
        # INVALID ANSWER
        # -------------------------------------------------

        raise HTTPException(
            status_code=400,
            detail=message
        )

    except HTTPException:

        raise

    except Exception as error:

        print(
            "QUESTION ANSWER ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể chấm câu trả lời."
        )

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return result


# =========================================================
# GET QUESTION SESSION
# =========================================================

@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    user = get_user_from_token(
        authorization
    )

    # =====================================================
    # VALIDATE SESSION ID
    # =====================================================

    session_id = validate_session_id(
        session_id
    )

    # =====================================================
    # GET SESSION
    # =====================================================

    row = get_question_session(
        session_id=session_id,
        user_id=user["id"]
    )

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiên câu hỏi."
        )

    # =====================================================
    # DECODE
    # =====================================================

    session = decode_question_session(
        row
    )

    if session is None:

        raise HTTPException(
            status_code=500,
            detail="Dữ liệu phiên câu hỏi không hợp lệ."
        )

    status = session.get(
        "status"
    )

    # =====================================================
    # ALREADY ANSWERED
    # =====================================================

    if status == "answered":

        return build_answered_result(
            row,
            session
        )

    # =====================================================
    # ALREADY EXPIRED
    # =====================================================

    if status == "expired":

        raise HTTPException(
            status_code=410,
            detail="Phiên câu hỏi đã hết thời gian."
        )

    # =====================================================
    # ACTIVE SESSION
    # =====================================================

    if status == "active":

        expires_at = session.get(
            "expires_at"
        )

        try:

            if expires_at and is_session_expired(
                expires_at
            ):

                expire_question_session(
                    session_id=session_id,
                    user_id=user["id"]
                )

                raise HTTPException(
                    status_code=410,
                    detail="Phiên câu hỏi đã hết thời gian."
                )

        except HTTPException:

            raise

        except Exception as error:

            print(
                "QUESTION SESSION EXPIRATION ERROR:",
                error
            )

            raise HTTPException(
                status_code=500,
                detail="Không thể kiểm tra phiên câu hỏi."
            )

        # -------------------------------------------------
        # RETURN PUBLIC DATA ONLY
        # -------------------------------------------------

        return get_public_session(
            session
        )

    # =====================================================
    # UNKNOWN STATUS
    # =====================================================

    raise HTTPException(
        status_code=409,
        detail="Trạng thái phiên câu hỏi không hợp lệ."
    )


# =========================================================
# TOPICS
# =========================================================

@router.get("/topics")
def get_topics():

    return {
        "topics": [
            {
                "id": key,
                "name": value
            }
            for key, value in TOPICS.items()
        ]
    }


# =========================================================
# DIFFICULTIES
# =========================================================

@router.get("/difficulties")
def get_difficulties():

    return {
        "difficulties": [
            {
                "id": key,
                "name": value
            }
            for key, value in DIFFICULTIES.items()
        ]
    }