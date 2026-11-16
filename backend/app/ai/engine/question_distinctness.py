"""Conservative identity of a *mathematical exercise type*, not an answer or ID.

Replacing numeric constants never creates a new type within a topic play run.
This is intentionally conservative: uncertain / nearly identical prompts are
rejected rather than shown twice. It is not a proof of mathematical novelty.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter

_STOP = set('cho hay tim tinh la cua trong voi mot cac va so duoc bao nhieu nao tu sau sau day ket qua gia tri biet rang neu thuoc xac dinh dung sai bai toan cau hoi lua chon phuong an'.split())
_NUMBER = re.compile(r'(?<![a-zA-Z])[-+]?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?(?:[eE][-+]?\d+)?')
_PREFIX = re.compile(r'^\s*(?:cau\s*(?:hoi\s*)?(?:so\s*)?\d+\s*[:.\-)]+\s*|kiem\s*tra\s*kien\s*thuc\s*[:：]\s*|sau\s*khi\s*phan\s*tich\s*du\s*kien\s*[,：]\s*)', re.I)


def clean(value: object) -> str:
    value = unicodedata.normalize('NFKC', str(value or '')).casefold()
    value = ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    value = value.replace('−', '-').replace('–', '-').replace('×', '*').replace('÷', '/')
    value = re.sub(r'\s+', ' ', value).strip()
    return _PREFIX.sub('', value)


def numeric_shape(value: object) -> str:
    text = _NUMBER.sub(' # ', clean(value))
    text = re.sub(r'[^a-z#\^+*/<>=!-]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _digest(value: object) -> str:
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


def _form(q: dict) -> str:
    # A reviewed Word form_id groups numeric variants of the same form.
    value = str(q.get('form_id') or '').strip()
    if not value or value.casefold() in ('none', 'null', 'unknown'):
        return ''
    return value.casefold()


def _family(q: dict) -> str:
    value = str(q.get('template_family') or '').strip().casefold()
    # IDs constructed from individual database rows do NOT identify a form.
    if not value or re.match(r'^(?:v254_|admin_bank_)\d+$', value):
        return ''
    return value


def claim_keys(q: dict) -> tuple[str, ...]:
    text = q.get('question') or q.get('text') or ''
    if not str(text).strip():
        return ()
    keys = ['exact:' + _digest(clean(text)), 'shape:' + _digest(numeric_shape(text))]
    if _form(q):
        keys.append('form:' + _digest(_form(q)))
    if _family(q):
        keys.append('family:' + _digest(_family(q)))
    return tuple(keys)


def _tokens(value: object) -> Counter:
    shape = numeric_shape(value)
    tokens = re.findall(r'[a-z]+', shape)
    return Counter(t for t in tokens if len(t) > 1 and t not in _STOP)


def same_mathematical_type(a: dict, b: dict) -> bool:
    """Reject exact, number-swapped, named-form, and strong paraphrase matches.

    Similarity is deliberately limited to high-overlap prompts: distant
    paraphrases cannot be proven equivalent automatically and need bank audit.
    """
    ta = a.get('question') or a.get('text') or ''
    tb = b.get('question') or b.get('text') or ''
    if not str(ta).strip() or not str(tb).strip():
        return False
    if clean(ta) == clean(tb) or numeric_shape(ta) == numeric_shape(tb):
        return True
    if _form(a) and _form(a) == _form(b):
        return True
    if _family(a) and _family(a) == _family(b):
        return True
    aa, bb = _tokens(ta), _tokens(tb)
    union = sum((aa | bb).values())
    intersection = sum((aa & bb).values())
    # Only strong evidence; avoid equating all remainder exercises simply
    # because they share words "chia" and "du".
    if union >= 7 and intersection >= 5 and intersection / union >= 0.80:
        return True
    return False
