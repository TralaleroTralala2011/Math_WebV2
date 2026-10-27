from fractions import Fraction
import ast
import math
import operator
import re

def normalize_answer(value):
    s=str(value).strip().lower().replace(" ", "")
    s=s.replace("−","-")
    try: return Fraction(s)
    except Exception: return s

def _safe_numeric(value):
    """Evaluate a restricted arithmetic expression for answer equivalence; never use eval()."""
    if isinstance(value, (int, float, Fraction)):
        return float(value)
    text = str(value).strip().replace("−", "-").replace("×", "*").replace("·", "*")
    text = text.replace("π", "pi")
    text = re.sub(r"(?<![A-Za-z])√\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", text)
    text = re.sub(r"(?<![A-Za-z])sqrt\s*\(([^()]*)\)", r"sqrt(\1)", text)
    try:
        tree = ast.parse(text, mode="eval")
    except Exception:
        return None
    binary = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
    unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in binary: return binary[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary: return unary[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sqrt" and len(node.args) == 1:
            return math.sqrt(visit(node.args[0]))
        raise ValueError("unsupported expression")
    try:
        result = visit(tree)
        return float(result) if math.isfinite(float(result)) else None
    except Exception:
        return None

def _coordinate_pair(value):
    text = str(value).strip().replace("−", "-")
    text = text.strip("()[]{} ")
    parts = re.split(r"\s*[;,]\s*", text)
    if len(parts) != 2:
        return None
    x, y = (_safe_numeric(part) for part in parts)
    return (x, y) if x is not None and y is not None else None

def equivalent(a,b):
    """Compare numeric, fraction, radical and coordinate-pair answers robustly."""
    if normalize_answer(a) == normalize_answer(b):
        return True
    pair_a, pair_b = _coordinate_pair(a), _coordinate_pair(b)
    if pair_a is not None and pair_b is not None:
        return all(math.isclose(x,y,rel_tol=1e-8,abs_tol=1e-8) for x,y in zip(pair_a,pair_b))
    numeric_a, numeric_b = _safe_numeric(a), _safe_numeric(b)
    if numeric_a is not None and numeric_b is not None:
        return math.isclose(numeric_a,numeric_b,rel_tol=1e-8,abs_tol=1e-8)
    return False

def solve_numeric(q: dict):
    return q.get("answer")
