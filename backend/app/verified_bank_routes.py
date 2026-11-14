"""Isolated, opt-in verified question bank API. Does not change existing game or battle routes."""
import json
import hashlib
import sys
import re
import random
import secrets
import threading
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/verified-bank", tags=["Verified Bank"])
BANK_PATH = Path(__file__).resolve().parent / "ai" / "verified_seed" / "verified_seed_bank.jsonl"
_LOCK = threading.RLock()
_SESSIONS = {}
_TTL = 1800
_MAX_SESSIONS = 10000
_INDEX_LOCK = threading.RLock()
_INDEX_CACHE = None


def normalized_question(text):
    return " ".join(str(text).casefold().split())


def _assert_real_seed(path):
    """Reject an unresolved Git LFS pointer with a clear HTTP status.

    A GitHub Pages/Render deploy may contain the text pointer rather than the
    actual verified JSONL. That must never be counted as verified questions.
    """
    p=Path(path)
    if not p.is_file():
        raise HTTPException(503,"Ngân hàng verified chưa được tải lên máy chủ.")
    with p.open('rb') as f:
        header=f.read(120)
    if header.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise HTTPException(503,"Ngân hàng verified hiện chỉ có con trỏ Git LFS; cần tải tệp JSONL thật trước khi dùng.")


def audit_records(records):
    """Structural audit, not a claim of mathematical proof for arbitrary questions."""
    forms = defaultdict(list)
    issues = []
    seen_questions = set()
    for index, row in enumerate(records):
        key = (row["grade"], row["topic"], normalized_question(row["question"]))
        if key in seen_questions:
            issues.append({"row": index, "issue": "duplicate_question"})
        seen_questions.add(key)
        forms[(row["grade"], row["topic"], row["form_signature"])].append(row)
        if len(str(row.get("solution", "")).strip()) < 35:
            issues.append({"row": index, "issue": "short_solution"})
        if row.get("form_id") == "linear_isolate":
            proof = row.get("proof", {})
            try:
                a, b, c, x = (Fraction(str(proof[k])) for k in ("a", "b", "c", "x"))
                if a == 0 or a*x+b != c or not check_numeric_equivalence(row["answer"], str(x)):
                    issues.append({"row": index, "issue": "invalid_linear_proof"})
            except (KeyError, ValueError, ZeroDivisionError):
                issues.append({"row": index, "issue": "missing_linear_proof"})
    underfilled = [{"grade": g, "topic": t, "form_signature": signature, "count": len(rows)}
                   for (g,t,signature), rows in forms.items() if len(rows) < 10]
    return {"question_count": len(records), "form_count": len(forms),
            "forms_with_ten_questions": len(forms)-len(underfilled),
            "underfilled_forms": underfilled, "issues": issues,
            "scope": "structural_checks_and_linear_equation_proof_only",
            "fully_mathematically_verified": False}



def _indexed_bank(path=BANK_PATH):
    """Index offsets, not 344k parsed dictionaries, for fast public reads.

    The original JSONL remains authoritative and read-only. Rebuild after a
    file replacement; do not cache user answers or modify the bank on disk.
    """
    global _INDEX_CACHE
    path = Path(path)
    _assert_real_seed(path)
    stat = path.stat()
    identity = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    with _INDEX_LOCK:
        if _INDEX_CACHE is not None and _INDEX_CACHE['identity'] == identity:
            return _INDEX_CACHE
        by_topic = defaultdict(list)
        topic_display = {}
        forms = defaultdict(set)
        seen = set()
        offsets = []
        form_ids = {}
        with path.open('rb') as stream:
            while True:
                offset = stream.tell()
                line = stream.readline()
                if not line:
                    break
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    required = ('topic','grade','form_id','form_signature','question','answer','solution')
                    if any(not str(row.get(k,'')).strip() for k in required):
                        continue
                    grade = int(row['grade'])
                    topic = sys.intern(str(row['topic']))
                    topic_folded = topic.casefold()
                    normalized = normalized_question(row['question'])
                    unique = hashlib.blake2b(f'{grade}|{topic_folded}|{normalized}'.encode('utf-8'),digest_size=16).digest()
                    if unique in seen:
                        continue
                    seen.add(unique)
                    form_id = sys.intern(str(row['form_id']))
                    form_idx = form_ids.setdefault(form_id,len(form_ids))
                    item = (offset,form_idx)
                    offsets.append((grade,topic_folded,item))
                    by_topic[(grade,topic_folded)].append(item)
                    topic_display.setdefault((grade,topic_folded),topic)
                    forms[(grade,topic_folded)].add(str(row['form_signature']))
                except (ValueError,TypeError,KeyError,json.JSONDecodeError):
                    continue
        # Store only the small index, not all parsed questions/solutions.
        result = {'identity':identity,'by_topic':by_topic,'offsets':offsets,
                  'form_ids':form_ids,'forms':forms,'topic_display':topic_display,'count':len(offsets)}
        _INDEX_CACHE = result
        return result


