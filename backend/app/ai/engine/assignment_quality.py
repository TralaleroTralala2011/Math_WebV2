"""Fail-closed, source-faithful question selection for AI TẬP HỌC.

This module deliberately does NOT generate extra problems, change numerical data,
claim Word candidates are proof-verified, or silently reduce the assigned count.
"""
from __future__ import annotations

from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
import io
import zipfile
import json
import re
import sqlite3
import unicodedata
from contextlib import closing

from .word_source_v62 import ensure_word_source
from .topic_relevance import is_question_on_topic

_FAKE = (
    'mệnh đề thứ hai được suy ra trực tiếp từ đề',
    'đáp án bằng một giá trị khác',
    'cách giải trên không cần dùng dữ kiện',
    'đúng; 11 sai;',
)
_INLINE_NUM = re.compile(r'\d+(?:[.,]\d+)?')
_PREFIX = re.compile(r'^\s*\|?\s*\d{3}-[A-Z0-9-]+\s+', flags=re.I)
_ANSWER_TYPE_ALIASES = {'mcq':'multiple_choice', 'choice':'multiple_choice', 'trac_nghiem':'multiple_choice',
                        'tu_luan':'short_answer', 'short':'short_answer', 'essay':'short_answer'}


def normalize_type(value):
    return _ANSWER_TYPE_ALIASES.get(str(value or 'mixed').strip().lower(), str(value or 'mixed').strip().lower())


def _plain(s):
    value=unicodedata.normalize('NFKC', str(s or '')).casefold()
    return ' '.join(value.split())


def content_signature(text):
    """Conservative repeat filter: numeric substitutions and document IDs cannot create new types."""
    text=_PREFIX.sub('', _plain(text))
    text=_INLINE_NUM.sub('#',text)
    text=re.sub(r'\s+', ' ', text)
    return re.sub(r'[^\w\s#≤≥<>+=()−÷×/]', '',text)


def math_method_family(topic, question):
    """Conservative, topic-specific grouping when Word form_id is missing.

    Crucial: different shopping narratives or new coefficients are NOT new
    methods for the same operation (such as enumerating feasible integer pairs).
    This is a conservative filter, not a proof of mathematical independence.
    """
    q=_plain(question)
    if topic=='he_bat_phuong_trinh':
        if any(t in q for t in ('có bao nhiêu','bao nhiêu cặp','bao nhiêu nghiệm','bao nhiêu cách','bao nhiêu kế hoạch','bao nhiêu phương án','đếm')):
            return 'count_integer_feasible_pairs'
        if any(t in q for t in ('hợp lệ','kiểm tra','có thỏa','thuộc miền nghiệm','có chứa điểm','có thuộc','phương án x=')):
            return 'check_feasible_point'
        if any(t in q for t in ('hệ điều kiện nào', 'viết bất phương trình','viết hệ bất phương trình')):
            return 'model_linear_constraints'
        if any(t in q for t in ('giá trị lớn nhất', 'giá trị nhỏ nhất','tối ưu')):
            return 'linear_optimization'
        if any(t in q for t in ('tìm điểm nguyên', 'tìm nghiệm nguyên')):
            return 'find_integer_solution'
        if 'giao của hai nửa mặt phẳng' in q:
            return 'intersect_halfplanes'
    return None


def is_repeated_signature(new, previous):
    if not new: return True
    if new in previous: return True
    # Near-identical wordings with number changes or small phrases.
    # Very short prompts are handled through exact normalized templates only.
    return any(len(new)>65 and len(old)>65 and SequenceMatcher(None,new,old).ratio()>0.91 for old in previous)


def _relevant(grade,topic,text):
    if not is_question_on_topic(topic,text): return False
    q=_plain(text)
    if str(topic)=='he_bat_phuong_trinh':
        # The supplied Word collection includes single-variable inequalities and
        # unrelated distribution examples under this ID. This grade-10 topic
        # concerns systems of inequalities in two variables.
        if grade!=10: return False
        return bool(re.search(r'(?<![a-z])x(?![a-z])',q) and
                    re.search(r'(?<![a-z])y(?![a-z])',q) and
                    (any(v in q for v in ('≥','≤','<','>','ít nhất','không quá','tối đa','hợp lệ','vùng nghiệm','miền nghiệm','nửa mặt phẳng','điều kiện','ngân sách'))))
    return True


WORD_SOURCE_ARCHIVE = Path(__file__).resolve().parents[1] / 'storage' / '150_CHU_DE_WORD_ORIGINAL_20261116.zip'


