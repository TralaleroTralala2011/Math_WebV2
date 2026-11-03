import hashlib
import re
from .validator import fingerprint

_NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:[\.,/]\d+)?")
_SPACE = re.compile(r"\s+")


def structure_fingerprint(question: str, template_family: str = "", generation_style: str = "") -> str:
    """Fingerprint the problem structure, not only its exact wording.

    Numeric values are normalized so the engine treats the same skeleton with
    different numbers as a repeat. Template family/style are retained so two
    genuinely different task types can coexist.
    """
    text = str(question or "").lower().strip()
    text = _NUMBER.sub("#", text)
    text = re.sub(r"[a-z]\s*[_₀-₉]*", "v", text)
    text = _SPACE.sub(" ", text)
    raw = f"{template_family}|{generation_style}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def is_duplicate(question: str, seen: set[str]) -> bool:
    return fingerprint(question) in seen
