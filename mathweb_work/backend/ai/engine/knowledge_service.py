import json
from ..config import KNOWLEDGE_DIR


class KnowledgeService:
    def __init__(self):
        path = KNOWLEDGE_DIR / "index.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.data = raw
        self.by_id = {
            topic["id"]: {**topic, "grade": int(grade)}
            for grade, topics in raw.items()
            for topic in topics
        }

    def list_topics(self, grade=None):
        if grade is None:
            return self.data
        return self.data.get(str(grade), [])

    def get(self, topic_id):
        return self.by_id.get(str(topic_id).strip())

    def normalize_topics(self, grade, topics):
        allowed = {x["id"] for x in self.list_topics(grade)}
        result = []
        for topic in topics or []:
            topic = str(topic).strip()
            if topic in allowed and topic not in result:
                result.append(topic)
        return result[:5]

    def common_topics(self, a, b, grade=None):
        a = self.normalize_topics(grade, a) if grade else list(dict.fromkeys(a or []))
        b = set(self.normalize_topics(grade, b) if grade else list(dict.fromkeys(b or [])))
        return [x for x in a if x in b][:5]
