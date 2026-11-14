import json
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..auth.routes import get_current_user
from ..presence.routes import is_user_online
from ..ai.routes import service as ai_service
from app.ai.archive import archive_questions
from database.database import get_connection


router = APIRouter(
    prefix="/api/matchmaking",
    tags=["Matchmaking"]
)


# =========================================================
# CONFIG
# =========================================================

MATCH_TOTAL_QUESTIONS = 10

MATCH_QUEUE_TIMEOUT_SECONDS = 10 * 60
MATCH_INVITE_TIMEOUT_SECONDS = 120
MATCH_MAX_DURATION_SECONDS = 5 * 60

MAX_PLAYER_ID_LENGTH = 100
MAX_MATCH_ID = 2_147_483_647
MAX_TOPIC_COUNT = 5

DEFAULT_GRADE = 12
DEFAULT_DIFFICULTY = "medium"
DEFAULT_QUESTION_TYPE = "mixed"

VALID_DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
    "expert"
}

VALID_QUESTION_TYPES = {
    "mixed",
    "multiple_choice",
    "short_answer",
    "true_false"
}

VALID_MATCH_STATUSES = {
    "INVITED",
    "STARTING",
    "PLAYING",
    "FINISHED",
    "CANCELLED"
}


# =========================================================
# DATABASE INIT
# =========================================================

