"""Restricted, non-evaluating equivalence for elementary polynomial equations.

Only x/y, rational numbers and +,-,*,/,integer powers are accepted. Python's
`eval`, SymPy `sympify` on raw strings, and parse_expr are deliberately avoided.
"""
import ast
import re


def _polynomial_expression(raw):
    from sympy import Integer, Rational, symbols
    x,y=symbols('x y')
    s=str(raw).strip().replace('−','-').replace('×','*').replace('·','*').replace('²','^2').replace('³','^3').replace('^','**')
    if len(s)>160 or not re.fullmatch(r'[0-9xyXY+*/().\s-]+',s):
        raise ValueError('Unsupported equation syntax')
    s=s.lower()
    s=re.sub(r'(?<=\d)(?=[xy(])','*',s)
    s=re.sub(r'(?<=[xy])(?=\()','*',s)
    s=re.sub(r'(?<=\))(?=[xy0-9(])','*',s)
    tree=ast.parse(s,mode='eval')
    if sum(1 for _ in ast.walk(tree))>65:raise ValueError('Expression too complex')

    def convert(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)) and not isinstance(node.value,bool):
            if abs(node.value)>1000000:raise ValueError('Constant out of bounds')
            return Integer(node.value) if isinstance(node.value,int) else Rational(str(node.value))
        if isinstance(node,ast.Name) and node.id in ('x','y'):
            return {'x':x,'y':y}[node.id]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
            value=convert(node.operand)
            return -value if isinstance(node.op,ast.USub) else value
        if isinstance(node,ast.BinOp):
            if isinstance(node.op,ast.Pow):
                if not isinstance(node.right,ast.Constant) or type(node.right.value) is not int or not 0<=node.right.value<=4:
                    raise ValueError('Unsupported exponent')
                return convert(node.left)**node.right.value
            left,right=convert(node.left),convert(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):
                if right.is_number and right!=0:return left/right
                raise ValueError('Division only by nonzero constants')
        raise ValueError('Unsupported syntax')
    return convert(tree.body)


def equivalent_polynomial_equations(a,b):
    """True only for the same solution set up to nonzero scalar scaling."""
    if not isinstance(a,str) or not isinstance(b,str) or a.count('=')!=1 or b.count('=')!=1:
        return False
    try:
        from sympy import Poly, expand, symbols
        x,y=symbols('x y')
        a_left,a_right=a.split('=');b_left,b_right=b.split('=')
        p=Poly(_polynomial_expression(a_left)-_polynomial_expression(a_right),x,y)
        q=Poly(_polynomial_expression(b_left)-_polynomial_expression(b_right),x,y)
        if p.is_zero or q.is_zero or p.total_degree()>3 or q.total_degree()>3:return False
        return expand(p.as_expr()*q.LC()-q.as_expr()*p.LC())==0
    except (ValueError,TypeError,OverflowError,SyntaxError,ImportError):
        return False
