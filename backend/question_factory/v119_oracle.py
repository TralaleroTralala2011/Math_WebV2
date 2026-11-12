"""Independent reference evaluation from recorded parameters for V119.

The oracle never imports the generator's expected numeric result or explanation.
It establishes arithmetic correctness, not original pedagogy/novel method status.
"""
from __future__ import annotations
from math import comb
from sympy import Integer, Rational, Abs, I, pi, re, im, simplify

def expected(family,p):
    k=family.removeprefix('v119_')
    a=p.get('a');b=p.get('b');c=p.get('c');d=p.get('d')
    if k=='set_symmetric_difference':return a+b-2*p['i']
    if k in {'set_triple_union','set_exactly_one_of_three','set_universe_complement_union'}:
        # Decompose a consistent three-set Venn diagram into seven disjoint atoms.
        ab=p['ab'];ac=p['ac'];bc=p['bc'];abc=p['abc']
        only_a=a-ab-ac+abc
        only_b=b-ab-bc+abc
        only_c=c-ac-bc+abc
        only_ab=ab-abc;only_ac=ac-abc;only_bc=bc-abc
        union=sum((only_a,only_b,only_c,only_ab,only_ac,only_bc,abc))
        if min(only_a,only_b,only_c,only_ab,only_ac,only_bc,abc)<0:
            raise ValueError('invalid Venn diagram counts')
        if k=='set_triple_union':return union
        if k=='set_exactly_one_of_three':return only_a+only_b+only_c
        if union>p['u']:raise ValueError('Venn union exceeds universe')
        return p['u']-union
    if k=='set_proper_nonempty_subsets':
        return sum(comb(p['n'],j) for j in range(1,p['n']))
    if k=='set_k_subsets':return comb(p['n'],p['k'])
    if k=='set_functions_domain_to_codomain':
        return p['m']**p['n']
    if k=='set_disjoint_cartesian_offdiagonal':return sum(i!=j for i in range(p['n']) for j in range(p['n']))
    if k=='set_union_difference_count':return a-p['i']
    if k=='set_pairwise_disjoint_triple':return a+b+c
    if k=='conditional_from_counts':return Rational(p['j'],p['b'])
    if k=='joint_from_conditional':return Rational(p['p'])*Rational(p['q'])
    if k=='total_prob_two_sources':
        s=Rational(p['p']);return s*Rational(p['a'])+(1-s)*Rational(p['b'])
    if k=='bayes_posterior_inverse':
        s=Rational(p['p']);a=Rational(p['a']);b=Rational(p['b']);return s*a/(s*a+(1-s)*b)
    if k=='independent_joint':return Rational(p['p'])*Rational(p['q'])
    if k=='independent_union':
        s=Rational(p['p']);t=Rational(p['q']);return 1-(1-s)*(1-t)
    if k=='independent_neither':
        s=Rational(p['p']);t=Rational(p['q']);return 1-s-t+s*t
    if k=='conditional_without_replacement':return Rational(p['red']-1,p['red']+p['blue']-1)
    if k=='posterior_negative_result':
        s=Rational(p['p']);t=Rational(p['s']);f=Rational(p['f'])
        return s*(1-t)/(s*(1-t)+(1-s)*(1-f))
    if k=='conditional_at_least_one_two_trials':
        s=Rational(p['p']);t=Rational(p['q']);return (s*t)/(1-(1-s)*(1-t))
    if k=='complex_modulus_squared':return Abs(a+b*I)**2
    if k=='complex_conjugate_imag':return im((a+b*I).conjugate())
    if k=='complex_product_modulus_squared':return Abs((a+b*I)*(c+d*I))**2
    if k=='complex_quotient_real':return re((a+b*I)/(c+d*I))
    if k=='complex_quotient_imag':return im((a+b*I)/(c+d*I))
    if k=='complex_inverse_real':return re(1/(a+b*I))
    if k=='complex_inverse_imag':return im(1/(a+b*I))
    if k=='complex_distance_between_points':return Abs((a+b*I)-(c+d*I))
    if k=='complex_rotate_by_i_real':return re(I*(a+b*I))
    if k=='complex_circle_disk_area':return pi*p['r']**2
    raise ValueError('no oracle for '+family)