@lru_cache(maxsize=18)
def _word_prompts_exact(source_word: str):
    """Extract only literal exercise lines from a user's supplied Word document.

    No paraphrasing, number replacements, synthetic prompts, or guessed topics.
    Missing/corrupt Word files fail closed rather than silently falling back to AI.
    """
    if not source_word.startswith('150_CHU_DE_WORD/') or not source_word.endswith('.docx'):
        return frozenset()
    if '..' in source_word or '\\' in source_word:
        return frozenset()
    try:
        from docx import Document
        with zipfile.ZipFile(WORD_SOURCE_ARCHIVE) as z:
            data=z.read(source_word)
        doc=Document(io.BytesIO(data))
        paragraphs=[p.text.strip() for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.extend(p.text.strip() for p in cell.paragraphs)
    except (OSError,KeyError,ValueError,zipfile.BadZipFile,ImportError):
        return frozenset()
    prompts=[]
    for line in paragraphs:
        if line.startswith('Đề bài:'):
            prompts.append(line[len('Đề bài:'):].strip())
        elif line.startswith('Câu hỏi:'):
            prompts.append(line[len('Câu hỏi:'):].strip())
        else:
            match=re.match(r'^Câu\s+\d+[.:]\s*(\S.*)$',line,flags=re.I)
            if match:
                prompts.append(match.group(1).strip())
    return frozenset(prompts)


def clean_candidate(row, grade, topic, requested_kind):
    """None if invalid; otherwise original Word prompt/answer, without rewriting."""
    # Legacy v62 importer attached the source item ID ('| 019-B20-01-Q01')
    # to some prompts. It is a Word heading, NOT part of the 'Đề bài:' line.
    text=_PREFIX.sub('',str(row['question'] or ''))
    answer=str(row['answer'] or '').strip()
    solution=str(row['solution'] or '').strip()
    source_word=str(row['source_word'] or '')
    if not 8<=len(text)<=5000 or not answer or len(answer)>2000 or not solution:
        return None
    if any(x in _plain(text+' '+answer) for x in _FAKE):return None
    if not source_word.endswith('.docx'):return None
    if text not in _word_prompts_exact(source_word):return None
    if not _relevant(grade,topic,text):return None
    try: options=json.loads(row['options'] or '[]')
    except (ValueError,TypeError):options=[]
    raw_type=normalize_type(row['question_type'])
    if raw_type=='multiple_choice':
        if not (isinstance(options,list) and len(options)==4 and all(isinstance(x,str) and x.strip() for x in options)):
            return None
        if len({_plain(o) for o in options})!=4:return None
        if any(any(p in _plain(o) for p in _FAKE) for o in options):return None
        from app.questions.answer_checker import _choice
        if _choice(answer,options) is None:return None
        kind='multiple_choice'
    elif raw_type=='short_answer':
        # A word entry labelled MCQ but without options is not a valid MCQ.
        kind='short_answer';options=[]
    else:
        return None
    if requested_kind not in ('mixed',kind):return None
    # The source group 019-B20-01-Q06 mistakenly allows arbitrarily negative y,
    # so its claimed finite answer is invalid. Exclude this audited source row.
    if topic=='he_bat_phuong_trinh' and row['id']=='word62_019_0016':return None
    return {'question':text, 'options':options, 'answer':answer, 'correct_answer':answer,
            'solution':solution, 'explanation':solution, 'question_type':kind,
            'difficulty':str(row['difficulty']), 'source':'150_CHU_DE_WORD',
            'source_word':source_word,'source_id':row['id'], 'word_question_number':row['source_question_number'],
            'quality_status':'word_original_candidate_topic_screened'}


def eligible_assignment_questions(grade, topic, difficulty, kind='mixed', cap=200):
    """Only exact-grade/topic/level originals, filtered for displayability and type diversity."""
    grade=int(grade);topic=str(topic);difficulty=str(difficulty).casefold()
    kind=normalize_type(kind)
    levels={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard','chuyên sâu':'expert'}
    difficulty=levels.get(difficulty,difficulty)
    if grade not in (10,11,12) or not topic or kind not in ('mixed','short_answer','multiple_choice','true_false'):
        return []
    if kind=='true_false':return []  # No verified native Word T/F format in this source index.
    path=ensure_word_source()
    if path is None:return []
    # Do not relax difficulty, topic or question count silently.
    with closing(sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True,timeout=5)) as conn:
        conn.row_factory=sqlite3.Row
        rows=conn.execute('''SELECT id,question,answer,solution,options,question_type,difficulty,
                            source_word,source_question_number
                            FROM questions WHERE grade=? AND topic=? AND difficulty=?
                            ORDER BY id''',(grade,topic,difficulty)).fetchall()
    candidates=[];seen=[];seen_methods=set()
    for row in rows:
        item=clean_candidate(row,grade,topic,kind)
        if item is None:continue
        signature=content_signature(item['question'])
        method=math_method_family(topic,item['question'])
        if method and method in seen_methods:continue
        if is_repeated_signature(signature,seen):continue
        if method:seen_methods.add(method)
        seen.append(signature)
        item['shape_signature']=signature
        candidates.append(item)
        if len(candidates)>=cap:break
    return candidates


def validate_cached_assignment(questions,grade,topic,difficulty,kind='mixed'):
    """Reject stale AI-generated, off-topic, malformed, or repeated saved homework."""
    if not isinstance(questions,list) or not questions:return False
    kind=normalize_type(kind)
    eligible={q['source_id']:(q['question'],q['answer']) for q in eligible_assignment_questions(grade,topic,difficulty,kind,cap=500)}
    seen=set()
    for q in questions:
        if not isinstance(q,dict):return False
        source_id=q.get('source_id')
        if not source_id or source_id not in eligible:return False
        if (q.get('question'),str(q.get('answer',q.get('correct_answer'))))!=eligible[source_id]:return False
        sign=content_signature(q.get('question'))
        if sign in seen:return False
        seen.add(sign)
        if q.get('question_type')=='multiple_choice' and (not isinstance(q.get('options'),list) or len(q['options'])!=4):return False
    return True


def assignment_bank_matrix(grade, topic):
    """Eligible source-backed question counts; not a mathematical certification."""
    levels = {}
    for level in ('easy', 'medium', 'hard', 'expert'):
        by_type = {kind: eligible_assignment_questions(grade, topic, level, kind, cap=500)
                   for kind in ('mixed', 'multiple_choice', 'short_answer')}
        levels[level] = {'mixed_distinct': len(by_type['mixed']),
                         'multiple_choice': len(by_type['multiple_choice']),
                         'short_answer': len(by_type['short_answer']),
                         'true_false': 0,
                         'sample_source_ids': [q['source_id'] for q in by_type['mixed'][:5]]}
    return {'grade': int(grade), 'topic': str(topic), 'levels': levels,
            'source': '150_CHU_DE_WORD', 'verified_math_answers': False,
            'policy': 'Never fill shortages with generated or number-substituted questions.'}
