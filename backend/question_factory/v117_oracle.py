"""Independent, parameter-driven mathematical oracles for V117 families.

Each expression is derived independently of the prompt generator. This checks
computed answers, not complete phrasing, instructional quality, or uniqueness
of a mathematical method in the overall bank.
"""
from __future__ import annotations
from sympy import (Integer as I, Rational as Q, sqrt, pi, cos, sin, log,
                   asin, simplify, binomial, diff, integrate, Symbol)
from math import comb

x = Symbol('x', real=True)

def expected(family, p):
    if family == 'v117_de_morgan_3':return p['N']-p['A']-p['B']+p['C']
    if family == 'v117_exactly_two':return p['ab']+p['ac']+p['bc']-3*p['abc']
    if family == 'v117_abs_inequality_length':return 2*p['r']+1
    if family == 'v117_quadratic_root_count':
        a,b,c=p['a'],p['b'],p['c'];D=b*b-4*a*c
        return 2 if D>0 else 1 if D==0 else 0
    if family == 'v117_parabola_line_tangency':
        a,b,c,m=p['a'],p['b'],p['c'],p['m'];return c-Q((b-m)**2,4*a)
    if family == 'v117_linear_optimal_corner':return max(p['p']*p['W'],0)+p['q']*p['H']
    if family in {'v117_triangle_inradius','v117_triangle_circumradius'}:
        a,b,c=p['a'],p['b'],p['c'];semi=Q(a+b+c,2)
        area=sqrt(semi*(semi-a)*(semi-b)*(semi-c))
        if not (a+b>c and a+c>b and b+c>a):raise ValueError('invalid triangle')
        return area/semi if family.endswith('inradius') else a*b*c/(4*area)
    if family == 'v117_centroid_coordinates':return Q(sum(P[0] for P in (p['A'],p['B'],p['C'])),3)
    if family == 'v117_triangle_area_sine':return Q(p['a']*p['b'],2)*sin(pi*p['ang']/180)
    if family == 'v117_hypergeometric_selection':
        if not (p['red']>=p['want']>=0 and p['draw']>=p['want']):raise ValueError('invalid selection')
        return Q(comb(p['red'],p['want'])*comb(p['blue'],p['draw']-p['want']),comb(p['red']+p['blue'],p['draw']))
    if family == 'v117_bayes_inverse':
        a,b,c=map(Q,(p['pA'],p['p1'],p['p0']));return a*b/(a*b+(1-a)*c)
    if family == 'v117_nonadjacent_selection':return binomial(p['n']-p['k']+1,p['k'])
    if family == 'v117_stars_bars_positive':return binomial(p['n']-1,p['k']-1)
    if family == 'v117_weighted_mean':return Q(p['a']*p['na']+p['b']*p['nb'],p['na']+p['nb'])
    if family == 'v117_variance_affine':return p['a']**2*p['variance']
    if family == 'v117_trig_double_sin':return Q(2*p['a']*p['b'],p['a']**2+p['b']**2)
    if family == 'v117_trig_cos_sum':return cos(pi*(p['a']+p['b'])/180)
    if family == 'v117_trig_equation_count':return p['b']-p['a']+1
    if family == 'v117_recursion_fixed_point':return Q(p['b'])/(1-Q(p['a']))
    if family == 'v117_telescoping_sum':return Q(p['n'],p['n']+1)
    if family == 'v117_geometric_infinite_sum':
        if not -1<Q(p['q'])<1: raise ValueError('not convergent')
        return Q(p['a'])/(1-Q(p['q']))
    if family == 'v117_removable_limit':return 2*p['a']
    if family == 'v117_piecewise_continuity':return p['a']*p['c']+p['b']
    if family == 'v117_product_derivative':return diff((p['a']*x+p['b'])*x**p['n'],x).subs(x,1)
    if family == 'v117_trig_derivative':return diff(sin(p['a']*x),x).subs(x,0)
    if family == 'v117_tangent_slope_normal':return Q(-1,2*p['a']*p['x0']+p['b'])
    if family == 'v117_translation_image':return p['A'][0]+p['v'][0]
    if family == 'v117_rotation_90':return -p['b']
    if family == 'v117_reflect_diag':return p['b']
    if family == 'v117_homothety_nonorigin':return p['C'][0]+p['k']*(p['P'][0]-p['C'][0])
    if family == 'v117_3d_prism_diagonal':return sqrt(p['a']**2+p['b']**2+p['c']**2)
    if family == 'v117_line_plane_angle':
        if not 0<=p['h']<=p['l']:raise ValueError('height exceeds segment')
        return 180*asin(Q(p['h'],p['l']))/pi
    if family == 'v117_cubic_critical_point':return abs(p['b']-p['a'])
    if family == 'v117_quadratic_interval_min':return p['d'] if p['a']>0 else None
    if family == 'v117_rational_oblique_asymptote':return p['b']
    if family == 'v117_exponential_quadratic_substitution':return min(p['a'],p['b'])
    if family == 'v117_log_change_base':
        if not (p['a']>0 and p['a']!=1 and p['b']>0):raise ValueError('invalid log')
        return log(p['b'])/log(p['a'])
    if family == 'v117_log_inequality_direction':
        if not 0<Q(p['a'])<1:raise ValueError('not a decreasing log')
        return p['c']
    if family == 'v117_integral_substitute_affine':return integrate(p['a']*(p['a']*x+1)**p['n'],(x,0,p['end']))
    if family == 'v117_integral_cos':return integrate(cos(p['a']*x),(x,0,pi/(2*p['a'])))
    if family == 'v117_integral_abs_area':return 2*integrate(x,(x,0,p['a']))
    if family == 'v117_complex_modulus':return sqrt(p['a']**2+p['b']**2)
    if family == 'v117_complex_quadratic_real_part':return abs(p['a'])
    if family == 'v117_complex_conjugate_norm_sq':return p['a']**2+p['b']**2
    if family == 'v117_point_plane_foot':return p['c']
    if family == 'v117_plane_line_intersection':
        P=p['P'];v=p['v'];a,b,c=1,2,3
        den=a*v[0]+b*v[1]+c*v[2]
        if den==0:raise ValueError('line parallel plane')
        return Q(p['d']-(a*P[0]+b*P[1]+c*P[2]),den)
    if family == 'v117_plane_parallel_parameter':return Q(4*p['a'],p['b'])
    if family == 'v117_3d_cross_product_norm':return abs(p['a']*p['b'])
    if family == 'v117_volume_revolution':return pi*integrate((p['a']*x)**2,(x,0,p['b']))
    if family == 'v117_binomial_variance':return p['n']*Q(p['p'])*(1-Q(p['p']))
    if family == 'v117_uniform_integer_expectation':return Q(p['a']+p['b'],2)
    if family == 'v117_truncated_cone_volume':return pi*p['h']*(p['R']**2+p['R']*p['r']+p['r']**2)/3
    if family == 'v117_sphere_plane_circle_radius':
        if not 0<=p['d']<p['R']:raise ValueError('no circular intersection')
        return sqrt(p['R']**2-p['d']**2)
    if family == 'v117_point_line_min_distance':return sqrt(p['P'][0]**2+p['P'][1]**2)
    if family == 'v117_rect_optimal_area':return Q(p['P']**2,16)
    raise ValueError(f'Unknown family {family}')
