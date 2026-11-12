import hashlib, re, ast
from .solver import equivalent

class ValidationError(ValueError): pass

def fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def _polynomial_key(value):
    """Conservative safe algebraic equivalence for basic univariate polynomials.

    Only parse arithmetic AST nodes, never eval input or SymPy parse_expr.
    Unsupported expressions return None rather than guessing.
    """
    raw = str(value).strip().replace("−", "-").replace("²", "^2").replace("³", "^3")
    # Vietnamese decimal comma is common in MCQ answer choices: 0,5 = 1/2.
    # Only convert commas BETWEEN digits; tuples/lists stay unsupported.
    raw = re.sub(r"(?<=\d),(?=\d)", ".", raw)
    if not 1 <= len(raw) <= 100 or "=" in raw:
        return None
    raw = raw.replace("^", "**").replace("×", "*").replace("·", "*")
    raw = re.sub(r"(?<=\d)(?=x\b)", "*", raw, flags=re.I)
    raw = re.sub(r"(?<=\d)(?=\()", "*", raw)
    raw = re.sub(r"(?<=x)(?=\()", "*", raw, flags=re.I)
    if re.search(r"[^\dxX\s+*()./-]", raw):
        return None
    try:
        import sympy as sp
        tree = ast.parse(raw, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 45:
            return None
        x = sp.Symbol('x')
        def visit(node):
            if isinstance(node, ast.Expression):return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int,float):return sp.Rational(str(node.value))
            if isinstance(node, ast.Name) and node.id.lower() == 'x':return x
            if isinstance(node, ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
                y=visit(node.operand);return y if isinstance(node.op,ast.UAdd) else -y
            if isinstance(node, ast.BinOp):
                l=visit(node.left);r=visit(node.right)
                if isinstance(node.op,ast.Add):return l+r
                if isinstance(node.op,ast.Sub):return l-r
                if isinstance(node.op,ast.Mult):return l*r
                if isinstance(node.op,ast.Div):
                    if r==0:raise ValueError('division by zero')
                    return l/r
                if isinstance(node.op,ast.Pow) and r.is_Integer and 0<=r<=5:return l**r
            raise ValueError('unsupported')
        result=sp.cancel(visit(tree))
        return result
    except (ValueError, SyntaxError, TypeError, ImportError, ZeroDivisionError, OverflowError):
        return None


def options_equivalent(a,b):
    if equivalent(a,b):return True
    lhs,rhs=_polynomial_key(a),_polynomial_key(b)
    if lhs is None or rhs is None:return False
    import sympy as sp
    return sp.cancel(lhs-rhs)==0


def validate(q: dict) -> None:
    required = ("id", "topic", "grade", "difficulty", "question_type", "question", "answer", "solution")
    for key in required:
        if key not in q or q[key] in (None, ""):
            raise ValidationError(f"missing:{key}")
    # Do not trust a free-form topic label when a canonical topic id is supplied.
    # When both fields are provided, a mismatch means the question is unsafe.
    canonical_topic = str(q.get("topic", "")).strip().casefold()
    requested_topic = str(q.get("requested_topic", canonical_topic)).strip().casefold()
    if requested_topic != canonical_topic:
        raise ValidationError("topic_mismatch_metadata")
    # Reject elementary arithmetic substituted for geometry topics. Topic IDs
    # alone are not evidence that the actual question belongs to that topic.
    topic_label = " ".join(str(q.get(k, "")) for k in ("topic", "knowledge_name", "topic_group")).casefold()
    prompt = re.sub(r"\s+", " ", str(q["question"]).strip().casefold())
    is_geometry = any(token in topic_label for token in (
        "geom", "hình học", "hinh hoc", "tam giác", "đường tròn", "không gian",
        "mặt phẳng", "tọa độ", "hình chóp", "hình trụ", "hình cầu",
    ))
    elementary_arithmetic = bool(re.fullmatch(
        r"(?:tính|tinh|hãy tính|hay tinh|calculate)\s*[:：]?\s*"
        r"[-+]?\d+(?:[.,]\d+)?\s*[+\-×*÷/]\s*[-+]?\d+(?:[.,]\d+)?\s*[.?!]?",
        prompt,
    ))
    subject_topic = any(token in topic_label for token in (
        "hàm số", "ham_so", "phương trình", "phuong_trinh", "mệnh đề", "menh_de",
        "tập hợp", "tap_hop", "lượng giác", "luong_giac", "xác suất", "xac_suat",
        "tích phân", "tich_phan", "giới hạn", "gioi_han", "đạo hàm", "dao_ham",
        "vectơ", "vector", "hình học", "hinh_hoc", "geom", "tam giác", "đường tròn",
    ))
    if elementary_arithmetic and (is_geometry or subject_topic):
        raise ValidationError("topic_mismatch_unrelated_arithmetic")
    # Verify elementary arithmetic independently instead of trusting a claimed
    # answer. This deliberately covers only prompts that are entire expressions.
    arithmetic_prompt = re.fullmatch(
        r"(?:tính|tinh|hãy tính|hay tinh|calculate)\s*[:：]?\s*"
        r"([-+]?\d+(?:[.,]\d+)?\s*[+\-×*÷/]\s*[-+]?\d+(?:[.,]\d+)?)\s*[.?!]?",
        prompt,
    )
    if arithmetic_prompt:
        from .solver import _safe_numeric
        expression = arithmetic_prompt.group(1).replace('÷','/').replace('×','*').replace(',','.')
        actual = _safe_numeric(expression)
        answer = _safe_numeric(q.get('answer'))
        if actual is not None and answer is not None and abs(actual-answer)>1e-8:
            raise ValidationError('wrong_arithmetic_answer')
    # A calculation question must not silently turn into a true/false prompt.
    if q["question_type"] == "true_false" and elementary_arithmetic:
        raise ValidationError("question_type_mismatch")
    if q["question_type"] == "multiple_choice":
        opts=q.get("options") or []
        if len(opts) != 4 or len({re.sub(r"\s+", " ", str(x).strip().casefold()) for x in opts}) != 4:
            raise ValidationError("mcq_options")
        if q["answer"] not in opts:
            raise ValidationError("mcq_answer")
        # Reject numerical duplicates such as 1/2 vs 0.5, not only identical text.
        # This is a conservative arithmetic check, not a proof of symbolic uniqueness.
        for i, left in enumerate(opts):
            for right in opts[i+1:]:
                if options_equivalent(left, right):
                    raise ValidationError("mcq_equivalent_options")
    elif q["question_type"] == "true_false":
        if not isinstance(q.get("statements"), list) or len(q["statements"]) != 4:
            raise ValidationError("tf_statements")
    q["fingerprint"] = fingerprint(q["question"])
    normalized = re.sub(r"(?<![A-Za-z])[-+]?\d+(?:[\.,/]\d+)?", "#", str(q["question"]).lower())
    normalized = re.sub(r"^trong [^,]+, ", "", normalized)
    normalized = re.sub(r"^sau khi phân tích dữ kiện, ", "", normalized)
    normalized = re.sub(r"^kiểm tra kiến thức: ", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    q["structure_fingerprint"] = fingerprint(normalized)
    return None
