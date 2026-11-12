"""A small, safely parsed numeric expression grader for factory questions.

No user-provided string is passed to sympify/eval/parse_expr. Only arithmetic,
pi and sqrt are accepted, with strict depth/magnitude limits. Does not grade
arbitrary algebra, proofs, or multiple mathematical solution sets.
"""
from __future__ import annotations
import ast
import re
from sympy import Integer, Rational, sqrt, pi, simplify, Abs

ALLOWED = re.compile(r'^[0-9\.\s\+\-\*\/\(\)\^π√,a-zA-Z]*$')

class GradingSyntaxError(ValueError): pass


def parse_numeric_expression(raw):
    if not isinstance(raw,str) or len(raw)>100:
        raise GradingSyntaxError('expression too long')
    value=raw.strip().replace('π','pi').replace('×','*').replace('÷','/')
    value=value.replace('−','-').replace('^','**')
    # Vietnamese decimal comma, but not arbitrary comma-separated arguments.
    value=re.sub(r'(?<=\d),(?=\d)', '.', value)
    value=value.replace('√(', 'sqrt(')
    value=re.sub(r'(?<=\d)\s*pi\b', '*pi', value)
    value=re.sub(r'(?<=\d)\s*sqrt\(', '*sqrt(', value)
    if not value or not ALLOWED.fullmatch(value):raise GradingSyntaxError('unsupported characters')
    if not re.fullmatch(r'[0-9\.\s\+\-\*\/\(\)a-zA-Z]*',value):raise GradingSyntaxError('unsupported input')
    try: tree=ast.parse(value,mode='eval')
    except SyntaxError as e:raise GradingSyntaxError('bad syntax') from e
    count=0
    def walk(node, depth):
        nonlocal count
        count+=1
        if count>50 or depth>15:raise GradingSyntaxError('expression too complex')
        if isinstance(node,ast.Constant):
            v=node.value
            if type(v) is int and abs(v)<=10**10:return Integer(v)
            if type(v) is float and abs(v)<=10**8:
                txt=str(v)
                if len(txt)>18:raise GradingSyntaxError('too many digits')
                return Rational(txt)
            raise GradingSyntaxError('numeric literal out of range')
        if isinstance(node,ast.Name) and node.id=='pi':return pi
        if isinstance(node,ast.Call):
            if not isinstance(node.func,ast.Name) or node.func.id!='sqrt' or len(node.args)!=1 or node.keywords:
                raise GradingSyntaxError('only sqrt(...) is supported')
            arg=walk(node.args[0],depth+1)
            if arg.is_number is not True or arg.is_real is not True or arg<0 or arg>10**12:
                raise GradingSyntaxError('invalid square root')
            return sqrt(arg)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            val=walk(node.operand,depth+1)
            return val if isinstance(node.op,ast.UAdd) else -val
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow)):
            left=walk(node.left,depth+1);right=walk(node.right,depth+1)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):
                if right==0: raise GradingSyntaxError('division by zero')
                return left/right
            if right.is_Integer is not True or not -8<=right<=8:
                raise GradingSyntaxError('power must be small integer')
            if left==0 and right<0:raise GradingSyntaxError('division by zero')
            if left.is_number is not True:raise GradingSyntaxError('invalid power')
            return left**int(right)
        raise GradingSyntaxError('unsupported syntax')
    return walk(tree.body,0)


def _parse_numeric_answer(raw):
    """Safe scalar or simple variable assignment, never user-supplied sympify."""
    m=re.fullmatch(r'\s*([A-Za-z])\s*=\s*(.+)\s*', raw, flags=re.DOTALL)
    if m:
        return m.group(1).casefold(),parse_numeric_expression(m.group(2))
    return None,parse_numeric_expression(raw)


def _parse_ordered_pair(raw):
    """Two ordered numeric coordinates; semicolon avoids decimal-comma ambiguity.

    Supports (x,y)=(7;5), (7;5), x=7;y=5 and x=7,y=5.
    Does not interpret (7,5) as coordinates: 7,5 is decimal in Vietnamese.
    """
    raw=raw.strip()
    names=None
    m=re.fullmatch(r'\(\s*([A-Za-z])\s*,\s*([A-Za-z])\s*\)\s*=\s*(.*)', raw, re.DOTALL)
    if m:
        names=(m.group(1).casefold(),m.group(2).casefold())
        if names[0]==names[1]: raise GradingSyntaxError('repeated coordinate name')
        raw=m.group(3).strip()
    m=re.fullmatch(r'\(\s*([^;]+?)\s*;\s*([^;]+?)\s*\)', raw, re.DOTALL)
    if m:
        return names,(parse_numeric_expression(m.group(1)),parse_numeric_expression(m.group(2)))
    # x=7;y=5 or x=7,y=5 (comma only before a new named variable)
    m=re.fullmatch(r'\s*([A-Za-z])\s*=\s*(.+?)\s*[;,]\s*([A-Za-z])\s*=\s*(.+?)\s*',raw,re.DOTALL)
    if m:
        names=(m.group(1).casefold(),m.group(3).casefold())
        if names[0]==names[1]: raise GradingSyntaxError('repeated variable name')
        return names,(parse_numeric_expression(m.group(2)),parse_numeric_expression(m.group(4)))
    raise GradingSyntaxError('not a supported ordered pair')


def _compare_values(left,right):
    return simplify(left-right)==0


def answers_equivalent(expected,user_answer):
    """Grade bounded numeric expressions, scalar assignments and ordered pairs.

    Unknown/free-text mathematical answers still require a separate reviewer:
    a matching string must not be called an independently checked proof.
    """
    if not isinstance(expected,str) or not isinstance(user_answer,str):
        return False,'invalid_answer_type'
    try:
        en,ep=_parse_ordered_pair(expected)
        un,up=_parse_ordered_pair(user_answer)
        if en is not None and un is not None and en != un:
            return False,'ordered_pair_equivalence'
        return all(_compare_values(a,b) for a,b in zip(ep,up)), 'ordered_pair_equivalence'
    except (GradingSyntaxError,ValueError,TypeError,OverflowError,ZeroDivisionError):
        pass
    try:
        en,e=_parse_numeric_answer(expected)
        un,u=_parse_numeric_answer(user_answer)
        if en is not None and un is not None and en != un:
            return False,'single_variable_equivalence'
        return _compare_values(e,u), ('single_variable_equivalence' if en or un else 'exact_symbolic_expression')
    except (GradingSyntaxError,ValueError,TypeError,OverflowError,ZeroDivisionError):
        # Text-only fallback for non-math items; never evaluate arbitrary text.
        return expected.strip().casefold()==user_answer.strip().casefold(), 'normalized_text'