def _read_indexed_question(offset, path=BANK_PATH):
    with Path(path).open('rb') as stream:
        stream.seek(offset)
        return json.loads(stream.readline())

@router.get("/quality")
def quality():
    return audit_records(load_bank())



def load_bank(path=BANK_PATH):
    _assert_real_seed(path)
    records = []
    seen = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            required = ("topic", "grade", "form_id", "form_signature", "question", "answer", "solution")
            if any(not str(row.get(k, "")).strip() for k in required):
                continue
            key = (str(row["grade"]), row["topic"], normalized_question(row["question"]))
            if key in seen:
                continue
            seen.add(key)
            records.append(row)
    return records


def check_numeric_equivalence(answer, expected):
    """Exact rational comparison for numeric answers, never float tolerance."""
    try:
        def parse(value):
            s = str(value).strip().replace(" ", "").replace(",", ".")
            if len(s) > 80 or not s:
                raise ValueError("invalid numeric expression")
            return Fraction(s)
        return parse(answer) == parse(expected)
    except (ValueError, ZeroDivisionError, OverflowError):
        return str(answer).strip().casefold() == str(expected).strip().casefold()


class Submit(BaseModel):
    session_id: str = Field(min_length=16, max_length=128)
    answer: str = Field(min_length=1, max_length=500)


@router.get("/catalog")
def catalog():
    index = _indexed_bank()
    topics = []
    for (grade, topic), rows in sorted(index['by_topic'].items()):
        signatures = index['forms'].get((grade, topic), set())
        display = index['topic_display'][(grade, topic)]
        topics.append({'grade':grade,'topic':display,'questions':len(rows),'forms':len(signatures)})
    return {'total_questions':index['count'],
            'distinct_forms':sum(len(v) for v in index['forms'].values()),
            'topics':topics,'target_met':False}


@router.get("/next")
def next_question(grade: int | None = None, topic: str | None = None, exclude_form: str | None = None):
    index = _indexed_bank()
    if grade is None and topic is None:
        candidates = [item for _,_,item in index['offsets']]
    else:
        folded = topic.strip().casefold() if topic is not None else None
        candidates = [item for (g,t),rows in index['by_topic'].items()
                      if (grade is None or grade == g) and (folded is None or folded == t)
                      for item in rows]
    if exclude_form:
        excluded = index['form_ids'].get(exclude_form)
        if excluded is not None:
            filtered = [item for item in candidates if item[1] != excluded]
            if filtered:
                candidates = filtered
    if not candidates:
        raise HTTPException(status_code=404, detail="Chưa có câu hỏi được kiểm duyệt cho bộ lọc này.")
    row = _read_indexed_question(random.SystemRandom().choice(candidates)[0])
    sid = secrets.token_urlsafe(24)
    now = time.time()
    with _LOCK:
        for key, entry in list(_SESSIONS.items()):
            if entry['created'] < now - _TTL:
                del _SESSIONS[key]
        if len(_SESSIONS) >= _MAX_SESSIONS:
            oldest = min(_SESSIONS, key=lambda k: _SESSIONS[k]['created'])
            del _SESSIONS[oldest]
        _SESSIONS[sid] = {'row':row,'created':now}
    return {'session_id':sid,'grade':row['grade'],'topic':row['topic'],
            'form_id':row['form_id'],'question':row['question'],
            'expires_in_seconds':_TTL}


@router.post("/answer")
def submit_answer(payload: Submit):
    with _LOCK:
        entry = _SESSIONS.pop(payload.session_id, None)
    if not entry or time.time() - entry["created"] > _TTL:
        raise HTTPException(status_code=404, detail="Phiên không tồn tại, hết hạn hoặc đã được chấm.")
    row = entry["row"]
    correct = check_numeric_equivalence(payload.answer, row["answer"])
    return {"is_correct": correct, "correct_answer": row["answer"], "solution": row["solution"], "feedback": "Chính xác. Hãy đối chiếu các bước giải." if correct else "Chưa đúng. Xem các bước giải và thử một câu tương tự.", "grading_scope": "numeric_or_exact_text_only", "form_id": row["form_id"]}
