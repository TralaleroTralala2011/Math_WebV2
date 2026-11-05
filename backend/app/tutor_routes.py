"""Bounded symbolic math tutor; does not claim general language-model reasoning."""
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sympy import Symbol, Eq, simplify, solveset, S
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

router = APIRouter(prefix='/api/tutor', tags=['tutor'])
x = Symbol('x')
TRANS = standard_transformations + (implicit_multiplication_application, convert_xor)
ALLOWED = {'x': x}

class TutorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    attempt: str = Field(default='', max_length=300)
    mode: str = 'hint'

def expr(raw):
    raw = raw.strip()
    if len(raw) > 120 or not re.fullmatch(r'[0-9xX+*/^().\-\s]+', raw):
        raise ValueError('Chỉ hỗ trợ biểu thức đại số một ẩn x và các phép toán cơ bản.')
    raw = raw.replace('X', 'x')
    result = parse_expr(raw, local_dict=ALLOWED, global_dict={'Integer':__import__('sympy').Integer,'Float':__import__('sympy').Float,'Rational':__import__('sympy').Rational,'Symbol':Symbol}, transformations=TRANS, evaluate=True)
    if result.free_symbols - {x} or result.count_ops() > 80:
        raise ValueError('Biểu thức vượt phạm vi hỗ trợ.')
    return result

@router.post('/step')
def step(req: TutorRequest):
    if req.mode not in ('hint','check','solution'):
        raise HTTPException(422, 'mode phải là hint, check hoặc solution')
    try:
        question = req.question.strip()
        if question.count('=') > 1:
            raise ValueError('Phương trình phải có đúng một dấu bằng.')
        if '=' in question:
            a,b = map(expr,question.split('='))
            diff = simplify(a-b)
            if diff == 0:
                answer = 'Mọi số thực đều là nghiệm.'
            else:
                sol = solveset(Eq(a,b),x,domain=S.Reals)
                answer = f'Tập nghiệm trên R: {sol}'
            hint = 'Chuyển các hạng tử về một vế, thu gọn, rồi giải phương trình theo x.'
        else:
            a = expr(question)
            diff = simplify(a)
            answer = f'Biểu thức rút gọn: {diff}'
            hint = 'Nhóm hạng tử đồng dạng, thực hiện phép toán và rút gọn từng bước.'
        result = {'scope':'symbolic_single_variable','hint':hint,'verified_with':'SymPy','limitations':'Không hỗ trợ bài toán lời văn, hình học hoặc chứng minh tổng quát.'}
        if req.mode == 'solution':
            result['solution'] = answer
        elif req.mode == 'check':
            if not req.attempt.strip():
                raise ValueError('Cần nhập bước giải để kiểm tra.')
            if '=' in question:
                if '=' in req.attempt:
                    c,d = map(expr,req.attempt.split('='))
                    attempt_diff = simplify(c-d)
                    # A constant multiple preserves roots, but zero is not a valid equivalent equation.
                    ratio = simplify(attempt_diff/diff) if diff != 0 else None
                    equivalent = bool(ratio is not None and ratio != 0 and not ratio.has(x))
                else:
                    equivalent = False
                result['equivalent_equation'] = equivalent
                result['feedback'] = 'Bước biến đổi tương đương về tập nghiệm.' if equivalent else 'Chưa xác minh được tương đương. Kiểm tra phép biến đổi và điều kiện.'
            else:
                equivalent = simplify(expr(req.attempt)-diff)==0
                result['equivalent_expression'] = bool(equivalent)
                result['feedback'] = 'Biểu thức tương đương.' if equivalent else 'Biểu thức chưa tương đương; hãy kiểm tra lại.'
        return result
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError, NotImplementedError) as exc:
        raise HTTPException(422, str(exc))
    except Exception:
        raise HTTPException(422, 'Bài toán chưa được bộ kiểm chứng này hỗ trợ.')
