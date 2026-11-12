"""Deterministic generation and independent symbolic verification of curated methods.

This is a bounded, transparent collection of mathematically distinct objectives.
The user target of 300,000 distinct problem METHODS is NOT achieved by making
copies of these families with new coefficients, IDs, or wording.
"""
from __future__ import annotations
import hashlib
import random
import re
from sympy import (Integer, Rational, Symbol, sqrt, pi, cos, sin, factorial,
                   binomial, simplify, sympify, solve, diff, integrate)
from .expanded_catalog import BLUEPRINTS

FAMILIES = {row[0] for row in BLUEPRINTS}


def _rng(family, ordinal, seed_key=None):
    value = hashlib.sha256(f'v113:{family}:{seed_key or family}:{ordinal}'.encode()).digest()
    return random.Random(int.from_bytes(value[:8], 'big'))


def _number(x):
    return simplify(x)


def generate(family, ordinal, difficulty, seed_key=None):
    if family not in FAMILIES: raise ValueError('unknown expanded family')
    if type(ordinal) is not int or not 0 <= ordinal < 10: raise ValueError('ordinal must be 0..9')
    r=_rng(family,ordinal,seed_key)
    v=r.randint
    p={}; stem=''; why=''; answer=None
    a=v(2,8); b=v(2,8); c=v(1,9); t=ordinal+2
    if family=='set_intersection_from_union':
        p=dict(a=12+t,b=14+v(0,8),common=v(2,8));p['union']=p['a']+p['b']-p['common']
        answer=p['a']+p['b']-p['union'];stem=f"Cho |A|={p['a']}, |B|={p['b']}, |A∪B|={p['union']}. Tính |A∩B|."
        why=f"Theo công thức |A∪B|=|A|+|B|−|A∩B|, suy ra |A∩B|={p['a']}+{p['b']}−{p['union']}={answer}."
    elif family=='set_difference_size':
        p=dict(a=t+12,common=v(1,6));answer=p['a']-p['common']
        stem=f"Tập A có {p['a']} phần tử, trong đó {p['common']} phần tử cũng thuộc B. Tính |A\\B|."
        why=f"A\\B chỉ gồm phần tử thuộc A nhưng không thuộc B; |A\\B|={p['a']}−{p['common']}={answer}."
    elif family=='set_symmetric_difference':
        p=dict(a=18+t,b=15+v(0,8),common=v(1,9));answer=p['a']+p['b']-2*p['common']
        stem=f"Hai tập hữu hạn có |A|={p['a']}, |B|={p['b']}, |A∩B|={p['common']}. Tính |A△B|."
        why=f"A△B=(A\\B)∪(B\\A), hai phần rời nhau. Số phần tử={p['a']}+{p['b']}−2×{p['common']}={answer}."
    elif family=='set_power_set':
        p=dict(n=t);answer=2**t
        stem=f"Một tập hợp có {t} phần tử phân biệt. Hỏi có bao nhiêu tập con (kể cả rỗng)?"
        why=f"Mỗi phần tử có hai lựa chọn: thuộc hoặc không thuộc tập con. Theo quy tắc nhân có 2^{t}={answer} tập con."
    elif family=='linear_inequality_bound':
        p=dict(a=a,b=v(-10,10),c=v(3,24));answer=Rational(p['c']-p['b'],p['a'])
        stem=f"Giải bất phương trình {p['a']}x+({p['b']}) ≥ {p['c']}. Hãy cho biết cận dưới của x."
        why=f"Do {p['a']}>0, chuyển vế được {p['a']}x≥{p['c']-p['b']}. Chia cho số dương {p['a']} ta có x≥{answer}."
    elif family=='quadratic_discriminant':
        p=dict(a=a,b=v(-9,9),c=v(-9,9));answer=p['b']**2-4*p['a']*p['c']
        stem=f"Với phương trình bậc hai {p['a']}x²+({p['b']})x+({p['c']})=0, hãy tính biệt thức Δ=b²−4ac."
        why=f"Áp dụng Δ=b²−4ac=({p['b']})²−4×{p['a']}×({p['c']})={answer}."
    elif family in ('quadratic_vertex_x','quadratic_vertex_y'):
        p=dict(a=a,b=v(-12,12),c=v(-10,10))
        x0=Rational(-p['b'],2*p['a']); y0=p['a']*x0*x0+p['b']*x0+p['c']
        answer=x0 if family=='quadratic_vertex_x' else y0
        stem=f"Cho parabol y={p['a']}x²+({p['b']})x+({p['c']}). Tính {'hoành' if family.endswith('_x') else 'tung'} độ đỉnh."
        why=(f"Trục đối xứng x₀=−b/(2a)={x0}. Thay vào y=ax²+bx+c được y₀={y0}; "
             f"vậy tọa độ cần tìm bằng {answer}.")
    elif family=='system_sum_solution':
        p=dict(x=v(-8,9),y=v(-6,10));p['s']=2*p['x']+p['y'];p['d']=p['x']-p['y'];answer=p['x']+p['y']
        stem=f"Cho hệ 2x+y={p['s']}; x−y={p['d']}. Tính x+y của nghiệm duy nhất."
        why=f"Từ x−y={p['d']} được y=x−{p['d']}. Thay vào 2x+y={p['s']} cho x={p['x']}, y={p['y']}. Vậy x+y={answer}."
    elif family=='polynomial_remainder':
        p=dict(a=a,b=v(-8,8),c=v(-8,8),t=v(-5,7));answer=p['a']*p['t']**2+p['b']*p['t']+p['c']
        stem=f"Chia P(x)={p['a']}x²+({p['b']})x+({p['c']}) cho x−({p['t']}). Tính số dư."
        why=f"Theo định lý dư, số dư=P({p['t']})={p['a']}×({p['t']})²+({p['b']})×({p['t']})+({p['c']})={answer}."
    elif family in ('circle_area','circle_circumference','circle_sector_area','circle_arc_length'):
        p=dict(radius=3+2*ordinal+v(0,1))
        if family=='circle_area':
            answer=pi*p['radius']**2;stem=f"Hình tròn có bán kính r={p['radius']} cm. Tính diện tích chính xác theo π (cm²)."
            why=f"Diện tích S=πr²=π×{p['radius']}²={answer} cm²."
        elif family=='circle_circumference':
            answer=2*pi*p['radius'];stem=f"Đường tròn có bán kính {p['radius']} cm. Tính chu vi chính xác theo π (cm)."
            why=f"Chu vi C=2πr=2π×{p['radius']}={answer} cm."
        else:
            p['angle']=(ordinal+1)*30
            if family=='circle_sector_area':
                answer=pi*p['radius']**2*Rational(p['angle'],360)
                stem=f"Hình quạt bán kính {p['radius']} cm có góc ở tâm {p['angle']}°. Tính diện tích chính xác (cm²)."
                why=f"S_quạt=({p['angle']}/360)π×{p['radius']}²={answer} cm²."
            else:
                answer=2*pi*p['radius']*Rational(p['angle'],360)
                stem=f"Một cung tròn bán kính {p['radius']} cm chắn góc ở tâm {p['angle']}°. Tính độ dài cung chính xác (cm)."
                why=f"Độ dài l=({p['angle']}/360)×2π×{p['radius']}={answer} cm."
    elif family in ('pythagoras_hypotenuse','pythagoras_missing_leg'):
        triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(9,40,41),(12,35,37),(11,60,61),(20,21,29),(28,45,53),(16,63,65)]
        x,y,h=triples[ordinal];p=dict(x=x,y=y,h=h)
        if family=='pythagoras_hypotenuse':
            answer=h;stem=f"Tam giác vuông có hai cạnh góc vuông {x} cm và {y} cm. Tính cạnh huyền (cm)."
            why=f"Định lý Pythagoras: c²={x}²+{y}²={h*h}, nên c=√{h*h}={h} cm."
        else:
            answer=y;stem=f"Tam giác vuông có cạnh huyền {h} cm và một cạnh góc vuông {x} cm. Tính cạnh còn lại."
            why=f"Cạnh còn lại b=√({h}²−{x}²)=√{y*y}={y} cm."
    elif family=='trapezoid_area':
        p=dict(base1=a+ordinal,base2=b+ordinal+5,h=c+2);answer=Rational((p['base1']+p['base2'])*p['h'],2)
        stem=f"Một hình thang có hai đáy {p['base1']} cm, {p['base2']} cm và chiều cao {p['h']} cm. Tính diện tích."
        why=f"S=(đáy lớn+đáy nhỏ)×chiều cao/2=({p['base1']}+{p['base2']})×{p['h']}/2={answer} cm²."
    elif family=='heron_area':
        base=[(3,4,5),(5,5,6),(5,12,13),(6,8,10),(7,15,20),
              (9,10,17),(13,14,15),(10,24,26),(8,15,17),(9,12,15)]
        x,y,z=base[ordinal];p=dict(a=x,b=y,c=z)
        semi=Rational(sum(p.values()),2);answer=sqrt(semi*(semi-p['a'])*(semi-p['b'])*(semi-p['c']))
        stem=f"Tam giác có ba cạnh {p['a']}, {p['b']}, {p['c']} cm. Tính diện tích chính xác bằng công thức Heron."
        why=f"Nửa chu vi s=({p['a']}+{p['b']}+{p['c']})/2={semi}. Theo Heron S=√[s(s−a)(s−b)(s−c)]={answer} cm²."
    elif family=='cosine_rule_side_square':
        p=dict(a=a+ordinal,b=b+ordinal,angle=[60,90,120][ordinal%3]);answer=p['a']**2+p['b']**2-2*p['a']*p['b']*cos(pi*p['angle']/180)
        stem=f"Tam giác có hai cạnh kề góc C dài {p['a']} cm và {p['b']} cm, góc xen giữa C={p['angle']}°. Tính bình phương cạnh đối diện C."
        why=f"Định lý cosin: c²=a²+b²−2ab cos C={p['a']}²+{p['b']}²−2×{p['a']}×{p['b']}×cos({p['angle']}°)={answer}."
    elif family=='midpoint_x_2d':
        p=dict(x1=v(-15,15),x2=ordinal*3-9);answer=Rational(p['x1']+p['x2'],2)
        stem=f"Trong Oxy, A({p['x1']};{v(-8,8)}), B({p['x2']};{v(-8,8)}). Tính hoành độ trung điểm AB."
        why=f"Hoành độ trung điểm bằng trung bình hoành độ hai đầu: ({p['x1']}+{p['x2']})/2={answer}."
    elif family in ('distance_2d','slope_2d','line_intersection_x'):
        if family=='distance_2d':
            p=dict(x1=v(-8,8),y1=v(-8,8),dx=ordinal+2,dy=v(1,9));answer=sqrt(p['dx']**2+p['dy']**2)
            stem=f"Trong Oxy, cho A({p['x1']};{p['y1']}) và B({p['x1']+p['dx']};{p['y1']+p['dy']}). Tính AB."
            why=f"AB=√[(Δx)²+(Δy)²]=√({p['dx']}²+{p['dy']}²)={answer}."
        elif family=='slope_2d':
            p=dict(x1=v(-6,4),y1=v(-8,8),dx=ordinal+1,dy=v(-9,9));answer=Rational(p['dy'],p['dx'])
            stem=f"Đường thẳng qua A({p['x1']};{p['y1']}) và B({p['x1']+p['dx']};{p['y1']+p['dy']}). Tính hệ số góc."
            why=f"Hệ số góc k=(yB−yA)/(xB−xA)={p['dy']}/{p['dx']}={answer}, vì Δx≠0."
        else:
            p=dict(m1=ordinal+2,m2=-(v(1,7)),b1=v(-10,10),intersection=ordinal-4)
            p['b2']=p['b1']+(p['m1']-p['m2'])*p['intersection'];answer=p['intersection']
            stem=f"Hai đường thẳng y={p['m1']}x+({p['b1']}) và y={p['m2']}x+({p['b2']}) cắt nhau tại P. Tính hoành độ P."
            why=f"Đặt tung độ bằng nhau: ({p['m1']}−({p['m2']}))x={p['b2']}−({p['b1']}); suy ra x={answer}."
    elif family in ('vector_dot_2d','vector_norm_sq_2d','parallelogram_area_det','triangle_area_coords'):
        p=dict(x=ordinal+1,y=v(-7,7),u=v(-6,7),w=v(-7,8))
        if family=='vector_dot_2d':
            answer=p['x']*p['u']+p['y']*p['w'];stem=f"Trong Oxy, u=({p['x']};{p['y']}), v=({p['u']};{p['w']}). Tính u·v."
            why=f"Tích vô hướng u·v=x₁x₂+y₁y₂={p['x']}×({p['u']})+({p['y']})×({p['w']})={answer}."
        elif family=='vector_norm_sq_2d':
            answer=p['x']**2+p['y']**2;stem=f"Vectơ u=({p['x']};{p['y']}) trong Oxy. Tính |u|²."
            why=f"Bình phương độ dài bằng tổng bình phương tọa độ: {p['x']}²+({p['y']})²={answer}."
        elif family=='parallelogram_area_det':
            if p['x']*p['w']==p['y']*p['u']: p['w']+=1
            answer=abs(p['x']*p['w']-p['y']*p['u'])
            stem=f"Hình bình hành sinh bởi u=({p['x']};{p['y']}), v=({p['u']};{p['w']}). Tính diện tích."
            why=f"S=|det(u,v)|=|{p['x']}×({p['w']})−({p['y']})×({p['u']})|={answer}."
        else:
            if p['x']*p['w']==p['y']*p['u']: p['w']+=1
            answer=Rational(abs(p['x']*p['w']-p['y']*p['u']),2)
            stem=f"Cho A(0;0), B({p['x']};{p['y']}), C({p['u']};{p['w']}). Tính diện tích tam giác ABC."
            why=f"S=1/2|det(AB,AC)|=|{p['x']}×({p['w']})−({p['y']})×({p['u']})|/2={answer}."
    elif family in ('binomial_coefficient','permutation_count','combination_count'):
        p=dict(n=6+ordinal,k=v(1,4))
        if family=='binomial_coefficient':
            answer=binomial(p['n'],p['k']);stem=f"Hệ số của x^{p['k']} trong khai triển (1+x)^{p['n']} bằng bao nhiêu?"
            why=f"Theo nhị thức Newton, hệ số C({p['n']},{p['k']})={p['n']}!/[{p['k']}!({p['n']}-{p['k']})!]={answer}."
        elif family=='permutation_count':
            answer=factorial(p['n']);stem=f"Có {p['n']} quyển sách phân biệt. Có bao nhiêu cách xếp thành một hàng?"
            why=f"Mỗi vị trí lần lượt có {p['n']},{p['n']-1},...,1 lựa chọn: {p['n']}!={answer} cách."
        else:
            answer=binomial(p['n'],p['k']);stem=f"Một nhóm gồm {p['n']} học sinh. Có bao nhiêu cách chọn {p['k']} học sinh vào một đội (không phân vai)?"
            why=f"Do không xét thứ tự, số cách chọn là C({p['n']},{p['k']})={p['n']}!/[{p['k']}!({p['n']}-{p['k']})!]={answer}."
    elif family=='classical_probability':
        p=dict(n=14+ordinal,k=v(2,9));answer=Rational(p['k'],p['n'])
        stem=f"Chọn ngẫu nhiên 1 phiếu trong {p['n']} phiếu đồng khả năng, có {p['k']} phiếu trúng. Xác suất trúng là bao nhiêu?"
        why=f"Theo định nghĩa cổ điển P(A)=số kết quả thuận lợi/tổng số kết quả={p['k']}/{p['n']}={answer}."
    elif family=='urn_two_success':
        p=dict(n=12+ordinal,k=v(3,8));answer=Rational(p['k']*(p['k']-1),p['n']*(p['n']-1))
        stem=f"Một hộp có {p['n']} viên, trong đó {p['k']} viên đỏ. Rút ngẫu nhiên 2 viên không hoàn lại. Xác suất cả hai đều đỏ là?"
        why=f"Xác suất lần đầu đỏ {p['k']}/{p['n']}, sau đó đỏ ({p['k']}-1)/({p['n']}-1). Nhân hai xác suất: {answer}."
    elif family in ('arithmetic_mean','population_variance'):
        data=[ordinal+v(-4,6),ordinal+v(0,7),ordinal+v(4,9),ordinal+v(-1,10)]
        p=dict(values=data);mean=Rational(sum(data),len(data))
        if family=='arithmetic_mean':
            answer=mean;stem=f"Tính số trung bình cộng của dữ liệu: {', '.join(map(str,data))}."
            why=f"Tổng là {sum(data)}, có {len(data)} giá trị. Trung bình = {sum(data)}/{len(data)}={answer}."
        else:
            answer=sum((x-mean)**2 for x in data)/len(data)
            stem=f"Tính phương sai của toàn bộ dữ liệu {', '.join(map(str,data))} (chia cho n, không chia n−1)."
            why=f"Trung bình x̄={mean}. Phương sai σ²=["+'+'.join(f'({x}−{mean})²' for x in data)+f"]/{len(data)}={answer}."
    elif family in ('geometric_sequence_nth','geometric_sequence_sum'):
        p=dict(u1=v(1,7),q=v(2,4),n=3+ordinal)
        if family=='geometric_sequence_nth':
            answer=p['u1']*p['q']**(p['n']-1)
            stem=f"Cấp số nhân có u₁={p['u1']}, công bội q={p['q']}. Tính u{p['n']}."
            why=f"uₙ=u₁q^(n−1)={p['u1']}×{p['q']}^({p['n']}-1)={answer}."
        else:
            answer=p['u1']*(p['q']**p['n']-1)//(p['q']-1)
            stem=f"Cấp số nhân có u₁={p['u1']}, q={p['q']}. Tính tổng {p['n']} số hạng đầu."
            why=f"Vì q≠1, Sₙ=u₁(qⁿ−1)/(q−1)={p['u1']}×({p['q']}^{p['n']}−1)/({p['q']}-1)={answer}."
    elif family=='polynomial_limit':
        p=dict(a=a,b=v(-10,10),c=v(-12,12),t=v(-6,8));answer=p['a']*p['t']**2+p['b']*p['t']+p['c']
        stem=f"Tính lim(x→{p['t']}) [{p['a']}x²+({p['b']})x+({p['c']})]."
        why=f"Đa thức liên tục trên ℝ, nên giới hạn bằng giá trị tại x={p['t']}: {answer}."
    elif family=='derivative_power_at':
        p=dict(power=2+ordinal,a=a,t=v(-3,4));answer=p['a']*p['power']*p['t']**(p['power']-1)
        stem=f"Cho f(x)={p['a']}x^{p['power']}. Tính f'({p['t']})."
        why=f"Theo quy tắc đạo hàm lũy thừa, f'(x)={p['a']}×{p['power']}x^{p['power']-1}. Thay x={p['t']}, nhận {answer}."
    elif family=='quadratic_second_derivative':
        p=dict(a=a+ordinal,b=v(-10,10),c=v(-10,10));answer=2*p['a']
        stem=f"Cho f(x)={p['a']}x²+({p['b']})x+({p['c']}). Tính f''(x) (hằng số)."
        why=f"Lấy đạo hàm: f'(x)=2×{p['a']}x+({p['b']}); lần hai f''(x)=2×{p['a']}={answer}."
    elif family=='conditional_probability':
        p=dict(a=v(1,5)+ordinal);p['joint']=p['a'];p['given']=p['a']+v(3,9);p['n']=p['given']+v(5,12)
        answer=Rational(p['joint'],p['given']);stem=f"Trong {p['n']} kết quả đồng khả năng, B xảy ra trong {p['given']} kết quả và A∩B trong {p['joint']} kết quả. Tính P(A|B)."
        why=f"B có xác suất dương. Theo công thức P(A|B)=P(A∩B)/P(B)=({p['joint']}/{p['n']})/({p['given']}/{p['n']})={answer}."
        if not 0 < p['joint'] <= p['given'] < p['n']: raise ValueError('invalid conditional fixture')
    elif family=='special_angle_sine':
        angles=[0,30,45,60,90,120,135,150,180,210];p=dict(angle=angles[ordinal]);answer=sin(pi*p['angle']/180)
        stem=f"Tính giá trị chính xác sin({p['angle']}°)."
        why=f"Quy về góc đặc biệt trên đường tròn lượng giác và xét dấu theo góc phần tư: sin({p['angle']}°)={answer}."
    elif family=='trig_pythagorean_cos2':
        p=dict(m=v(1,6),n=8+ordinal);answer=1-Rational(p['m']**2,p['n']**2)
        stem=f"Biết sin α={p['m']}/{p['n']}. Tính cos² α."
        why=f"Từ sin² α+cos² α=1, suy ra cos² α=1−({p['m']}/{p['n']})²={answer}."
    elif family=='exponential_equation':
        p=dict(base=v(2,6),power=ordinal+2);answer=p['power']
        stem=f"Giải phương trình {p['base']}^x={p['base']}^{p['power']}. Tìm x."
        why=f"Vì cơ số {p['base']}>0 và khác 1, hàm mũ một-một; bằng nhau khi số mũ bằng nhau: x={answer}."
    elif family=='logarithm_equation':
        p=dict(base=v(2,5),power=ordinal+1);answer=p['base']**p['power']
        stem=f"Giải phương trình log_{p['base']}(x)={p['power']}, x>0."
        why=f"Theo định nghĩa logarit, x={p['base']}^{p['power']}={answer}>0, thỏa điều kiện."
    elif family=='logarithm_power':
        p=dict(base=v(2,5),power=ordinal+2);p['value']=p['base']**p['power'];answer=p['power']
        stem=f"Sử dụng định nghĩa logarit, tính giá trị chính xác log_{p['base']}({p['value']})."
        why=f"Vì {p['value']}={p['base']}^{p['power']}, nên log_{p['base']}({p['value']})={answer}."
    elif family in ('complex_modulus_squared','complex_add_real','complex_multiply_imag'):
        p=dict(a=v(-9,9),b=ordinal+2,c=v(-7,7),d=v(-6,9))
        if family=='complex_modulus_squared':
            answer=p['a']**2+p['b']**2;stem=f"Trên mặt phẳng phức, số z={p['a']}+({p['b']})i. Tính bình phương môđun |z|²."
            why=f"|a+bi|²=a²+b²=({p['a']})²+({p['b']})²={answer}."
        elif family=='complex_add_real':
            answer=p['a']+p['c'];stem=f"Cho z₁={p['a']}+({p['b']})i, z₂={p['c']}+({p['d']})i. Tính Re(z₁+z₂)."
            why=f"Cộng phần thực và phần ảo tương ứng. Phần thực bằng {p['a']}+({p['c']})={answer}."
        else:
            answer=p['a']*p['d']+p['b']*p['c']
            stem=f"Cho z₁={p['a']}+({p['b']})i, z₂={p['c']}+({p['d']})i. Tính Im(z₁z₂)."
            why=f"Nhân phân phối, dùng i²=−1: Im(z₁z₂)=ad+bc={p['a']}×({p['d']})+({p['b']})×({p['c']})={answer}."
    elif family=='integral_monomial':
        p=dict(a=v(1,7),power=ordinal+1,upper=v(2,5));answer=Rational(p['a']*p['upper']**(p['power']+1),p['power']+1)
        stem=f"Tính tích phân I=∫₀^{p['upper']} {p['a']}x^{p['power']} dx."
        why=f"Nguyên hàm của ax^n là ax^(n+1)/(n+1). Áp dụng Newton-Leibniz từ 0 tới {p['upper']}: I={answer}."
    elif family=='integral_mean_value':
        p=dict(a=v(2,8),b=v(-8,8),upper=ordinal+2);answer=Rational(p['a']*p['upper'],2)+p['b']
        stem=f"Tính giá trị trung bình của f(x)={p['a']}x+({p['b']}) trên đoạn [0;{p['upper']}]."
        why=f"Giá trị trung bình bằng (1/{p['upper']})∫₀^{p['upper']}f(x)dx={p['a']}×{p['upper']}/2+({p['b']})={answer}."
    elif family in ('cylinder_volume','cone_volume','sphere_volume','cylinder_surface_area','sphere_surface_area'):
        p=dict(radius=ordinal+2,height=v(3,13));radius=p['radius'];h=p['height']
        if family=='cylinder_volume':
            answer=pi*radius*radius*h;stem=f"Hình trụ bán kính đáy {radius} cm, chiều cao {h} cm. Tính thể tích chính xác."
            why=f"V=πr²h=π×{radius}²×{h}={answer} cm³."
        elif family=='cone_volume':
            answer=Rational(radius*radius*h,3)*pi;stem=f"Hình nón bán kính đáy {radius} cm, chiều cao {h} cm. Tính thể tích chính xác."
            why=f"V=(1/3)πr²h=π×{radius}²×{h}/3={answer} cm³."
        elif family=='sphere_volume':
            answer=Rational(4*radius**3,3)*pi;stem=f"Khối cầu bán kính {radius} cm. Tính thể tích chính xác."
            why=f"V=(4/3)πr³=(4/3)π×{radius}³={answer} cm³."
        elif family=='cylinder_surface_area':
            answer=2*pi*radius*(radius+h);stem=f"Hình trụ bán kính {radius} cm, chiều cao {h} cm. Tính diện tích toàn phần chính xác."
            why=f"S_tp=2πr²+2πrh=2π×{radius}×({radius}+{h})={answer} cm²."
        else:
            answer=4*pi*radius*radius;stem=f"Mặt cầu bán kính {radius} cm có diện tích bao nhiêu? Viết chính xác theo π."
            why=f"S=4πr²=4π×{radius}²={answer} cm²."
    elif family=='point_plane_distance':
        p=dict(a=v(1,4),b=v(1,4),c=v(1,4),d=v(-8,8),x=ordinal,y=v(-7,7),z=v(-7,7))
        dot=p['a']*p['x']+p['b']*p['y']+p['c']*p['z']+p['d'];answer=abs(dot)/sqrt(p['a']**2+p['b']**2+p['c']**2)
        stem=(f"Trong Oxyz, cho P({p['x']};{p['y']};{p['z']}) và mặt phẳng "
              f"({p['a']})x+({p['b']})y+({p['c']})z+({p['d']})=0. Tính khoảng cách từ P đến mặt phẳng.")
        why=f"d=|a xP+b yP+c zP+d|/√(a²+b²+c²)=|{dot}|/√({p['a']}²+{p['b']}²+{p['c']}²)={answer}."
    elif family=='vector_dot_3d':
        p=dict(x=ordinal+1,y=v(-9,9),z=v(-8,8),a=v(-8,8),b=v(-8,8),c=v(-8,8));answer=p['x']*p['a']+p['y']*p['b']+p['z']*p['c']
        stem=f"Trong Oxyz, u=({p['x']};{p['y']};{p['z']}), v=({p['a']};{p['b']};{p['c']}). Tính u·v."
        why=f"Tích vô hướng theo tọa độ u·v=x₁x₂+y₁y₂+z₁z₂={answer}."
    elif family=='midpoint_z_3d':
        p=dict(z1=ordinal*3-11,z2=v(-9,9));answer=Rational(p['z1']+p['z2'],2)
        stem=f"Trong Oxyz, A({v(-7,7)};{v(-7,7)};{p['z1']}), B({v(-7,7)};{v(-7,7)};{p['z2']}). Tính tọa độ z của trung điểm AB."
        why=f"Tung độ không gian của trung điểm là trung bình hai tọa độ z: ({p['z1']}+{p['z2']})/2={answer}."
    elif family=='sphere_radius_from_eq':
        p=dict(cx=v(-5,5),cy=v(-5,5),cz=v(-5,5),radius=ordinal+2)
        p['A']=-2*p['cx'];p['B']=-2*p['cy'];p['C']=-2*p['cz']
        p['D']=p['cx']**2+p['cy']**2+p['cz']**2-p['radius']**2;answer=p['radius']
        stem=f"Mặt cầu x²+y²+z²+({p['A']})x+({p['B']})y+({p['C']})z+({p['D']})=0 có bán kính bao nhiêu?"
        why=f"Hoàn thành bình phương theo x,y,z, ta có r²=(A²+B²+C²)/4−D={p['radius']**2}. Do r>0, r={answer}."
    elif family=='box_volume':
        p=dict(x=t+1,y=v(3,11),z=v(4,10));answer=p['x']*p['y']*p['z']
        stem=f"Khối hộp chữ nhật có ba kích thước {p['x']}, {p['y']}, {p['z']} cm. Tính thể tích."
        why=f"Thể tích hình hộp bằng tích ba kích thước: {p['x']}×{p['y']}×{p['z']}={answer} cm³."
    else:
        raise ValueError(f'family not implemented: {family}')
    if not stem or not why or answer is None: raise RuntimeError('incomplete question template')
    # Simple textbook methods may have a concise one-step computation. Add the
    # geometric/algebraic justification rather than a meaningless word-count pad.
    rationale = {
        'quadratic_discriminant': 'Biệt thức quyết định số nghiệm thực của phương trình bậc hai.',
        'circle_area': 'Áp dụng công thức tính diện tích phần hình phẳng bên trong đường tròn.',
        'circle_circumference': 'Độ dài đường tròn bằng hai lần tích của π và bán kính.',
        'circle_sector_area': 'Diện tích hình quạt bằng phần góc ở tâm tương ứng của cả hình tròn.',
        'circle_arc_length': 'Độ dài cung tỉ lệ thuận với số đo góc ở tâm tương ứng.',
        'pythagoras_missing_leg': 'Chỉ lấy căn không âm vì độ dài cạnh tam giác luôn dương.',
        'parallelogram_area_det': 'Giá trị tuyệt đối của định thức cho diện tích không âm.',
        'geometric_sequence_nth': 'Ở mỗi bước cấp số nhân, số hạng được nhân với công bội.',
        'logarithm_power': 'Cơ số lớn hơn 0 và khác 1 nên áp dụng được tính chất logarit.',
        'complex_modulus_squared': 'Dựa trên khoảng cách từ gốc O đến điểm biểu diễn số phức.',
        'cylinder_volume': 'Thể tích bằng diện tích đáy nhân chiều cao của hình trụ.',
        'cone_volume': 'Thể tích hình nón bằng một phần ba khối trụ cùng đáy và chiều cao.',
        'sphere_volume': 'Thay bán kính của khối cầu vào công thức thể tích.',
        'sphere_surface_area': 'Diện tích mặt cầu được tính từ bình phương bán kính.',
    }
    if family in rationale: why = rationale[family] + ' ' + why
    answer=_number(answer)
    result=dict(family=family, ordinal=ordinal,params=p,stem=stem,answer=str(answer),solution=why,difficulty=difficulty)
    result['fingerprint']=hashlib.sha256(re.sub(r'\s+',' ',stem.strip().casefold()).encode()).hexdigest()
    return result


