"""Conservative, explainable topic-content gate for known mislabeled question sets.

A bank row's `topic` and Word filename only assert *metadata*, not that the
exercise actually tests that skill.  For the audited geometry topic, reject
unrelated exercises even if the source mistakenly assigns its topic ID.

Unknown/unreviewed topics intentionally retain their pre-existing behavior.
This gate makes no claim of independently verifying mathematical answers.
"""
from __future__ import annotations

import re
import unicodedata

# Keep rules exact and auditable. Broad generic geometry words such as 'tam giác',
# 'song song', 'diện tích' are NOT sufficient evidence for this topic.
_TOPIC = 'g10_geom_quadrilaterals_properties'
_MAIN = re.compile(r'\b(?:hinh binh hanh|hinh thoi)\b')
_QUADRILATERAL = re.compile(r'\btu giac\b')
_CHARACTERISTIC = re.compile(
    r'\b(?:duong cheo|canh doi|goc doi|hai cap canh|trung diem|song song|bang nhau)\b'
)


def _plain(value: object) -> str:
    raw = unicodedata.normalize('NFKD', str(value or '').casefold())
    # Vietnamese đ is not split by Unicode NFKD.
    raw = raw.replace('đ', 'd')
    return ' '.join(''.join(ch if (ch.isalnum() or ch.isspace()) else ' '
                            for ch in raw if not unicodedata.combining(ch)).split())


def is_question_on_topic(topic: str, question: object) -> bool:
    """Fail closed for the specifically audited topic; otherwise non-destructive.

    This deliberately does not classify a problem as appropriate just because
    it was saved inside the right Word file / stored with the right topic ID.
    """
    body = _plain(question)
    if not body:
        return False
    if topic != _TOPIC:
        return True
    if _MAIN.search(body):
        return True
    # E.g. "Hai đường chéo của tứ giác có trung điểm khác nhau. Có phải
    # là hình bình hành?" Includes a discriminating quadrilateral property.
    return bool(_QUADRILATERAL.search(body) and _CHARACTERISTIC.search(body))


def audited_topic_ids() -> tuple[str, ...]:
    return (_TOPIC,)
