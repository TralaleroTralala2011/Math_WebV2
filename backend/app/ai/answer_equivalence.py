"""Conservative numeric answer equivalence; no eval or arbitrary code execution."""
import ast
import math
import re

_ALLOWED = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)

def _value(expr):
    if isinstance(expr, (int, float)) and not isinstance(expr, bool):
        return float(expr)
    if not isinstance(expr, str) or len(expr) > 120:
        raise ValueError("Unsupported answer")
    s = expr.strip().lower().replace("π", "pi").replace("^", "**").replace("×", "*").replace("÷", "/")
    s = s.replace(",", ".")
    if not re.fullmatch(r"[0-9. +*/()\-pie]+", s):
        raise ValueError("Unsupported expression")
    tree = ast.parse(s, mode="eval")
    def visit(node, depth=0):
        if depth > 16: raise ValueError("Too complex")
        if isinstance(node, ast.Expression): return visit(node.body, depth+1)
        if isinstance(node, ast.Constant) and type(node.value) in (int,float): return float(node.value)
        if isinstance(node, ast.Name) and node.id in ("pi", "e"): return getattr(math,node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            v=visit(node.operand,depth+1);return v if isinstance(node.op,ast.UAdd) else -v
        if isinstance(node, ast.BinOp) and isinstance(node.op,_ALLOWED):
            a,b=visit(node.left,depth+1),visit(node.right,depth+1)
            if isinstance(node.op,ast.Add):v=a+b
            elif isinstance(node.op,ast.Sub):v=a-b
            elif isinstance(node.op,ast.Mult):v=a*b
            elif isinstance(node.op,ast.Div):v=a/b
            else:
                if abs(b)>16 or abs(a)>1e10:raise ValueError("Too large")
                v=a**b
            if not isinstance(v,(int,float)) or not math.isfinite(v) or abs(v)>1e15:raise ValueError("Out of range")
            return v
        raise ValueError("Unsupported expression")
    return visit(tree)

def numeric_equivalent(student, expected, rel_tol=1e-9, abs_tol=1e-9):
    """Return True/False, or None if answer needs a different grading method."""
    try: return math.isclose(_value(student),_value(expected),rel_tol=rel_tol,abs_tol=abs_tol)
    except (ValueError,SyntaxError,TypeError,ZeroDivisionError,OverflowError): return None
