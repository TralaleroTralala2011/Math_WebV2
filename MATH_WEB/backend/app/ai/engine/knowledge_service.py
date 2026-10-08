import json
from pathlib import Path
from ..config import KNOWLEDGE_DIR

class KnowledgeService:
    GAME_TOPIC_ALIASES = {
        "probability": "xac_suat",
        "combination": "hoan_vi_chinh_hop_to_hop",
        "permutation": "hoan_vi_chinh_hop_to_hop",
        "function": "ham_so_bac_hai",
        "system-equation": "phuong_trinh_he",
        "quadratic-equation": "phuong_trinh_he",
        "inequality": "bat_phuong_trinh",
        "sequence": "day_so",
        "divisibility": "menh_de_tap_hop",
        "remainder": "menh_de_tap_hop",
        "radical": "menh_de_tap_hop",
        "identities": "menh_de_tap_hop",
        "algebraic-fraction": "menh_de_tap_hop",
        "geometry": "menh_de_tap_hop",
        "statistics": "thong_ke",
    }

    def __init__(self):
        self.path = KNOWLEDGE_DIR / "index.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.by_id = {item["id"]: {**item, "grade": int(grade)} for grade, items in self.data.items() for item in items}

    def list_topics(self, grade: int | None = None):
        if grade is None:
            return self.data
        return self.data.get(str(grade), [])

    def get(self, topic_id: str):
        return self.by_id.get(topic_id) or self.by_id.get(self.GAME_TOPIC_ALIASES.get(topic_id, topic_id))

    def normalize_topics(self, grade: int, topics: list[str] | None):
        allowed = {x["id"] for x in self.list_topics(grade)}
        if not topics:
            return list(allowed)
        result = []
        for topic in topics:
            alias = self.GAME_TOPIC_ALIASES.get(topic)
            canonical = alias or topic
            if canonical in allowed or alias is not None:
                if canonical not in result:
                    result.append(canonical)
        return result
