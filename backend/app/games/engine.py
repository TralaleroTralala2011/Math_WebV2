from dataclasses import dataclass, field
from typing import Optional
import time


# =========================================================
# GAME LEVEL
# =========================================================

LEVELS = {
    "easy": {
        "name": "Dễ",
        "xp_per_correct": 10,
        "score_per_correct": 10,
    },
    "medium": {
        "name": "Vừa",
        "xp_per_correct": 15,
        "score_per_correct": 15,
    },
    "hard": {
        "name": "Khó",
        "xp_per_correct": 25,
        "score_per_correct": 25,
    },
}


# =========================================================
# GAME CONFIG
# =========================================================

DEFAULT_TOTAL_QUESTIONS = 10

MIN_QUESTIONS = 1
MAX_QUESTIONS = 50

MAX_GAME_TIME = 60 * 60

MAX_GAME_ID_LENGTH = 100
MAX_USER_ID = 2_147_483_647
MAX_GAME_NAME_LENGTH = 150
MAX_TOPIC_NAME_LENGTH = 100


# =========================================================
# GAME STATE
# =========================================================

@dataclass
class GameState:

    game_id: str

    user_id: int

    game_name: str

    topic_name: str

    current_level: str = "easy"

    total_questions: int = DEFAULT_TOTAL_QUESTIONS

    current_question: int = 0

    correct: int = 0

    wrong: int = 0

    blank: int = 0

    score: int = 0

    xp: int = 0

    started_at: float = field(default_factory=time.time)

    finished_at: Optional[float] = None

    finished: bool = False

    answered_questions: int = 0


# =========================================================
# GAME ENGINE
# =========================================================

