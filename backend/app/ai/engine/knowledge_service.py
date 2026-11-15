import json
from pathlib import Path
from ..config import KNOWLEDGE_DIR

class KnowledgeService:
    # Game-only bank topics supported by B56/Word, not added to the 150-topic
    # public catalogue, to keep existing navigation IDs and counts stable.
    GAME_BANK_TOPICS = {
        "chia_du": {"id":"chia_du","name":"Chia dư","grade":10},
        "chia_het": {"id":"chia_het","name":"Chia hết","grade":10},
        "phuong_trinh_bac_hai": {"id":"phuong_trinh_bac_hai","name":"Phương trình bậc hai","grade":10},
    }
    GAME_TOPIC_ALIASES = {
        "probability": "xac_suat",
        "combination": "hoan_vi_chinh_hop_to_hop",
        "permutation": "hoan_vi_chinh_hop_to_hop",
        "function": "ham_so_bac_hai",
        "system-equation": "phuong_trinh_he",
        "system_equation": "phuong_trinh_he",
        "quadratic-equation": "phuong_trinh_bac_hai",
        "quadratic_equation": "phuong_trinh_bac_hai",
        "inequality": "bat_phuong_trinh",
        "sequence": "day_so",
        "divisibility": "chia_het",
        "remainder": "chia_du",
        "radical": "g10_radical_equations_advanced",
        "identities": "ham_so_bac_hai",
        "algebraic-fraction": "phuong_trinh",
        "geometry": "hinh_hoc_10",
        "statistics": "thong_ke",
    }

    def __init__(self):
        self.path = KNOWLEDGE_DIR / "index.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.by_id = {item["id"]: {**item, "grade": int(grade)} for grade, items in self.data.items() for item in items}
        # V61: grade-scoped Word title / file aliases; IDs remain authoritative.
        # Ambiguous labels (for instance the two different "Dãy số" topics)
        # are deliberately excluded from aliases to avoid wrong-topic questions.
        aliases_file = self.path.parent.parent / "storage" / "word_topic_aliases_v61.json"
        try:
            self.word_topic_aliases = json.loads(aliases_file.read_text(encoding="utf-8")).get("aliases", {})
        except (OSError, ValueError, TypeError):
            self.word_topic_aliases = {}

    def list_topics(self, grade: int | None = None):
        if grade is None:
            return self.data
        return self.data.get(str(grade), [])

    def get(self, topic_id: str):
        canonical=self.GAME_TOPIC_ALIASES.get(str(topic_id).casefold(),str(topic_id))
        return self.by_id.get(canonical) or self.GAME_BANK_TOPICS.get(canonical)

    def normalize_topics(self, grade: int, topics: list[str] | None):
        allowed = {x["id"] for x in self.list_topics(grade)}
        allowed.update(x for x, info in self.GAME_BANK_TOPICS.items() if info["grade"] == int(grade))
        if not topics:
            return list(allowed)
        result = []
        for topic in topics:
            # Legacy game IDs can be uppercase (SYSTEM_EQUATION) or have whitespace.
            # Only admit canonical IDs actually belonging to the requested grade.
            raw = str(topic).strip()
            folded = raw.casefold()
            canonical = self.GAME_TOPIC_ALIASES.get(folded, folded)
            if canonical not in allowed:
                canonical = self.word_topic_aliases.get(str(int(grade)), {}).get(folded, canonical)
            if canonical in allowed and canonical not in result:
                result.append(canonical)
        return result
