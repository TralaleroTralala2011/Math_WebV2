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

def _choice(v, options):
    if isinstance(v,dict): v=v.get("value",v.get("answer",v.get("label",v)))
    s=str(v).strip()
    for i,option in enumerate(options or []):
        label=option.get("text",option.get("value",option.get("label",""))) if isinstance(option,dict) else str(option)
        if s.casefold()==str(label).strip().casefold(): return chr(65+i)
    m=re.fullmatch(r"(?:[A-Da-d]|[1-4])(?:[.)])?",s)
    if m:
        letter=s[0].upper()
        return chr(65+int(letter)-1) if letter.isdigit() else letter
    return s.casefold()

def grade_answer(question, submitted, correct=None):
    t=canonical_type(question)
    if correct is None: correct=question.get("correct_answer",question.get("answer"))
    if correct is None: return False
    if t=="multiple_choice":
        options=question.get("options") or question.get("choices") or []
        return _choice(submitted,options)==_choice(correct,options)
    if t=="true_false":
        def parse(v):
            if isinstance(v,str) and ("," in v or ";" in v): v=re.split(r"[,;]",v)
            if isinstance(v,(list,tuple)):
                vals=[_truth(x) for x in v]
                return vals if all(x is not None for x in vals) else None
            return _truth(v)
        a,b=parse(submitted),parse(correct)
        return a is not None and b is not None and a==b
    if t=="short_answer":
        try:
            from ..ai.engine.solver import equivalent
            return bool(equivalent(submitted,correct))
        except (TypeError,ValueError,ImportError):
            return str(submitted).strip().casefold()==str(correct).strip().casefold()
    return False