def init_matchmaking_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matchmaking_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                grade INTEGER DEFAULT 12,
                topics TEXT DEFAULT '[]',
                difficulty TEXT DEFAULT 'medium',
                question_type TEXT DEFAULT 'multiple_choice'
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_code TEXT NOT NULL UNIQUE,

                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,

                status TEXT NOT NULL,

                questions TEXT NOT NULL,

                topics TEXT DEFAULT '[]',
                grade INTEGER DEFAULT 12,
                difficulty TEXT DEFAULT 'medium',
                question_type TEXT DEFAULT 'multiple_choice',

                player1_answers TEXT DEFAULT '{}',
                player2_answers TEXT DEFAULT '{}',

                player1_current INTEGER DEFAULT 0,
                player2_current INTEGER DEFAULT 0,

                player1_correct INTEGER DEFAULT 0,
                player1_wrong INTEGER DEFAULT 0,
                player1_blank INTEGER DEFAULT 0,
                player1_time INTEGER DEFAULT 0,

                player2_correct INTEGER DEFAULT 0,
                player2_wrong INTEGER DEFAULT 0,
                player2_blank INTEGER DEFAULT 0,
                player2_time INTEGER DEFAULT 0,

                winner_id INTEGER,

                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS match_invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        ensure_columns(
            cursor,
            "matchmaking_queue",
            {
                "grade": "INTEGER DEFAULT 12",
                "topics": "TEXT DEFAULT '[]'",
                "difficulty": "TEXT DEFAULT 'medium'",
                "question_type": "TEXT DEFAULT 'multiple_choice'"
            }
        )

        ensure_columns(
            cursor,
            "matches",
            {
                "topics": "TEXT DEFAULT '[]'",
                "grade": "INTEGER DEFAULT 12",
                "difficulty": "TEXT DEFAULT 'medium'",
                "question_type": "TEXT DEFAULT 'multiple_choice'",
                "player1_answers": "TEXT DEFAULT '{}'",
                "player2_answers": "TEXT DEFAULT '{}'",
                "player1_current": "INTEGER DEFAULT 0",
                "player2_current": "INTEGER DEFAULT 0"
            }
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_queue_created
            ON matchmaking_queue(created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_player1
            ON matches(player1_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_player2
            ON matches(player2_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_status
            ON matches(status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_invites_receiver
            ON match_invites(receiver_id, status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_invites_match
            ON match_invites(match_id)
            """
        )

        connection.commit()

    finally:
        connection.close()


def ensure_columns(cursor, table_name, columns):
    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    existing = {
        row["name"]
        for row in cursor.fetchall()
    }

    for column_name, column_definition in columns.items():
        if column_name in existing:
            continue

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )


init_matchmaking_tables()


# =========================================================
# REQUEST MODELS
# =========================================================

class MatchSettings(BaseModel):
    grade: int = Field(
        default=DEFAULT_GRADE,
        ge=10,
        le=12
    )

    topics: list[str] = Field(
        default_factory=list,
        max_length=MAX_TOPIC_COUNT
    )

    difficulty: str = Field(
        default=DEFAULT_DIFFICULTY
    )

    question_type: str = Field(
        default=DEFAULT_QUESTION_TYPE
    )


class InviteRequest(MatchSettings):
    player_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_PLAYER_ID_LENGTH
    )


class MatchAnswerRequest(BaseModel):
    question_index: int = Field(
        ...,
        ge=0,
        le=1_000_000
    )

    answer: object = None


class MatchSkipRequest(BaseModel):
    question_index: int = Field(
        ...,
        ge=0,
        le=1_000_000
    )


# =========================================================
# HELPERS
# =========================================================

def get_user(authorization):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    return get_current_user(authorization)


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def parse_iso(value):
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except (
        ValueError,
        TypeError
    ):
        return None


def seconds_since(value):
    parsed = parse_iso(value)

    if parsed is None:
        return None

    delta = (
        datetime.now(timezone.utc)
        - parsed
    ).total_seconds()

    # Millisecond resolution matters for the Battle speed tiebreaker.
    return max(0.0, round(delta, 3))


def safe_json_loads(value, default=None):
    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value)

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError
    ):
        return default


def safe_json_dumps(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":")
    )


def validate_match_id(match_id):
    if (
        not isinstance(match_id, int)
        or match_id <= 0
        or match_id > MAX_MATCH_ID
    ):
        raise HTTPException(
            status_code=400,
            detail="Match ID không hợp lệ."
        )


def validate_player_id(player_id):
    if not isinstance(player_id, str):
        raise HTTPException(
            status_code=400,
            detail="Player ID không hợp lệ."
        )

    player_id = player_id.strip()

    if not player_id:
        raise HTTPException(
            status_code=400,
            detail="Player ID không được để trống."
        )

    if len(player_id) > MAX_PLAYER_ID_LENGTH:
        raise HTTPException(
            status_code=400,
            detail="Player ID quá dài."
        )

    return player_id


def normalize_settings(data):
    grade = int(
        getattr(
            data,
            "grade",
            DEFAULT_GRADE
        )
    )

    if grade < 10 or grade > 12:
        raise HTTPException(
            status_code=400,
            detail="Khối lớp không hợp lệ."
        )

    difficulty = str(
        getattr(
            data,
            "difficulty",
            DEFAULT_DIFFICULTY
        )
    ).strip().lower()

    if difficulty not in VALID_DIFFICULTIES:
        difficulty = DEFAULT_DIFFICULTY

    question_type = str(
        getattr(
            data,
            "question_type",
            DEFAULT_QUESTION_TYPE
        )
    ).strip().lower()

    aliases = {
        "choice": "multiple_choice",
        "mcq": "multiple_choice",
        "multiple-choice": "multiple_choice",
        "input": "short_answer",
        "short": "short_answer",
        "short-answer": "short_answer",
        "tf": "true_false",
        "true-false": "true_false"
    }

    question_type = aliases.get(
        question_type,
        question_type
    )

    if question_type not in VALID_QUESTION_TYPES:
        question_type = DEFAULT_QUESTION_TYPE

    topics = getattr(
        data,
        "topics",
        []
    )

    if not isinstance(topics, list):
        topics = []

    cleaned_topics = []

    for topic in topics:
        if not isinstance(topic, str):
            continue

        topic = topic.strip()

        if (
            topic
            and topic not in cleaned_topics
        ):
            cleaned_topics.append(topic)

    return {
        "grade": grade,
        "topics": cleaned_topics[:MAX_TOPIC_COUNT],
        "difficulty": difficulty,
        "question_type": question_type
    }


def get_default_topics(grade):
    try:
        topics = ai_service.topics(grade)

        if isinstance(topics, list):
            result = []

            for topic in topics:
                if isinstance(topic, dict):
                    topic_id = (
                        topic.get("id")
                        or topic.get("code")
                        or topic.get("topic_id")
                    )

                    if topic_id:
                        result.append(
                            str(topic_id)
                        )

                elif isinstance(topic, str):
                    result.append(topic)

            if result:
                return result[:MAX_TOPIC_COUNT]

    except Exception:
        pass

    return [
        "PROBABILITY",
        "COMBINATION",
        "PERMUTATION",
        "FUNCTION",
        "SYSTEM_EQUATION"
    ]



def choose_random_bank_topics(grade, fallback):
    """Choose actual grade-matching topics with existing bank questions.

    Only used when a battle was requested without manually selected topics.
    No questions are invented here; the regular battle validator still gates them.
    """
    try:
        topic_ids = [str(t.get('id') or t.get('code') or t.get('topic_id'))
                     for t in ai_service.topics(grade)
                     if isinstance(t, dict) and (t.get('id') or t.get('code') or t.get('topic_id'))]
        random.shuffle(topic_ids)
        result = []
        for topic_id in topic_ids:
            if ai_service._v254_candidates(grade, topic_id, 'medium', 'multiple_choice'):
                result.append(topic_id)
                if len(result) >= MAX_TOPIC_COUNT:
                    break
        return result or fallback
    except Exception:
        return fallback


def normalize_topics_for_grade(grade, topics):
    if not topics:
        return get_default_topics(grade)

    try:
        normalized = ai_service.knowledge.normalize_topics(
            grade,
            topics
        )

        if normalized:
            return normalized[:MAX_TOPIC_COUNT]

    except Exception:
        pass

    valid = []

    for topic in topics:
        try:
            if ai_service.knowledge.get(topic):
                valid.append(topic)
        except Exception:
            pass

    return valid[:MAX_TOPIC_COUNT]


def get_common_topics(grade, topics1, topics2):
    normalized1 = normalize_topics_for_grade(
        grade,
        topics1
    )

    normalized2 = normalize_topics_for_grade(
        grade,
        topics2
    )

    if not normalized1 or not normalized2:
        return []

    common = []

    for topic in normalized1:
        if (
            topic in normalized2
            and topic not in common
        ):
            common.append(topic)

    return common[:MAX_TOPIC_COUNT]


def generate_ai_battle_questions(grade, topics, difficulty, question_type, *, existing=None, count=MATCH_TOTAL_QUESTIONS):
    """Battle only reads existing bank entries; never invokes a generator.

    Returns a shared batch of validated questions, excluding previous prompts.
    If the bank is exhausted, it returns a shorter batch or raises 503 initially.
    """
    from ..ai.engine.validator import validate, ValidationError
    from ..questions.answer_checker import canonical_type
    existing = list(existing or [])
    seen = {" ".join(str(q.get("question", "")).casefold().split()) for q in existing}
    result = []
    topics = list(dict.fromkeys(str(t) for t in topics if t))
    if not topics:
        raise HTTPException(status_code=409, detail="Hai người chơi không có chủ đề chung.")
    types = ["multiple_choice", "short_answer", "true_false"] if question_type == "mixed" else [question_type]
    candidates = []
    for topic in topics:
        for kind in types:
            for item in ai_service._curated_admin_candidates(grade, topic, difficulty, kind):
                q = ai_service._build_curated_question(item, grade, topic, difficulty, kind)
                if q is not None:
                    candidates.append(q)
            # V254 contains mostly medium-tier drafts. Prefer the requested
            # level; if no bank records exist, use medium as a clearly labeled
            # fallback so a random match can still start (no runtime generation).
            bank_rows = ai_service._v254_candidates(grade, topic, difficulty, kind)
            if not bank_rows and difficulty != "medium":
                bank_rows = ai_service._v254_candidates(grade, topic, "medium", kind)
            for item in bank_rows:
                try:
                    options = json.loads(item.get("options") or "[]")
                    q = {
                        "id": "v254_" + str(item["id"]), "grade": grade,
                        "topic": topic, "difficulty": "medium",
                        "question_type": item["question_type"],
                        "question": item["question"], "answer": item["answer"],
                        "solution": item["solution"], "explanation": item["solution"],
                        "options": options, "source": "Question_Bank_V254",
                        "bank_status": "candidate_unverified",
                        "difficulty_fallback": (item["difficulty"] != difficulty),
                        "archetype": "v254_" + str(item["id"]),
                        "template_family": "v254_" + str(item["id"]),
                    }
                    candidates.append(q)
                except (ValueError, TypeError, KeyError):
                    continue
    random.shuffle(candidates)
    for q in candidates:
        if len(result) >= count:
            break
        text = " ".join(str(q.get("question") or "").casefold().split())
        if not text or text in seen:
            continue
        try:
            validate(q)
            if canonical_type(q) not in types:
                continue
        except (ValidationError, ValueError, KeyError, TypeError):
            continue
        seen.add(text)
        q["battle_index"] = len(existing) + len(result)
        result.append(q)
    if not result and not existing:
        raise HTTPException(status_code=503, detail="Ngân hàng chưa có câu hỏi hợp lệ cho chủ đề đã chọn. Battle không tự tạo câu hỏi.")
    return result


def extend_battle_bank(cursor, match, player_number):
    """Extend the SAME deck atomically when a player reaches its end."""
    if match["status"] != "PLAYING" or is_match_expired(match):
        return match
    questions = safe_json_loads(match["questions"], [])
    if not isinstance(questions, list):
        return match
    answers = load_player_answers(match, player_number)
    if len(answers) < len(questions):
        return match
    more = generate_ai_battle_questions(
        match["grade"], safe_json_loads(match["topics"], []),
        match["difficulty"], match["question_type"], existing=questions,
    )
    if more:
        cursor.execute("UPDATE matches SET questions=? WHERE id=? AND status='PLAYING'",
                       (safe_json_dumps(questions + more), match["id"]))
        return cursor.execute("SELECT * FROM matches WHERE id=?", (match["id"],)).fetchone()
    return match


def sanitize_question(question, index=None):
    safe = {
        "id": question.get("id"),
        "battle_index": (
            question.get("battle_index")
            if index is None
            else index
        ),
        "topic": question.get("topic"),
        "type": question.get("type"),
        "question_type": question.get(
            "question_type"
        ),
        "question": question.get("question"),
        "difficulty": question.get("difficulty")
    }

    options = question.get("options")

    if isinstance(options, list):
        safe["options"] = options

    statements = question.get("statements")
    if isinstance(statements, list):
        safe["statements"] = [str(item) for item in statements]

    return safe


def sanitize_questions(questions):
    return [
        sanitize_question(
            question,
            index
        )
        for index, question in enumerate(
            questions
        )
        if isinstance(question, dict)
    ]


def get_match_for_user(user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                (
                    player1_id = ?
                    OR player2_id = ?
                )
                AND status NOT IN (
                    'FINISHED',
                    'CANCELLED'
                )
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                user_id
            )
        )

        return cursor.fetchone()

    finally:
        connection.close()


def get_user_by_player_id(player_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                level,
                xp,
                last_seen
            FROM users
            WHERE player_id = ? COLLATE NOCASE
            """,
            (player_id,)
        )

        return cursor.fetchone()

    finally:
        connection.close()


def is_friend(user1_id, user2_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM friends
            WHERE
                (
                    (
                        requester_id = ?
                        AND receiver_id = ?
                    )
                    OR
                    (
                        requester_id = ?
                        AND receiver_id = ?
                    )
                )
                AND status = 'accepted'
            LIMIT 1
            """,
            (
                user1_id,
                user2_id,
                user2_id,
                user1_id
            )
        )

        return cursor.fetchone() is not None

    finally:
        connection.close()


def cleanup_expired_queue(cursor):
    cursor.execute(
        """
        DELETE FROM matchmaking_queue
        -- created_at is ISO 8601 (e.g. 2026-11-11T10:00:00+00:00).
        -- Comparing that text with SQLite's space-separated datetime()
        -- fails for rows from the same day. Compare normalized instants.
        WHERE julianday(created_at) < julianday('now', '-10 minutes')
        """
    )


def cleanup_expired_invites(cursor):
    cursor.execute(
        """
        SELECT
            id,
            match_id
        FROM match_invites
        WHERE
            status = 'pending'
            AND julianday(created_at) < julianday('now', '-120 seconds')
        """
    )

    expired = cursor.fetchall()

    for invite in expired:
        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'expired'
            WHERE
                id = ?
                AND status = 'pending'
            """,
            (invite["id"],)
        )

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'CANCELLED',
                finished_at = ?
            WHERE
                id = ?
                AND status = 'INVITED'
            """,
            (
                now_iso(),
                invite["match_id"]
            )
        )


def expire_match_if_needed(cursor, match):
    """Finish a timed-out match with a real scoreboard, not an empty draw.

    Completed players retain their measured finish times. Anyone who did not
    finish receives the match time limit, so elapsed-time tie-breaks remain
    meaningful even if one player's connection disappears.
    """
    if not is_match_expired(match):
        return False

    questions = safe_json_loads(match["questions"], [])
    if not isinstance(questions, list):
        questions = []
    count = len(questions)
    p1_answers = load_player_answers(match, 1)
    p2_answers = load_player_answers(match, 2)
    p1 = calculate_player_stats(questions, p1_answers, match["started_at"])
    p2 = calculate_player_stats(questions, p2_answers, match["started_at"])
    p1["time"] = (
        float(match["player1_time"] or 0) or MATCH_MAX_DURATION_SECONDS
        if count and len(p1_answers) >= count else MATCH_MAX_DURATION_SECONDS
    )
    p2["time"] = (
        float(match["player2_time"] or 0) or MATCH_MAX_DURATION_SECONDS
        if count and len(p2_answers) >= count else MATCH_MAX_DURATION_SECONDS
    )
    winner_id = calculate_winner({
        **dict(match),
        "player1_correct": p1["correct"], "player1_wrong": p1["wrong"],
        "player1_blank": p1["blank"], "player1_time": p1["time"],
        "player2_correct": p2["correct"], "player2_wrong": p2["wrong"],
        "player2_blank": p2["blank"], "player2_time": p2["time"],
    }) if count else None
    cursor.execute("""
        UPDATE matches
        SET status='FINISHED', finished_at=?, winner_id=?,
            player1_correct=?, player1_wrong=?, player1_blank=?, player1_time=?,
            player2_correct=?, player2_wrong=?, player2_blank=?, player2_time=?
        WHERE id=? AND status='PLAYING'
    """, (
        now_iso(), winner_id,
        p1["correct"], p1["wrong"], p1["blank"], p1["time"],
        p2["correct"], p2["wrong"], p2["blank"], p2["time"],
        match["id"],
    ))
    return cursor.rowcount > 0


def cleanup_expired_matches(cursor):
    cursor.execute("SELECT * FROM matches WHERE status='PLAYING'")
    for match in cursor.fetchall():
        expire_match_if_needed(cursor, match)


def cleanup_matchmaking():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_queue(cursor)
        cleanup_expired_invites(cursor)
        cleanup_expired_matches(cursor)

        connection.commit()

    finally:
        connection.close()


def get_players(cursor, player1_id, player2_id):
    cursor.execute(
        """
        SELECT
            id,
            player_id,
            username,
            level,
            xp,
            last_seen
        FROM users
        WHERE id IN (?, ?)
        """,
        (
            player1_id,
            player2_id
        )
    )

    rows = cursor.fetchall()

    return {
        row["id"]: row
        for row in rows
    }


def format_player(player):
    if not player:
        return None

    return {
        "id": player["id"],
        "player_id": player["player_id"],
        "username": player["username"],
        "level": player["level"],
        "xp": player["xp"],
        "last_seen": player["last_seen"]
    }


def get_opponent_id(match, user_id):
    if user_id == match["player1_id"]:
        return match["player2_id"]

    if user_id == match["player2_id"]:
        return match["player1_id"]

    return None


def is_match_expired(match):
    if match["status"] != "PLAYING":
        return False

    elapsed = seconds_since(
        match["started_at"]
    )

    return (
        elapsed is not None
        and elapsed >= MATCH_MAX_DURATION_SECONDS
    )


def get_question_count(match):
    questions = safe_json_loads(
        match["questions"],
        []
    )

    if not isinstance(questions, list):
        return 0

    return len(questions)


def load_player_answers(match, player_number):
    key = (
        "player1_answers"
        if player_number == 1
        else "player2_answers"
    )

    answers = safe_json_loads(
        match[key],
        {}
    )

    return answers if isinstance(
        answers,
        dict
    ) else {}


def save_player_answers(
    cursor,
    match_id,
    player_number,
    answers
):
    column = (
        "player1_answers"
        if player_number == 1
        else "player2_answers"
    )

    cursor.execute(
        f"""
        UPDATE matches
        SET {column} = ?
        WHERE id = ?
        """,
        (
            safe_json_dumps(answers),
            match_id
        )
    )


def get_player_number(match, user_id):
    if user_id == match["player1_id"]:
        return 1

    if user_id == match["player2_id"]:
        return 2

    return None


def normalize_answer(answer):
    if isinstance(answer, str):
        return answer.strip()

    if isinstance(answer, bool):
        return answer

    if isinstance(answer, (int, float)):
        return answer

    if isinstance(answer, list):
        return [
            normalize_answer(item)
            for item in answer
        ]

    if isinstance(answer, dict):
        return {
            str(key): normalize_answer(value)
            for key, value in answer.items()
        }

    return answer


def check_battle_answer(question, user_answer):
    from ..questions.answer_checker import grade_answer
    return grade_answer(question, user_answer)


def calculate_player_stats(questions, answers, started_at):
    """Count only submitted answers; unanswered shared-deck entries are not skips."""
    correct = wrong = blank = 0
    for index in range(len(questions)):
        item = answers.get(str(index))
        if not isinstance(item, dict):
            continue
        if item.get("skipped"):
            blank += 1
        elif item.get("correct"):
            correct += 1
        else:
            wrong += 1
    return {"correct": correct, "wrong": wrong, "blank": blank,
            "time": seconds_since(started_at) or 0}



def calculate_winner(match):
    """Correct desc, elapsed asc, wrong asc, attempted desc, skipped asc."""
    def rank(number):
        correct = int(match[f"player{number}_correct"] or 0)
        wrong = int(match[f"player{number}_wrong"] or 0)
        skipped = int(match[f"player{number}_blank"] or 0)
        elapsed = float(match[f"player{number}_time"] or 0)
        attempted = correct + wrong + skipped
        return (correct, -elapsed, -wrong, attempted, -skipped)

    p1, p2 = rank(1), rank(2)
    if p1 == p2:
        return None
    return match["player1_id"] if p1 > p2 else match["player2_id"]



def finalize_match_if_needed(
    cursor,
    match,
    questions
):
    # Five-minute Battle is time-limited, never question-count-limited.
    return False, None

    question_count = len(
        questions
    )

    p1_answers = load_player_answers(
        match,
        1
    )

    p2_answers = load_player_answers(
        match,
        2
    )

    p1_done = len(
        p1_answers
    ) >= question_count

    p2_done = len(
        p2_answers
    ) >= question_count

    if not (
        p1_done
        and p2_done
    ):
        return False, None

    p1_stats = calculate_player_stats(
        questions,
        p1_answers,
        match["started_at"]
    )

    p2_stats = calculate_player_stats(
        questions,
        p2_answers,
        match["started_at"]
    )

    # Do not recompute BOTH players' finish times now: doing so assigns
    # the same elapsed time to the two players and destroys the speed tie-break.
    # Each participant's elapsed time was persisted by update_player_stats at
    # their own final answer/skip, and must remain unchanged afterwards.
    p1_stats["time"] = float(match["player1_time"] or 0)
    p2_stats["time"] = float(match["player2_time"] or 0)

    winner_id = calculate_winner(
        {
            **dict(match),
            "player1_correct": p1_stats["correct"],
            "player1_wrong": p1_stats["wrong"],
            "player1_blank": p1_stats["blank"],
            "player1_time": p1_stats["time"],
            "player2_correct": p2_stats["correct"],
            "player2_wrong": p2_stats["wrong"],
            "player2_blank": p2_stats["blank"],
            "player2_time": p2_stats["time"]
        }
    )

    cursor.execute(
        """
        UPDATE matches
        SET
            status = 'FINISHED',

            player1_correct = ?,
            player1_wrong = ?,
            player1_blank = ?,
            player1_time = ?,

            player2_correct = ?,
            player2_wrong = ?,
            player2_blank = ?,
            player2_time = ?,

            winner_id = ?,
            finished_at = ?

        WHERE
            id = ?
            AND status = 'PLAYING'
        """,
        (
            p1_stats["correct"],
            p1_stats["wrong"],
            p1_stats["blank"],
            p1_stats["time"],

            p2_stats["correct"],
            p2_stats["wrong"],
            p2_stats["blank"],
            p2_stats["time"],

            winner_id,
            now_iso(),
            match["id"]
        )
    )

    return True, winner_id


def update_player_stats(
    cursor,
    match,
    questions,
    player_number,
    answers
):
    stats = calculate_player_stats(
        questions,
        answers,
        match["started_at"]
    )

    if player_number == 1:
        cursor.execute(
            """
            UPDATE matches
            SET
                player1_current = ?,
                player1_correct = ?,
                player1_wrong = ?,
                player1_blank = ?,
                player1_time = ?
            WHERE id = ?
            """,
            (
                len(answers),
                stats["correct"],
                stats["wrong"],
                stats["blank"],
                stats["time"],
                match["id"]
            )
        )

    else:
        cursor.execute(
            """
            UPDATE matches
            SET
                player2_current = ?,
                player2_correct = ?,
                player2_wrong = ?,
                player2_blank = ?,
                player2_time = ?
            WHERE id = ?
            """,
            (
                len(answers),
                stats["correct"],
                stats["wrong"],
                stats["blank"],
                stats["time"],
                match["id"]
            )
        )

    return stats


# =========================================================
# RANDOM MATCHMAKING
# =========================================================

@router.post("/random/join")
def join_random_match(
    data: MatchSettings | None = None,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    settings = normalize_settings(
        data or MatchSettings()
    )
    settings["topics"] = normalize_topics_for_grade(
        settings["grade"], settings["topics"]
    )
    if not settings["topics"]:
        settings["topics"] = get_default_topics(settings["grade"])

    cleanup_matchmaking()

    existing_match = get_match_for_user(
        user["id"]
    )

    if existing_match:
        return {
            "success": True,
            "status": "MATCHED",
            "match_id": existing_match["id"]
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_queue(
            cursor
        )

        cursor.execute(
            """
            DELETE FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        cursor.execute(
            """
            SELECT *
            FROM matchmaking_queue
            WHERE user_id != ?
            ORDER BY id ASC
            """,
            (user["id"],)
        )

        queued_players = cursor.fetchall()

        opponent = None
        common_topics = []

        for candidate in queued_players:
            opponent_id = candidate["user_id"]

            opponent_match = get_match_for_user(
                opponent_id
            )

            if opponent_match:
                cursor.execute(
                    """
                    DELETE FROM matchmaking_queue
                    WHERE user_id = ?
                    """,
                    (opponent_id,)
                )
                continue

            candidate_topics = safe_json_loads(
                candidate["topics"],
                []
            )

            candidate_grade = int(
                candidate["grade"]
                or DEFAULT_GRADE
            )

            if candidate_grade != settings["grade"]:
                continue

            common_topics = get_common_topics(
                settings["grade"],
                settings["topics"],
                candidate_topics
            )

            if common_topics:
                opponent = candidate
                break

        if opponent:
            opponent_id = opponent["user_id"]

            opponent_topics = safe_json_loads(
                opponent["topics"],
                []
            )

            opponent_difficulty = (
                opponent["difficulty"]
                or DEFAULT_DIFFICULTY
            )

            opponent_question_type = (
                opponent["question_type"]
                or DEFAULT_QUESTION_TYPE
            )

            difficulty = settings["difficulty"]

            if difficulty != opponent_difficulty:
                difficulty = DEFAULT_DIFFICULTY

            question_type = settings[
                "question_type"
            ]

            if question_type != opponent_question_type:
                question_type = DEFAULT_QUESTION_TYPE

            # Auto mode: draw random topics from the actual existing grade bank,
            # while keeping manually selected topics unchanged.
            if not getattr(data, 'topics', None) and common_topics == get_default_topics(settings['grade']):
                common_topics = choose_random_bank_topics(settings['grade'], common_topics)

            questions = generate_ai_battle_questions(
                settings["grade"],
                common_topics,
                difficulty,
                question_type
            )

            match_code = (
                "MW-"
                + uuid.uuid4().hex[:10].upper()
            )

            cursor.execute(
                """
                DELETE FROM matchmaking_queue
                WHERE user_id IN (?, ?)
                """,
                (
                    opponent_id,
                    user["id"]
                )
            )

            cursor.execute(
                """
                INSERT INTO matches
                (
                    match_code,
                    player1_id,
                    player2_id,
                    status,
                    questions,
                    topics,
                    grade,
                    difficulty,
                    question_type,
                    player1_answers,
                    player2_answers,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    match_code,
                    opponent_id,
                    user["id"],
                    "STARTING",
                    safe_json_dumps(
                        questions
                    ),
                    safe_json_dumps(
                        common_topics
                    ),
                    settings["grade"],
                    difficulty,
                    question_type,
                    "{}",
                    "{}",
                    now_iso()
                )
            )

            match_id = cursor.lastrowid

            connection.commit()

            return {
                "success": True,
                "status": "MATCHED",
                "match_id": match_id,
                "topics": common_topics,
                "grade": settings["grade"],
                "difficulty": difficulty,
                "question_type": question_type,
                "question_count": len(
                    questions
                )
            }

        cursor.execute(
            """
            INSERT INTO matchmaking_queue
            (
                user_id,
                created_at,
                grade,
                topics,
                difficulty,
                question_type
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                created_at = excluded.created_at,
                grade = excluded.grade,
                topics = excluded.topics,
                difficulty = excluded.difficulty,
                question_type = excluded.question_type
            """,
            (
                user["id"],
                now_iso(),
                settings["grade"],
                safe_json_dumps(
                    settings["topics"]
                ),
                settings["difficulty"],
                settings["question_type"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "QUEUED",
            "grade": settings["grade"],
            "topics": settings["topics"],
            "difficulty": settings["difficulty"],
            "question_type": settings["question_type"]
        }

    finally:
        connection.close()


# =========================================================
# RANDOM STATUS
# =========================================================

@router.get("/random/status")
def random_match_status(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    cleanup_matchmaking()

    match = get_match_for_user(
        user["id"]
    )

    if match:
        return {
            "success": True,
            "status": "MATCHED",
            "match_id": match["id"],
            "match_status": match["status"]
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                created_at,
                grade,
                topics,
                difficulty,
                question_type
            FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        queue = cursor.fetchone()

    finally:
        connection.close()

    if not queue:
        return {
            "success": True,
            "status": "IDLE",
            "waiting": False
        }

    waiting_seconds = seconds_since(
        queue["created_at"]
    )

    return {
        "success": True,
        "status": "QUEUED",
        "waiting": True,
        "waiting_seconds": waiting_seconds or 0,
        "grade": queue["grade"],
        "topics": safe_json_loads(
            queue["topics"],
            []
        ),
        "difficulty": queue["difficulty"],
        "question_type": queue["question_type"]
    }


# =========================================================
# RANDOM CANCEL
# =========================================================

@router.post("/random/cancel")
def cancel_random_match(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        connection.commit()

        return {
            "success": True,
            "status": "CANCELLED"
        }

    finally:
        connection.close()


# =========================================================
# FIND PLAYER
# =========================================================

@router.get("/player")
def find_player(
    player_id: str,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    player_id = validate_player_id(
        player_id
    )

    target = get_user_by_player_id(
        player_id
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    if target["id"] == user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Bạn không thể đấu với chính mình."
        )

    existing_match = get_match_for_user(
        target["id"]
    )

    return {
        "id": target["id"],
        "player_id": target["player_id"],
        "username": target["username"],
        "level": target["level"],
        "xp": target["xp"],
        "last_seen": target["last_seen"],
        "online": is_user_online(target["last_seen"]),
        "in_match": existing_match is not None,
        "is_friend": is_friend(
            user["id"],
            target["id"]
        )
    }


# =========================================================
# DIRECT INVITE
# =========================================================

@router.post("/invite")
def invite_player(
    data: InviteRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    settings = normalize_settings(
        data
    )
    settings["topics"] = normalize_topics_for_grade(
        settings["grade"], settings["topics"]
    )
    if not settings["topics"]:
        settings["topics"] = get_default_topics(settings["grade"])

    target_player_id = validate_player_id(
        data.player_id
    )

    target = get_user_by_player_id(
        target_player_id
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    if target["id"] == user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Bạn không thể mời chính mình."
        )

    current_match = get_match_for_user(
        user["id"]
    )

    if current_match:
        raise HTTPException(
            status_code=400,
            detail="Bạn đang ở trong một trận đấu."
        )

    target_match = get_match_for_user(
        target["id"]
    )

    if target_match:
        raise HTTPException(
            status_code=400,
            detail="Người chơi này đang ở trong một trận đấu."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_invites(
            cursor
        )

        cursor.execute(
            """
            SELECT id
            FROM match_invites
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            LIMIT 1
            """,
            (
                user["id"],
                target["id"]
            )
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Bạn đã gửi lời mời cho người này."
            )

        cursor.execute(
            """
            SELECT id
            FROM match_invites
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            LIMIT 1
            """,
            (
                target["id"],
                user["id"]
            )
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Người này đã gửi lời mời cho bạn."
            )

        target_topics = get_default_topics(
            settings["grade"]
        )

        common_topics = get_common_topics(
            settings["grade"],
            settings["topics"],
            target_topics
        )

        if not common_topics:
            common_topics = settings["topics"]

        if not common_topics:
            raise HTTPException(
                status_code=400,
                detail="Bạn cần chọn ít nhất một chủ đề để đấu."
            )

        if not data.topics:
            common_topics = choose_random_bank_topics(settings['grade'], common_topics)

        questions = generate_ai_battle_questions(
            settings["grade"],
            common_topics,
            settings["difficulty"],
            settings["question_type"]
        )

        match_code = (
            "MW-"
            + uuid.uuid4().hex[:10].upper()
        )

        cursor.execute(
            """
            INSERT INTO matches
            (
                match_code,
                player1_id,
                player2_id,
                status,
                questions,
                topics,
                grade,
                difficulty,
                question_type,
                player1_answers,
                player2_answers,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_code,
                user["id"],
                target["id"],
                "INVITED",
                safe_json_dumps(
                    questions
                ),
                safe_json_dumps(
                    common_topics
                ),
                settings["grade"],
                settings["difficulty"],
                settings["question_type"],
                "{}",
                "{}",
                now_iso()
            )
        )

        match_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO match_invites
            (
                match_id,
                sender_id,
                receiver_id,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                match_id,
                user["id"],
                target["id"],
                "pending",
                now_iso()
            )
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (
                user_id,
                type,
                title,
                message,
                related_user_id,
                related_id,
                is_read,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                target["id"],
                "pvp_invite",
                "Lời mời đấu PvP",
                f"{user['username']} đã mời bạn đấu PvP.",
                user["id"],
                match_id,
                now_iso()
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "INVITED",
            "match_id": match_id,
            "topics": common_topics,
            "grade": settings["grade"],
            "difficulty": settings["difficulty"],
            "question_type": settings["question_type"],
            "question_count": len(
                questions
            )
        }

    finally:
        connection.close()


# =========================================================
# GET MATCH
# =========================================================

@router.get("/match/{match_id}")
def get_match(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    cleanup_matchmaking()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận đấu."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu này."
            )

        player_number = get_player_number(match, user["id"])
        if is_match_expired(match):
            expire_match_if_needed(cursor, match)
            connection.commit()
            match = cursor.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
        elif match["status"] == "PLAYING":
            match = extend_battle_bank(cursor, match, player_number)
            connection.commit()

        players = get_players(
            cursor,
            match["player1_id"],
            match["player2_id"]
        )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            questions = []

        return {
            "id": match["id"],
            "match_code": match["match_code"],
            "status": match["status"],
            "player1_id": match["player1_id"],
            "player2_id": match["player2_id"],

            "players": [
                format_player(
                    players[player_id]
                )
                for player_id in (
                    match["player1_id"],
                    match["player2_id"]
                )
                if player_id in players
            ],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "question_count": len(
                questions
            ),

            "questions": sanitize_questions(
                questions
            ),

            "winner_id": match["winner_id"],
            "created_at": match["created_at"],
            "started_at": match["started_at"],
            "finished_at": match["finished_at"],
            "server_now": now_iso(),
            "duration_seconds": MATCH_MAX_DURATION_SECONDS,
        }

    finally:
        connection.close()


# =========================================================
# ACCEPT INVITE
# =========================================================

@router.post("/match/{match_id}/accept")
def accept_invite(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    cleanup_matchmaking()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (
                match_id,
                user["id"]
            )
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Lời mời không còn tồn tại."
            )

        existing_match = get_match_for_user(
            user["id"]
        )

        # get_match_for_user() intentionally includes INVITED matches.
        # The invitation being accepted is therefore expected to be returned
        # here; only block a different active match.
        if existing_match and int(existing_match["id"]) != int(match_id):
            raise HTTPException(
                status_code=400,
                detail="Bạn đang ở trong một trận đấu khác."
            )

        # Accept + start is ONE atomic, server-authoritative transition.
        # Both users see exactly the same started_at, even if one tab is late.
        started_at = now_iso()
        cursor.execute(
            """
            UPDATE matches
            SET status = 'PLAYING', started_at = ?
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (started_at, match_id, user["id"])
        )

        if cursor.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Lời mời vừa được xử lý."
            )

        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'accepted'
            WHERE
                match_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                match_id,
                user["id"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "PLAYING",
            "match_id": match_id,
            "started_at": started_at,
            "duration_seconds": MATCH_MAX_DURATION_SECONDS,
        }

    finally:
        connection.close()


# =========================================================
# REJECT INVITE
# =========================================================

@router.post("/match/{match_id}/reject")
def reject_invite(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (
                match_id,
                user["id"]
            )
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Lời mời không còn tồn tại."
            )

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'CANCELLED',
                finished_at = ?
            WHERE
                id = ?
                AND status = 'INVITED'
            """,
            (
                now_iso(),
                match_id
            )
        )

        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'rejected'
            WHERE
                match_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                match_id,
                user["id"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "CANCELLED"
        }

    finally:
        connection.close()


# =========================================================
# START MATCH
# =========================================================

@router.post("/match/{match_id}/start")
def start_match(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] == "PLAYING":
            return {
                "success": True,
                "status": "PLAYING",
                "started_at": match["started_at"]
            }

        if match["status"] != "STARTING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa thể bắt đầu."
            )

        started_at = now_iso()

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'PLAYING',
                started_at = ?
            WHERE
                id = ?
                AND status = 'STARTING'
            """,
            (
                started_at,
                match_id
            )
        )

        if cursor.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Trận đấu vừa được bắt đầu."
            )

        connection.commit()

        return {
            "success": True,
            "status": "PLAYING",
            "started_at": started_at,
            "duration_seconds": MATCH_MAX_DURATION_SECONDS
        }

    finally:
        connection.close()


# =========================================================
# ANSWER
# =========================================================

@router.post("/match/{match_id}/answer")
def submit_answer(
    match_id: int,
    data: MatchAnswerRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()
        # Serialize concurrent answers from multiple tabs/devices. A stale
        # read must not overwrite an already submitted answer.
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] != "PLAYING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa ở trạng thái chơi."
            )

        if is_match_expired(match):
            expire_match_if_needed(cursor, match)
            connection.commit()
            raise HTTPException(
                status_code=409,
                detail="Trận đấu đã hết thời gian."
            )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            raise HTTPException(
                status_code=500,
                detail="Bộ câu hỏi không hợp lệ."
            )

        if data.question_index >= len(
            questions
        ):
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không tồn tại."
            )

        answers = load_player_answers(
            match,
            player_number
        )

        key = str(
            data.question_index
        )

        if data.question_index != len(answers):
            raise HTTPException(
                status_code=409,
                detail="Phải xử lý câu hỏi theo đúng thứ tự trong trận đấu."
            )

        if key in answers:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã trả lời câu này."
            )

        question = questions[
            data.question_index
        ]

        correct = check_battle_answer(
            question,
            data.answer
        )

        answers[key] = {
            "correct": bool(correct),
            "skipped": False,
            "answered_at": now_iso()
        }

        save_player_answers(
            cursor,
            match_id,
            player_number,
            answers
        )

        stats = update_player_stats(
            cursor,
            match,
            questions,
            player_number,
            answers
        )

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        updated_match = cursor.fetchone()

        finished, winner_id = (
            finalize_match_if_needed(
                cursor,
                updated_match,
                questions
            )
        )

        connection.commit()

        current = len(
            answers
        )

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            updated_match,
            opponent_number
        )

        return {
            "success": True,
            "question_index": data.question_index,
            "correct": bool(correct),

            "correct_answer": (
                question.get("answer")
                if not correct
                else None
            ),

            "solution": (
                question.get("solution")
                if not correct
                else None
            ),

            "current": current,
            "total": len(questions),

            "correct_count": stats["correct"],
            "wrong_count": stats["wrong"],
            "blank_count": stats["blank"],

            "opponent_progress": len(
                opponent_answers
            ),

            "status": (
                "FINISHED"
                if finished
                else "PLAYING"
            ),

            "winner_id": winner_id
        }

    finally:
        connection.close()


# =========================================================
# SKIP
# =========================================================

@router.post("/match/{match_id}/skip")
def skip_question(
    match_id: int,
    data: MatchSkipRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()
        # Serialize concurrent answers from multiple tabs/devices. A stale
        # read must not overwrite an already submitted answer.
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] != "PLAYING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa ở trạng thái chơi."
            )

        if is_match_expired(match):
            expire_match_if_needed(cursor, match)
            connection.commit()
            raise HTTPException(
                status_code=409,
                detail="Trận đấu đã hết thời gian."
            )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            raise HTTPException(
                status_code=500,
                detail="Bộ câu hỏi không hợp lệ."
            )

        if data.question_index >= len(
            questions
        ):
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không tồn tại."
            )

        answers = load_player_answers(
            match,
            player_number
        )

        key = str(
            data.question_index
        )

        if data.question_index != len(answers):
            raise HTTPException(
                status_code=409,
                detail="Phải xử lý câu hỏi theo đúng thứ tự trong trận đấu."
            )

        if key in answers:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã xử lý câu này."
            )

        answers[key] = {
            "correct": False,
            "skipped": True,
            "answered_at": now_iso()
        }

        save_player_answers(
            cursor,
            match_id,
            player_number,
            answers
        )

        stats = update_player_stats(
            cursor,
            match,
            questions,
            player_number,
            answers
        )

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        updated_match = cursor.fetchone()

        finished, winner_id = (
            finalize_match_if_needed(
                cursor,
                updated_match,
                questions
            )
        )

        connection.commit()

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            updated_match,
            opponent_number
        )

        return {
            "success": True,
            "question_index": data.question_index,
            "skipped": True,

            "current": len(
                answers
            ),

            "total": len(
                questions
            ),

            "correct_count": stats["correct"],
            "wrong_count": stats["wrong"],
            "blank_count": stats["blank"],

            "opponent_progress": len(
                opponent_answers
            ),

            "status": (
                "FINISHED"
                if finished
                else "PLAYING"
            ),

            "winner_id": winner_id
        }

    finally:
        connection.close()


# =========================================================
# PROGRESS
# =========================================================

@router.get("/match/{match_id}/progress")
def get_match_progress(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if is_match_expired(match):
            expire_match_if_needed(cursor, match)
            connection.commit()
            match = cursor.execute(
                "SELECT * FROM matches WHERE id=?", (match_id,)
            ).fetchone()

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            questions = []

        own_answers = load_player_answers(
            match,
            player_number
        )

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            match,
            opponent_number
        )

        own_stats = calculate_player_stats(
            questions,
            own_answers,
            match["started_at"]
        )

        opponent_stats = calculate_player_stats(
            questions,
            opponent_answers,
            match["started_at"]
        )

        # A completed player's recorded finish time must not keep increasing.
        for number, answers, stats in (
            (1 if player_number == 1 else 2, own_answers, own_stats),
            (2 if player_number == 1 else 1, opponent_answers, opponent_stats),
        ):
            if questions and len(answers) >= len(questions):
                stats["time"] = float(match[f"player{number}_time"] or 0)
            elif match["status"] == "FINISHED":
                stats["time"] = float(match[f"player{number}_time"] or 0)

        elapsed = seconds_since(
            match["started_at"]
        ) or 0

        remaining = max(
            0,
            MATCH_MAX_DURATION_SECONDS
            - elapsed
        )

        return {
            "success": True,
            "match_id": match_id,
            "status": match["status"],

            "total": len(
                questions
            ),

            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,

            "you": {
                "current": len(
                    own_answers
                ),
                **own_stats
            },

            "opponent": {
                "current": len(
                    opponent_answers
                ),
                **opponent_stats
            },

            "winner_id": match["winner_id"]
        }

    finally:
        connection.close()


# =========================================================
# RESULT
# =========================================================

@router.get("/match/{match_id}/result")
def get_match_result(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận."
            )

        if is_match_expired(match):
            expire_match_if_needed(cursor, match)
            connection.commit()
            match = cursor.execute(
                "SELECT * FROM matches WHERE id=?", (match_id,)
            ).fetchone()

        return {
            "success": True,
            "match_id": match["id"],
            "status": match["status"],
            "winner_id": match["winner_id"],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "player1": {
                "user_id": match["player1_id"],
                "correct": match["player1_correct"],
                "wrong": match["player1_wrong"],
                "blank": match["player1_blank"],
                "time": match["player1_time"]
            },

            "player2": {
                "user_id": match["player2_id"],
                "correct": match["player2_correct"],
                "wrong": match["player2_wrong"],
                "blank": match["player2_blank"],
                "time": match["player2_time"]
            },

            "is_finished": (
                match["status"]
                == "FINISHED"
            ),

            "is_draw": (
                match["status"]
                == "FINISHED"
                and match["winner_id"]
                is None
            )
        }

    finally:
        connection.close()


# =========================================================
# CURRENT MATCH
# =========================================================

@router.get("/current")
def current_match(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    cleanup_matchmaking()

    match = get_match_for_user(
        user["id"]
    )

    if not match:
        return {
            "success": True,
            "match": None,
            "match_id": None,
            "status": "IDLE"
        }

    return {
        "success": True,
        # Keep top-level aliases for the polling client and the nested object for newer clients.
        "match_id": match["id"],
        "status": match["status"],
        "match": {
            "id": match["id"],
            "match_code": match["match_code"],
            "status": match["status"],
            "player1_id": match["player1_id"],
            "player2_id": match["player2_id"],
            "winner_id": match["winner_id"],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "created_at": match["created_at"],
            "started_at": match["started_at"],
            "finished_at": match["finished_at"]
        }
    }


# =========================================================
# PENDING INVITES
# =========================================================

@router.get("/invites")
def get_pending_invites(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_invites(
            cursor
        )

        cursor.execute(
            """
            SELECT
                mi.id,
                mi.match_id,
                mi.sender_id,
                mi.receiver_id,
                mi.status,
                mi.created_at,

                u.player_id,
                u.username,
                u.level,
                u.xp

            FROM match_invites mi

            JOIN users u
                ON u.id = mi.sender_id

            WHERE
                mi.receiver_id = ?
                AND mi.status = 'pending'

            ORDER BY mi.id DESC
            """,
            (user["id"],)
        )

        rows = cursor.fetchall()

        connection.commit()

        invites = []

        for row in rows:
            invites.append(
                {
                    "id": row["id"],
                    "match_id": row["match_id"],
                    "status": row["status"],
                    "created_at": row["created_at"],

                    "sender": {
                        "id": row["sender_id"],
                        "player_id": row["player_id"],
                        "username": row["username"],
                        "level": row["level"],
                        "xp": row["xp"]
                    }
                }
            )

        return {
            "success": True,
            "invites": invites,
            "count": len(invites)
        }

    finally:
        connection.close()
