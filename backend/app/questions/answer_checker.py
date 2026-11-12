"""Shared type-aware answer grading for practice and Battle."""
import re

def canonical_type(question):
    t = str(question.get("question_type") or question.get("type") or "multiple_choice").strip().lower()
    return {"mcq":"multiple_choice", "choice":"multiple_choice", "multiple-choice":"multiple_choice", "short":"short_answer", "input":"short_answer", "short-answer":"short_answer", "tf":"true_false", "true-false":"true_false"}.get(t,t)

def _truth(v):
    if isinstance(v,bool): return v
    if isinstance(v,(int,float)) and v in (0,1): return bool(v)
    s=str(v).strip().casefold()
    if s in ("true","đúng","dung","1","t","yes"): return True
    if s in ("false","sai","0","f","no"): return False
    return None

def _option_text(option):
    if isinstance(option, dict):
        return str(option.get("text", option.get("value", option.get("label", "")))).strip()
    return str(option).strip()


def _choice(v, options):
    """Resolve a submitted choice to a zero-based index, if unambiguous.

    Numeric JSON indices are zero-based; a string such as "2" is the *visible
    answer text* when an option is literally 2, never silently index 2.
    """
    if isinstance(v, dict):
        if "index" in v:
            index = v["index"]
            return index if isinstance(index, int) and not isinstance(index, bool) and 0 <= index < len(options) else None
        v = v.get("value", v.get("answer", v.get("label")))
    if isinstance(v, int) and not isinstance(v, bool):
        return v if 0 <= v < len(options) else None
    if v is None or isinstance(v, bool):
        return None
    s = str(v).strip()
    if not s:
        return None
    # The user interface sends visible answer text or an A-D label.
    texts = [_option_text(option) for option in options]
    # First respect case-sensitive mathematical symbols such as R and r.
    strict = [i for i,text in enumerate(texts) if s == text]
    if len(strict) == 1:return strict[0]
    if len(strict) > 1:return None
    exact = [i for i, text in enumerate(texts) if s.casefold() == text.casefold()]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None
    m = re.fullmatch(r"(?:option[_ ]?)?([A-Da-d])(?:[.)])?", s)
    if m and len(options) == 4:
        return ord(m.group(1).upper()) - 65
    # Numeric expressions may be equivalent without identical strings:
    # 0.5 and 1/2 are the same answer. Ambiguous bank entries are rejected.
    from ..ai.engine.validator import options_equivalent
    matches = [i for i, text in enumerate(texts) if options_equivalent(s, text)]
    return matches[0] if len(matches) == 1 else None


def _composite_verdict_number(value):
    """Parse a two-part true/false + numeric answer without executing expressions.

    Accepted: 'Sai, 90', 'Không đúng; kết quả là 90',
    'Sai; 9(7+3)=90'. Rejects extra contradictory numbers.
    """
    import unicodedata
    if not isinstance(value, str) or len(value) > 300:
        return None
    folded = ''.join(c for c in unicodedata.normalize('NFD', value.casefold()) if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    negative = bool(re.search(r'\b(?:sai|khong\s+dung|false)\b', folded))
    positive = bool(re.search(r'\b(?:dung|chinh\s+xac|true)\b', re.sub(r'khong\s+dung', '', folded)))
    if negative == positive:
        return None
    # Explicit final result only; intermediate expressions are not graded by their numbers.
    tail = re.search(r'(?:=|la|bang|ket\s+qua\s+la)\s*([-+]?\d+(?:[.,]\d+)?)\s*$', folded)
    if tail is None:
        tail = re.search(r'[,;:]\s*([-+]?\d+(?:[.,]\d+)?)\s*$', folded)
    if tail is None:
        return None
    return (not negative, float(tail.group(1).replace(',', '.')))

def grade_answer(question, submitted, correct=None):
    t=canonical_type(question)
    if correct is None: correct=question.get("correct_answer",question.get("answer"))
    if correct is None: return False
    if t=="multiple_choice":
        options=question.get("options") or question.get("choices") or []
        a, b = _choice(submitted, options), _choice(correct, options)
        return a is not None and b is not None and a == b
    if t=="true_false":
        # Some generated true/false tasks store the numeric/text answer for
        # their underlying problem in `answer`, but the actual four judgments
        # in `statement_answers`. Grade the displayed statements, not that
        # unrelated scalar answer.
        if isinstance(question.get("statement_answers"), list):
            correct = question["statement_answers"]
        def parse(v):
            if isinstance(v,str) and ("," in v or ";" in v): v=re.split(r"[,;]",v)
            if isinstance(v,(list,tuple)):
                vals=[_truth(x) for x in v]
                return vals if all(x is not None for x in vals) else None
            return _truth(v)
        a,b=parse(submitted),parse(correct)
        return a is not None and b is not None and a==b
    if t in ("short_answer", "written", "essay"):
        # Equivalent line equations must receive the same grade, e.g.
        # y=2x+3, y=2*x+(3), and 2y=4x+6. Parse only restricted arithmetic;
        # never execute a student's input.
        if isinstance(submitted,str) and isinstance(correct,str) and '=' in submitted and '=' in correct:
            from .safe_math_equivalence import equivalent_polynomial_equations
            if equivalent_polynomial_equations(submitted,correct):
                return True
        expected_composite = _composite_verdict_number(correct)
        if expected_composite is not None:
            actual_composite = _composite_verdict_number(submitted)
            return actual_composite is not None and actual_composite == expected_composite
        try:
            from ..ai.engine.solver import equivalent
            if equivalent(submitted,correct):
                return True
            # Bài số phức: cho phép khoảng trắng và ký hiệu i/j, kể cả 0+0i.
            a=str(submitted).casefold().replace(' ', '').replace('−','-').replace('i','j')
            b=str(correct).casefold().replace(' ', '').replace('−','-').replace('i','j')
            if ('j' in a or 'j' in b) and all(re.fullmatch(r'[0-9.+\-j]+', v) for v in (a,b)):
                try:
                    return abs(complex(a)-complex(b)) < 1e-9
                except (ValueError, OverflowError):
                    pass
            return False
        except (TypeError,ValueError,ImportError):
            return str(submitted).strip().casefold()==str(correct).strip().casefold()
    return False
