import time
import uuid

from ..config import MAX_COUNT, MAX_HISTORY, MAX_TOPICS, QUESTION_TTL_SECONDS
from .adaptive import next_difficulty
from .difficulty import normalize
from .feedback import message
from .generator import QuestionGenerator
from .knowledge_service import KnowledgeService
from .solver import equivalent
from .validator import ValidationError, validate


class QuestionStore:
    def __init__(self):
        self.items = {}

    def put(self, question):
        self.items[question["id"]] = (time.time(), question)

    def get(self, question_id):
        item = self.items.get(question_id)
        if not item:
            return None
        if time.time() - item[0] > QUESTION_TTL_SECONDS:
            self.items.pop(question_id, None)
            return None
        return item[1]

    def cleanup(self):
        now = time.time()
        for key, (created, _) in list(self.items.items()):
            if now - created > QUESTION_TTL_SECONDS:
                self.items.pop(key, None)


class AIQuestionService:
    def __init__(self):
        self.knowledge = KnowledgeService()
        self.generator = QuestionGenerator(self.knowledge)
        self.store = QuestionStore()

    def topics(self, grade=None):
        return self.knowledge.list_topics(grade)

    def generate_one(self, grade, topic_id, difficulty="medium", question_type="multiple_choice", seen=None):
        if self.knowledge.get(topic_id) is None:
            raise ValueError("Unknown topic")
        seen = seen or set()
        last_error = None
        for _ in range(30):
            question = self.generator.generate(grade, topic_id, normalize(difficulty), question_type)
            try:
                validate(question)
            except ValidationError as exc:
                last_error = exc
                continue
            if question["fingerprint"] in seen:
                continue
            self.store.put(question)
            return question
        raise RuntimeError(f"Could not generate a unique valid question: {last_error}")

    @staticmethod
    def public_question(question):
        """Chỉ trả dữ liệu cần cho client, tuyệt đối không trả answer/solution."""
        public = {
            "id": question["id"],
            "grade": question["grade"],
            "topic": question["topic"],
            "difficulty": question["difficulty"],
            "question_type": question["question_type"],
            "question": question["question"],
            "knowledge_name": question.get("knowledge_name", ""),
        }
        if question["question_type"] == "multiple_choice":
            public["options"] = question["options"]
        elif question["question_type"] == "true_false":
            public["statements"] = question["statements"]
        return public

    def generate_set(self, grade, topics, count, difficulty="medium", question_type="multiple_choice", history=None):
        if count < 1 or count > MAX_COUNT:
            raise ValueError("count out of range")
        if question_type not in ("multiple_choice", "true_false", "short_answer"):
            raise ValueError("invalid question_type")

        topics = self.knowledge.normalize_topics(grade, topics)[:MAX_TOPICS]
        if not topics:
            raise ValueError("No valid topics")

        history = (history or [])[:MAX_HISTORY]
        current = next_difficulty(history, normalize(difficulty))
        private_questions = []
        seen = set()

        for index in range(count):
            topic_id = topics[index % len(topics)]
            level = current
            if count >= 8 and index >= int(count * 0.65):
                level = {"easy": "medium", "medium": "hard", "hard": "expert", "expert": "expert"}[current]
            question = self.generate_one(grade, topic_id, level, question_type, seen)
            seen.add(question["fingerprint"])
            private_questions.append(question)

        return {
            "set_id": uuid.uuid4().hex,
            "mode": "practice",
            "grade": grade,
            "topics": topics,
            "difficulty": current,
            "count": len(private_questions),
            "questions": [self.public_question(q) for q in private_questions],
        }

    def answer(self, question_id, user_answer):
        question = self.store.get(question_id)
        if not question:
            raise KeyError("question_expired_or_not_found")

        correct = self._check(question, user_answer)
        result = {
            "question_id": question_id,
            "correct": correct,
            "feedback": message(correct),
        }
        if not correct:
            result["correct_answer"] = question["answer"]
            result["solution"] = question["solution"]
        else:
            result["correct_answer"] = None
            result["solution"] = None
        return result

    def _check(self, question, user_answer):
        t = question["question_type"]
        if t == "multiple_choice":
            return str(user_answer).strip() == str(question["answer"]).strip()
        if t == "short_answer":
            return equivalent(user_answer, question["answer"])
        if t == "true_false":
            if not isinstance(user_answer, list) or len(user_answer) != 4:
                return False
            return [bool(x) for x in user_answer] == question["statement_answers"]
        return False

    def battle_topics(self, player_topics, opponent_topics):
        a = [x for x in player_topics or [] if self.knowledge.get(x)]
        b = {x for x in opponent_topics or [] if self.knowledge.get(x)}
        return [x for x in dict.fromkeys(a) if x in b][:MAX_TOPICS]
