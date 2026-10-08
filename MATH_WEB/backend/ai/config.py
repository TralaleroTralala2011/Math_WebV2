from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

QUESTION_TYPES = ("multiple_choice", "true_false", "short_answer")
DIFFICULTIES = ("easy", "medium", "hard", "expert")

MAX_TOPICS = 5
MAX_COUNT = 50
QUESTION_TTL_SECONDS = 3600
MAX_HISTORY = 100
