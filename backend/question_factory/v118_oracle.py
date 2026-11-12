"""Independent, parameter-driven mathematical verification for V118 candidates.

Do not import generated answers. Recompute from parameters using enumeration,
mathematical limit/derivative/integral libraries, or independent identities.
This oracle checks arithmetic, NOT global distinctness of problem types.
"""
from math import comb, factorial
from itertools import permutations
from sympy import (Integer as Z, Rational as Q, pi, sqrt, sin, cos, exp, log,
                   Symbol, simplify, diff, integrate, limit, oo, Matrix, I, re, igcd)

x=Symbol('x',real=True)

def expected(family,p):
    a=p.get('a');b=p.get('b');c=p.get('c');d=p.get('d')
    if family=='v118_cartesian_pair_count':return sum(1 for _ in ((i,j) for i in range(a) for j in range(b)))
    if family=='v118_pigeonhole_ceil':return (p['n']+p['k']-1)//p['k']
    if family=='v118_two_by_two_cramer_x':
        return Matrix([[a,b],[c,d]]).LUsolve(Matrix([p['e'],p['f']]))[0]
    if family=='v118_quad_sign_integer_count':
        return sum((v-p['p'])*(v-p['q'])<=0 for v in range(p['p']-2,p['q']+3))
    if family=='v118_similarity_area_scale':return p['area']*p['ratio']**2
    if family=='v118_external_tangent_length':
        if p['d']<=p['r']:raise ValueError('not outside circle')
        return sqrt(p['d']**2-p['r']**2)
    if family=='v118_cyclic_opposite_angle':return 180-p['angle']
    if family=='v118_vector_parallel_parameter':return Q(p['b']*p['c'],p['a'])
    if family=='v118_right_triangle_circumcenter':
        return sqrt(p['a']**2+p['b']**2)/2
    if family=='v118_fixed_digit_even_numbers':
        n=p['n'];k=p['k']
        return sum(1 for v in permutations(range(n),k) if v[0]!=0 and v[-1]%2==0)
    if family=='v118_binomial_sum_alternating':
        return sum((-1)**k*comb(p['n'],k) for k in range(p['n']+1))
    if family=='v118_circle_equation_from_diameter':
        return Q((c-a)**2+(d-b)**2,4)
    if family=='v118_ap_two_terms_reconstruct':
        common=Q(p['uj']-p['ui'],p['j']-p['i'])
        return p['ui']+(p['n']-p['i'])*common
    if family=='v118_affine_recurrence_explicit':
        v=p['u1']
        for _ in range(p['n']-1):v=a*v+b
        return v
    if family=='v118_square_sum_formula':
        return sum(k*k for k in range(1,p['n']+1))
    if family=='v118_trig_tan_sum':
        ta=Q(p['a']);tb=Q(p['b'])
        return simplify((ta+tb)/(1-ta*tb))
    if family=='v118_count_trig_cos_period':
        return sum(1 for k in range(-100,101) if p['lo']<=k<=p['hi'])
    if family=='v118_limit_rational_infinity':
        return limit((a*x*x+b*x+1)/(d*x*x+c*x+3),x,oo)
    if family=='v118_limit_radical_conjugate':
        return limit(sqrt(x*x+a*x)-x,x,oo)
    if family=='v118_derivative_quotient':
        return diff((a*x+b)/(c*x+d),x).subs(x,p['x0'])
    if family=='v118_inverse_derivative':
        return 1/diff(x**3+x,x).subs(x,a)
    if family=='v118_pyramid_section_parallel_area':
        return p['S']*Q(p['k'])**2
    if family=='v118_prism_lateral_area':
        hyp=sqrt(a*a+b*b)
        return (a+b+hyp)*p['h']
    if family=='v118_3d_skew_lines_distance_axes':
        u=Matrix([1,0,0]);v=Matrix([0,1,0]);delta=Matrix([0,0,p['h']]);cross=u.cross(v)
        return abs(delta.dot(cross))/cross.norm()
    if family=='v118_vertical_asymptote_cancel':
        from sympy import cancel, denom, solve
        expr=cancel(((x-a)*(x-b))/((x-a)*(x-c)))
        poles=solve(denom(expr),x)
        if len(poles)!=1 or poles[0]==b:raise ValueError('no unique pole')
        return poles[0]
    if family=='v118_log_derivative_at':
        return diff(log(a*x+b),x).subs(x,p['x0'])
    if family=='v118_inflection_cubic':
        return __import__('sympy').solve(diff(a*x**3+b*x**2+c*x+1,x,2),x)[0]
    if family=='v118_integral_by_parts':
        return integrate(x*exp(p['k']*x),(x,0,1))
    if family=='v118_area_between_curves':
        return integrate(a*(p['r']**2-x*x),(x,-p['r'],p['r']))
    if family=='v118_partial_fraction_integral':
        return integrate(1/((x+a)*(x+b)),(x,0,1))
    if family=='v118_complex_division_real':
        return re((a+b*I)/(c+d*I)).expand(complex=True)
    if family=='v118_complex_locus_circle':
        return pi*p['r']**2
    if family=='v118_sphere_tangent_plane_d':
        T=Matrix([p['cx']+a,p['cy']+b,p['cz']+c]);n=Matrix([a,b,c]);return n.dot(T)
    if family=='v118_tetrahedron_volume_det':
        return abs(Matrix([[a,0,0],[0,b,0],[0,0,c]]).det())/6
    if family=='v118_binomial_at_least_two':
        success=Q(p['p']); n=p['n']
        return sum(comb(n,k)*success**k*(1-success)**(n-k) for k in range(2,n+1))
    if family=='v118_exponential_doubling_time':
        return log(2)/Q(p['r'])
    if family=='v118_plane_angle_normal':
        n1=Matrix([a,b,0]);n2=Matrix([a,0,c]);return abs(n1.dot(n2))/(n1.norm()*n2.norm())
    if family=='v118_exponential_inequality_lower':return p['k']
    raise ValueError('unsupported '+str(family))