class GameEngine:

    def __init__(
        self,
        game_id: str,
        user_id: int,
        game_name: str,
        topic_name: str,
        total_questions: int = DEFAULT_TOTAL_QUESTIONS,
    ):

        # -------------------------------------------------
        # GAME ID
        # -------------------------------------------------

        if not isinstance(game_id, str):

            raise ValueError(
                "game_id phải là chuỗi."
            )

        game_id = game_id.strip()

        if not game_id:

            raise ValueError(
                "game_id không được để trống."
            )

        if len(game_id) > MAX_GAME_ID_LENGTH:

            raise ValueError(
                f"game_id không được vượt quá "
                f"{MAX_GAME_ID_LENGTH} ký tự."
            )


        # -------------------------------------------------
        # USER ID
        # -------------------------------------------------

        if isinstance(user_id, bool) or not isinstance(user_id, int):

            raise ValueError(
                "user_id phải là số nguyên."
            )

        if user_id <= 0:

            raise ValueError(
                "user_id phải lớn hơn 0."
            )

        if user_id > MAX_USER_ID:

            raise ValueError(
                "user_id không hợp lệ."
            )


        # -------------------------------------------------
        # GAME NAME
        # -------------------------------------------------

        if not isinstance(game_name, str):

            raise ValueError(
                "game_name phải là chuỗi."
            )

        game_name = game_name.strip()

        if not game_name:

            raise ValueError(
                "game_name không được để trống."
            )

        if len(game_name) > MAX_GAME_NAME_LENGTH:

            raise ValueError(
                f"game_name không được vượt quá "
                f"{MAX_GAME_NAME_LENGTH} ký tự."
            )


        # -------------------------------------------------
        # TOPIC
        # -------------------------------------------------

        if not isinstance(topic_name, str):

            raise ValueError(
                "topic_name phải là chuỗi."
            )

        topic_name = topic_name.strip()

        if not topic_name:

            raise ValueError(
                "topic_name không được để trống."
            )

        if len(topic_name) > MAX_TOPIC_NAME_LENGTH:

            raise ValueError(
                f"topic_name không được vượt quá "
                f"{MAX_TOPIC_NAME_LENGTH} ký tự."
            )


        # -------------------------------------------------
        # TOTAL QUESTIONS
        # -------------------------------------------------

        if isinstance(total_questions, bool):

            raise ValueError(
                "total_questions phải là số nguyên."
            )

        if not isinstance(total_questions, int):

            raise ValueError(
                "total_questions phải là số nguyên."
            )

        if (
            total_questions < MIN_QUESTIONS
            or total_questions > MAX_QUESTIONS
        ):

            raise ValueError(
                f"Số câu phải từ "
                f"{MIN_QUESTIONS} đến "
                f"{MAX_QUESTIONS}."
            )


        # -------------------------------------------------
        # CREATE STATE
        # -------------------------------------------------

        self.state = GameState(
            game_id=game_id,
            user_id=user_id,
            game_name=game_name,
            topic_name=topic_name,
            total_questions=total_questions,
        )


    # =====================================================
    # LEVEL
    # =====================================================

    def get_current_level(self) -> str:

        return self.state.current_level


    def get_current_level_name(self) -> str:

        level = self.state.current_level

        return LEVELS[level]["name"]


    def set_level(self, level: str):

        if not isinstance(level, str):

            raise ValueError(
                "Độ khó phải là chuỗi."
            )

        level = level.strip().lower()

        if level not in LEVELS:

            raise ValueError(
                "Độ khó không hợp lệ."
            )

        self.state.current_level = level

        return self.state.current_level


    # =====================================================
    # LEVEL PROGRESSION
    # =====================================================

    def update_level(self):

        total = self.state.total_questions

        answered = self.state.answered_questions

        if total <= 0:

            self.state.current_level = "easy"

            return self.state.current_level


        progress = answered / total


        # -------------------------------------------------
        # 0% -> dưới 33.33%
        # -------------------------------------------------

        if progress < 1 / 3:

            self.state.current_level = "easy"


        # -------------------------------------------------
        # 33.33% -> dưới 66.67%
        # -------------------------------------------------

        elif progress < 2 / 3:

            self.state.current_level = "medium"


        # -------------------------------------------------
        # 66.67% -> 100%
        # -------------------------------------------------

        else:

            self.state.current_level = "hard"


        return self.state.current_level


    # =====================================================
    # PROGRESS
    # =====================================================

    def get_progress(self) -> float:

        total = self.state.total_questions

        if total <= 0:

            return 0.0

        progress = (
            self.state.answered_questions / total
        ) * 100

        return round(
            min(100.0, max(0.0, progress)),
            2
        )


    def get_remaining_questions(self) -> int:

        remaining = (
            self.state.total_questions
            - self.state.answered_questions
        )

        return max(
            0,
            remaining
        )


    def can_submit_answer(self) -> bool:

        if self.state.finished:

            return False

        if (
            self.state.answered_questions
            >= self.state.total_questions
        ):

            return False

        if self.is_timeout():

            return False

        return True


    # =====================================================
    # ANSWER VALIDATION
    # =====================================================

    @staticmethod
    def _validate_boolean(
        value: bool,
        field_name: str,
    ):

        if not isinstance(value, bool):

            raise ValueError(
                f"{field_name} phải là True hoặc False."
            )


    # =====================================================
    # ANSWER
    # =====================================================

    def submit_answer(
        self,
        is_correct: bool,
        is_blank: bool = False,
    ) -> dict:

        # -------------------------------------------------
        # VALIDATE INPUT
        # -------------------------------------------------

        self._validate_boolean(
            is_correct,
            "is_correct"
        )

        self._validate_boolean(
            is_blank,
            "is_blank"
        )


        # -------------------------------------------------
        # GAME FINISHED
        # -------------------------------------------------

        if self.state.finished:

            raise ValueError(
                "Game đã kết thúc."
            )


        # -------------------------------------------------
        # ALL QUESTIONS ANSWERED
        # -------------------------------------------------

        if (
            self.state.answered_questions
            >= self.state.total_questions
        ):

            self.finish()

            raise ValueError(
                "Đã trả lời đủ số câu."
            )


        # -------------------------------------------------
        # TIMEOUT
        # -------------------------------------------------

        if self.is_timeout():

            self.state.blank += 1

            self.state.answered_questions += 1

            self.state.current_question += 1

            self.update_level()

            self.finish()

            return {
                "result": "timeout",

                "correct": False,

                "xp_gained": 0,

                "score_gained": 0,

                "level": self.state.current_level,

                "difficulty_name": (
                    self.get_current_level_name()
                ),

                "question_number": (
                    self.state.current_question
                ),

                "finished": True,

                "remaining_questions": (
                    self.get_remaining_questions()
                ),
            }


        # -------------------------------------------------
        # CURRENT LEVEL
        # -------------------------------------------------

        level = self.state.current_level

        level_config = LEVELS[level]


        # -------------------------------------------------
        # BLANK ANSWER
        # -------------------------------------------------

        if is_blank:

            self.state.blank += 1

            result = "blank"

            xp_gained = 0

            score_gained = 0

            answer_correct = False


        # -------------------------------------------------
        # CORRECT ANSWER
        # -------------------------------------------------

        elif is_correct:

            self.state.correct += 1

            xp_gained = level_config[
                "xp_per_correct"
            ]

            score_gained = level_config[
                "score_per_correct"
            ]

            self.state.xp += xp_gained

            self.state.score += score_gained

            result = "correct"

            answer_correct = True


        # -------------------------------------------------
        # WRONG ANSWER
        # -------------------------------------------------

        else:

            self.state.wrong += 1

            xp_gained = 0

            score_gained = 0

            result = "wrong"

            answer_correct = False


        # -------------------------------------------------
        # UPDATE QUESTION
        # -------------------------------------------------

        self.state.answered_questions += 1

        self.state.current_question += 1


        # -------------------------------------------------
        # UPDATE DIFFICULTY
        # -------------------------------------------------

        self.update_level()


        # -------------------------------------------------
        # FINISH IF LAST QUESTION
        # -------------------------------------------------

        if (
            self.state.answered_questions
            >= self.state.total_questions
        ):

            self.finish()


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return {
            "result": result,

            "correct": answer_correct,

            "xp_gained": xp_gained,

            "score_gained": score_gained,

            "level": self.state.current_level,

            "difficulty_name": (
                self.get_current_level_name()
            ),

            "question_number": (
                self.state.current_question
            ),

            "remaining_questions": (
                self.get_remaining_questions()
            ),

            "progress": self.get_progress(),

            "finished": self.state.finished,

            "elapsed_time": round(
                self.elapsed_time(),
                3
            ),
        }


    # =====================================================
    # TIME
    # =====================================================

    def elapsed_time(self) -> float:

        if self.state.finished_at is not None:

            end_time = self.state.finished_at

        else:

            end_time = time.time()


        elapsed = (
            end_time
            - self.state.started_at
        )


        elapsed = max(
            0.0,
            elapsed
        )


        # Không cho thời gian game vượt quá
        # thời lượng tối đa.

        if elapsed > MAX_GAME_TIME:

            elapsed = MAX_GAME_TIME


        return elapsed


    def is_timeout(self) -> bool:

        if self.state.finished:

            return False

        elapsed = (
            time.time()
            - self.state.started_at
        )

        return (
            elapsed >= MAX_GAME_TIME
        )


    def get_remaining_time(self) -> float:

        if self.state.finished:

            remaining = (
                MAX_GAME_TIME
                - self.elapsed_time()
            )

        else:

            remaining = (
                MAX_GAME_TIME
                - self.elapsed_time()
            )

        return round(
            max(0.0, remaining),
            3
        )


    # =====================================================
    # FINISH
    # =====================================================

    def finish(self):

        if self.state.finished:

            return False

        self.state.finished = True

        self.state.finished_at = time.time()

        return True


    # =====================================================
    # FORCE TIMEOUT
    # =====================================================

    def timeout(self):

        if self.state.finished:

            return False

        self.finish()

        return True


    # =====================================================
    # RESULT
    # =====================================================

    def get_result(self) -> dict:

        if not self.state.finished:

            self.finish()


        elapsed = self.elapsed_time()


        total_answers = (
            self.state.correct
            + self.state.wrong
            + self.state.blank
        )


        accuracy = 0.0

        if total_answers > 0:

            accuracy = (
                self.state.correct
                / total_answers
            ) * 100


        return {
            "game_id": self.state.game_id,

            "user_id": self.state.user_id,

            "game_name": self.state.game_name,

            "topic_name": self.state.topic_name,

            "total": self.state.total_questions,

            "total_questions": (
                self.state.total_questions
            ),

            "answered_questions": (
                self.state.answered_questions
            ),

            "correct": self.state.correct,

            "wrong": self.state.wrong,

            "blank": self.state.blank,

            "score": self.state.score,

            "xp": self.state.xp,

            "accuracy": round(
                accuracy,
                2
            ),

            "time": round(
                elapsed,
                3
            ),

            "elapsed_time": round(
                elapsed,
                3
            ),

            "finished": self.state.finished,

            "difficulty": self.state.current_level,

            "difficulty_name": (
                self.get_current_level_name()
            ),
        }


    # =====================================================
    # PUBLIC STATE
    # =====================================================

    def get_public_state(self) -> dict:

        return {
            "game_id": self.state.game_id,

            "game_name": self.state.game_name,

            "topic_name": self.state.topic_name,

            "difficulty": self.state.current_level,

            "difficulty_name": (
                self.get_current_level_name()
            ),

            "total_questions": (
                self.state.total_questions
            ),

            "current_question": (
                self.state.current_question
            ),

            "answered_questions": (
                self.state.answered_questions
            ),

            "remaining_questions": (
                self.get_remaining_questions()
            ),

            "progress": self.get_progress(),

            "correct": self.state.correct,

            "wrong": self.state.wrong,

            "blank": self.state.blank,

            "score": self.state.score,

            "xp": self.state.xp,

            "elapsed_time": round(
                self.elapsed_time(),
                3
            ),

            "remaining_time": (
                self.get_remaining_time()
            ),

            "finished": self.state.finished,

            "can_submit": (
                self.can_submit_answer()
            ),
        }


    # =====================================================
    # SIMPLE STATISTICS
    # =====================================================

    def get_accuracy(self) -> float:

        answered = (
            self.state.correct
            + self.state.wrong
            + self.state.blank
        )

        if answered <= 0:

            return 0.0

        return round(
            (
                self.state.correct
                / answered
            ) * 100,
            2
        )


    def get_score(self) -> int:

        return self.state.score


    def get_xp(self) -> int:

        return self.state.xp


    def get_correct(self) -> int:

        return self.state.correct


    def get_wrong(self) -> int:

        return self.state.wrong


    def get_blank(self) -> int:

        return self.state.blank


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.state.current_level = "easy"

        self.state.current_question = 0

        self.state.correct = 0

        self.state.wrong = 0

        self.state.blank = 0

        self.state.score = 0

        self.state.xp = 0

        self.state.started_at = time.time()

        self.state.finished_at = None

        self.state.finished = False

        self.state.answered_questions = 0

        return self.get_public_state()


# =========================================================
# GAME FACTORY
# =========================================================

def create_game(
    game_id: str,
    user_id: int,
    game_name: str,
    topic_name: str,
    total_questions: int = DEFAULT_TOTAL_QUESTIONS,
) -> GameEngine:

    return GameEngine(
        game_id=game_id,
        user_id=user_id,
        game_name=game_name,
        topic_name=topic_name,
        total_questions=total_questions,
    )