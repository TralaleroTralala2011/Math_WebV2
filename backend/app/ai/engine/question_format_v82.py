"""Presentation-only normalization of *verifiable* binary divisibility items.

Never modify Word/SQLite files. Only rewrite recognized encoded prompt patterns
when the saved answer agrees with independently computed integer arithmetic.
Unrecognized coded prompts are held back for review rather than guessed.
"""
import re
from typing import Any

_DIVISIBLE = re.compile(
    r'^\s*Hỏi\s+([+-]?\d{1,15})\s+có\s+chia\s+hết\s+cho\s+([+-]?\d{1,15})'
    r'\s+không\s*\?\s*Mã\s*1\s*nếu\s*có\s*,\s*0\s*nếu\s*không\s*\.?\s*$', re.I
)
_CLAIM = re.compile(
    r'^\s*ĐÚNG\s*/\s*SAI\s*:\s*Hỏi\s+([+-]?\d{1,15})\s+có\s+chia\s+hết\s+cho\s+([+-]?\d{1,15})'
    r'\s+không\s*\?\s*Mã\s*1\s*nếu\s*có\s*,\s*0\s*nếu\s*không\s*\.\s*'
    r'Một\s+học\s+sinh\s+(?:trả\s+lời\s*:\s*|đưa\s+ra\s+kết\s+quả\s+)([012])\s*\.'
    r'\s*(?:(?:Nhận\s+định\s+này|Khẳng\s+định\s+đó)\s+đúng\s+hay\s+sai\s*\?)?\s*$', re.I
)
_CODED_DIVISION = re.compile(r'\bMã\s*1\s*nếu\s*có\s*,\s*0\s*nếu\s*không\b', re.I)


def adapt_question(q: dict[str, Any]) -> dict[str, Any] | None:
    raw = str(q.get('question') or '')
    standard = _DIVISIBLE.fullmatch(raw)
    claim = _CLAIM.fullmatch(raw) if not standard else None
    match = standard or claim
    if not match:
        return None if _CODED_DIVISION.search(raw) else q
    try:
        numerator, divisor = int(match.group(1)), int(match.group(2))
    except ValueError:
        return None
    if divisor == 0:
        return None
    quotient, remainder = divmod(numerator, divisor)
    divisible = remainder == 0
    original = str(q.get('answer') or '').strip()

    if standard:
        if original not in ('0', '1') or (original == '1') != divisible:
            return None
        displayed = f'{numerator} có chia hết cho {divisor} không?'
        correct = 'Đúng' if divisible else 'Sai'
        reasoning = ('Số dư bằng 0 nên chia hết.' if divisible
                     else f'Số dư bằng {remainder} khác 0 nên không chia hết.')
    else:
        claimed_code = int(match.group(3))
        actual_code = 1 if divisible else 0
        correct = 'Đúng' if claimed_code == actual_code else 'Sai'
        if original.casefold() != correct.casefold():
            return None  # Do not silently override a mismatching Word answer.
        displayed = (f'Một học sinh chọn mã {claimed_code} cho câu hỏi: '
                     f'“{numerator} có chia hết cho {divisor} không?” '
                     'Bạn ấy trả lời đúng hay sai?')
        reasoning = (f'Số dư là {remainder}, nên mã chính xác phải là {actual_code}. '
                     f'Học sinh chọn {claimed_code}; vì thế nhận định {correct.lower()}.')

    result = dict(q)
    result['source_question_original'] = raw
    result['source_answer_original'] = original
    result['source_options_original'] = list(q.get('options') or [])
    result['question'] = displayed
    result['question_type'] = 'true_false'
    result['answer_mode'] = 'binary_boolean'
    result['answer'] = correct
    result['options'] = ['Đúng', 'Sai']
    result.pop('statements', None)
    result.pop('statement_answers', None)
    result['solution'] = (f'{numerator} = {divisor} × ({quotient}) + {remainder}. '
                          f'{reasoning} Vì vậy chọn {correct}.')
    result['explanation'] = result['solution']
    return result
