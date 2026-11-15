"""Stable prompt identity shared by Practice, Battle and imported Word banks.

Normalizes visible formatting only. It never treats numerically different
exercises as identical and makes no claim of mathematical equivalence.
"""
from __future__ import annotations
import hashlib
import re
import unicodedata


def normalize_question_text(value: object) -> str:
    text = unicodedata.normalize('NFKC', str(value or ''))
    text = text.replace('\u200b','').replace('\u2060','').replace('\u00a0',' ')
    text = text.replace('−','-').replace('–','-')
    text = re.sub(r'^\s*Câu\s*(?:hỏi\s*)?(?:số\s*)?\d+\s*[.:·\-]\s*', '', text, flags=re.I)
    text = re.sub(r'\s*([=+*/;(),?:])\s*', r'\1',text)
    return ' '.join(text.casefold().split()).strip(' .')


def question_key(value: object) -> str:
    return hashlib.sha256(normalize_question_text(value).encode('utf8')).hexdigest()