def verify(q):
    """Recompute answer from parameters independently of prose/claimed answer.

    Only validates numerical/symbolic value plus basic constraints. It does not
    by itself certify semantic uniqueness or the pedagogical explanation.
    """
    f=q['family'];p=q['params'];x=Symbol('x');t=Symbol('t')
    try:
        if f=='set_intersection_from_union':
            expected=p['a']+p['b']-p['union'];assert 0<=expected<=min(p['a'],p['b'])
        elif f=='set_difference_size': expected=p['a']-p['common'];assert 0<=expected<=p['a']
        elif f=='set_symmetric_difference': expected=(p['a']-p['common'])+(p['b']-p['common']);assert expected>=0
        elif f=='set_power_set': expected=2**p['n'];assert 0<=p['n']<=24
        elif f=='linear_inequality_bound': expected=solve(p['a']*x+p['b']-p['c'],x)[0];assert p['a']>0
        elif f=='quadratic_discriminant': expected=p['b']*p['b']-4*p['a']*p['c'];assert p['a']!=0
        elif f=='quadratic_vertex_x': expected=solve(diff(p['a']*x*x+p['b']*x+p['c'],x),x)[0]
        elif f=='quadratic_vertex_y': expected=(p['a']*x*x+p['b']*x+p['c']).subs(x,Rational(-p['b'],2*p['a']))
        elif f=='system_sum_solution':
            z=Symbol('z');rr=solve([2*x+z-p['s'],x-z-p['d']],[x,z],dict=True);assert len(rr)==1
            expected=rr[0][x]+rr[0][z]
        elif f=='polynomial_remainder': expected=(p['a']*x*x+p['b']*x+p['c']).subs(x,p['t'])
        elif f=='circle_area': expected=pi*p['radius']**2
        elif f=='circle_circumference': expected=2*pi*p['radius']
        elif f=='circle_sector_area': expected=pi*p['radius']**2*p['angle']/360
        elif f=='circle_arc_length': expected=pi*p['radius']*p['angle']/180
        elif f=='pythagoras_hypotenuse': expected=sqrt(p['x']**2+p['y']**2);assert expected==p['h']
        elif f=='pythagoras_missing_leg': expected=sqrt(p['h']**2-p['x']**2);assert expected==p['y']
        elif f=='trapezoid_area': expected=Rational((p['base1']+p['base2'])*p['h'],2)
        elif f=='heron_area':
            s=Rational(p['a']+p['b']+p['c'],2);expected=sqrt(s*(s-p['a'])*(s-p['b'])*(s-p['c']));assert s>max(p.values())
        elif f=='cosine_rule_side_square': expected=p['a']**2+p['b']**2-2*p['a']*p['b']*cos(pi*p['angle']/180)
        elif f=='midpoint_x_2d': expected=Rational(p['x1']+p['x2'],2)
        elif f=='distance_2d': expected=sqrt(p['dx']**2+p['dy']**2)
        elif f=='slope_2d': expected=Rational(p['dy'],p['dx']);assert p['dx']!=0
        elif f=='line_intersection_x': expected=solve(p['m1']*x+p['b1']-(p['m2']*x+p['b2']),x)[0];assert p['m1']!=p['m2']
        elif f=='vector_dot_2d': expected=p['x']*p['u']+p['y']*p['w']
        elif f=='vector_norm_sq_2d': expected=p['x']**2+p['y']**2
        elif f=='parallelogram_area_det': expected=abs(p['x']*p['w']-p['y']*p['u'])
        elif f=='triangle_area_coords': expected=Rational(abs(p['x']*p['w']-p['y']*p['u']),2)
        elif f in ('binomial_coefficient','combination_count'): expected=binomial(p['n'],p['k']);assert 0<=p['k']<=p['n']
        elif f=='permutation_count': expected=factorial(p['n']);assert p['n']>=0
        elif f=='classical_probability': expected=Rational(p['k'],p['n']);assert 0<=p['k']<=p['n']
        elif f=='urn_two_success': expected=binomial(p['k'],2)/binomial(p['n'],2);assert 2<=p['k']<=p['n']
        elif f=='arithmetic_mean': expected=Rational(sum(p['values']),len(p['values']))
        elif f=='population_variance':
            mean=Rational(sum(p['values']),len(p['values']));expected=sum((n-mean)**2 for n in p['values'])/len(p['values'])
        elif f=='geometric_sequence_nth': expected=p['u1']*p['q']**(p['n']-1)
        elif f=='geometric_sequence_sum': expected=sum(p['u1']*p['q']**j for j in range(p['n']))
        elif f=='polynomial_limit': expected=(p['a']*x*x+p['b']*x+p['c']).subs(x,p['t'])
        elif f=='derivative_power_at': expected=diff(p['a']*x**p['power'],x).subs(x,p['t'])
        elif f=='quadratic_second_derivative': expected=diff(p['a']*x*x+p['b']*x+p['c'],x,2)
        elif f=='conditional_probability': expected=Rational(p['joint'],p['given']);assert 0<=p['joint']<=p['given']<=p['n']
        elif f=='special_angle_sine': expected=sin(pi*p['angle']/180)
        elif f=='trig_pythagorean_cos2': expected=1-Rational(p['m']**2,p['n']**2);assert 0<p['m']<p['n']
        elif f=='exponential_equation': expected=solve(p['base']**x-p['base']**p['power'],x)[0];assert p['base']>1
        elif f=='logarithm_equation': expected=p['base']**p['power'];assert p['base']>1
        elif f=='logarithm_power': expected=p['power'];assert p['value']==p['base']**p['power']
        elif f=='complex_modulus_squared': expected=p['a']**2+p['b']**2
        elif f=='complex_add_real': expected=(p['a']+p['c'])
        elif f=='complex_multiply_imag': expected=(p['a']+p['b']*Symbol('I'))*(p['c']+p['d']*Symbol('I'))
        elif f=='integral_monomial': expected=integrate(p['a']*x**p['power'],(x,0,p['upper']))
        elif f=='integral_mean_value': expected=integrate(p['a']*x+p['b'],(x,0,p['upper']))/p['upper']
        elif f=='cylinder_volume': expected=pi*p['radius']**2*p['height']
        elif f=='cone_volume': expected=pi*p['radius']**2*p['height']/3
        elif f=='sphere_volume': expected=4*pi*p['radius']**3/3
        elif f=='cylinder_surface_area': expected=2*pi*p['radius']*(p['radius']+p['height'])
        elif f=='sphere_surface_area': expected=4*pi*p['radius']**2
        elif f=='point_plane_distance': expected=abs(p['a']*p['x']+p['b']*p['y']+p['c']*p['z']+p['d'])/sqrt(p['a']**2+p['b']**2+p['c']**2)
        elif f=='vector_dot_3d': expected=p['x']*p['a']+p['y']*p['b']+p['z']*p['c']
        elif f=='midpoint_z_3d': expected=Rational(p['z1']+p['z2'],2)
        elif f=='sphere_radius_from_eq': expected=sqrt(Rational(p['A']**2+p['B']**2+p['C']**2,4)-p['D']);assert expected>0
        elif f=='box_volume': expected=p['x']*p['y']*p['z']
        else: return False,{'error':'missing independent verifier'}
        if f=='complex_multiply_imag':
            # Expand with actual imaginary unit. Avoid relying on an unevaluated symbol I.
            from sympy import I, im, expand
            expected=im(expand((p['a']+p['b']*I)*(p['c']+p['d']*I)))
        if simplify(sympify(q['answer'])-expected)!=0:
            return False,{'error':'answer differs from independent recomputation','recomputed':str(expected)}
        if len(q['stem'])<20 or len(q['solution'])<35:
            return False,{'error':'incomplete question or solution'}
        if q['difficulty'] not in {'nền tảng','trung cấp','nâng cao'}:
            return False,{'error':'invalid difficulty'}
        return True,dict(engine='sympy-expanded-v113', answer=str(simplify(expected)),
                         numeric_math_verified=True, method_independence='curated-distinct-objective-not-external-review')
    except Exception as exc:
        return False,{'error':f'{type(exc).__name__}: {exc}'}
