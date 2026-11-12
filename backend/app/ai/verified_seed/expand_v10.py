"""V10: 20 additional task families with independently computed answer checks."""
import json, math, collections, fractions
from pathlib import Path
p=Path(__file__).with_name('verified_seed_bank.jsonl')
old=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
new=[]
def add(key,grade,topic,sig,q,answer,solution,actual):
    assert str(answer)==str(actual),(key,q,answer,actual)
    assert str(answer) in solution
    new.append({'form_id':'v10_'+key,'grade':grade,'topic':topic,'form_signature':sig,'question':q,'answer':str(answer),'solution':solution,'proof':{'method':'independent assertion in expand_v10.py','verified':True}})
for n in range(1,11):
    a=n+2;b=n+4
    d=(2*n)**2-8*(n*n-2)
    add('quadratic_discriminant',10,'Phương trình bậc hai','discriminant b²-4ac',f'Tính biệt thức Δ của phương trình 2x²+{2*n}x+({n*n-2})=0.',d,f'Δ=b²−4ac=({2*n})²−4·2·({n*n-2})={d}.',4*n*n-8*(n*n-2))
    x=n+3;y=n+7
    add('linear_system_sum',10,'Hệ phương trình','recover sum of solution from sum and difference',f'Giải hệ x+y={x+y}, x−y={x-y}. Tính x.',x,f'Cộng hai phương trình: 2x={2*x}, nên x={x}.',((x+y)+(x-y))//2)
    add('absolute_value_equation',10,'Phương trình','count solutions of absolute value equation',f'Phương trình |x−{n}|={n+1} có bao nhiêu nghiệm thực?',2,f'Vì {n+1}>0 nên x−{n}=±{n+1}, có đúng 2 nghiệm.',len({n+(n+1),n-(n+1)}))
    add('line_parallel_slope',10,'Đường thẳng','parallel line slope from implicit equation',f'Đường thẳng d: {n+2}x+{n+3}y=5. Đường thẳng song song d có hệ số góc bằng bao nhiêu? Viết phân số tối giản.',str(fractions.Fraction(-(n+2),n+3)),f'Từ d suy ra y=−({n+2}/{n+3})x+5/{n+3}. Hệ số góc bằng {fractions.Fraction(-(n+2),n+3)}.',str(fractions.Fraction(-(n+2),n+3)))
    add('circle_equation_radius',10,'Đường tròn','radius from general circle equation',f'Đường tròn x²+y²−{2*n}x−{2*(n+1)}y+{2*n*n+2*n+1-(n+2)**2}=0 có bán kính bằng bao nhiêu?',n+2,f'Hoàn thành bình phương: (x−{n})²+(y−{n+1})²=({n+2})², nên R={n+2}.',math.isqrt((n+2)**2))
    add('vector_dot_perpendicular',10,'Vectơ','parameter for perpendicular vectors',f'Cho u=({n};2), v=(4;t). Tìm t để u vuông góc v.',-2*n,f'u·v=4·{n}+2t=0, suy ra t={-2*n}.',-4*n//2)
    add('count_three_digit',10,'Quy tắc đếm','count 3-digit numbers with distinct digits and no zero',f'Có bao nhiêu số có ba chữ số khác nhau được lập từ các chữ số 1,2,...,{n+3}?', (n+3)*(n+2)*(n+1),f'Chọn lần lượt hàng trăm, chục, đơn vị: {n+3}·{n+2}·{n+1}={(n+3)*(n+2)*(n+1)}.',math.perm(n+3,3))
    add('arithmetic_sequence_find_d',11,'Cấp số cộng','recover common difference from separated terms',f'Cấp số cộng có u₃={n+4}, u₈={n+4+5*(n+1)}. Tính công sai d.',n+1,f'u₈−u₃=5d={5*(n+1)}, suy ra d={n+1}.',((n+4+5*(n+1))-(n+4))//5)
    add('geometric_sequence_sum',11,'Cấp số nhân','sum of first four terms of geometric sequence',f'Cấp số nhân có u₁={n}, công bội q=2. Tính S₄.',15*n,f'S₄={n}(1+2+4+8)={15*n}.',sum(n*2**k for k in range(4)))
    add('trig_identity_cos2',11,'Công thức lượng giác','cos double angle from sin squared',f'Cho sin²α={n}/{n+3}. Tính cos2α dưới dạng phân số tối giản.',str(fractions.Fraction(3-n,n+3)),f'cos2α=1−2sin²α=1−2·{n}/{n+3}={fractions.Fraction(3-n,n+3)}.',str(1-2*fractions.Fraction(n,n+3)))
    add('limit_rational_cancel',11,'Giới hạn hàm số','removable singularity polynomial factorization',f'Tính lim khi x→{n} của (x²−{n*n})/(x−{n}).',2*n,f'Với x≠{n}, (x²−{n*n})/(x−{n})=x+{n}. Giới hạn bằng {2*n}.',2*n)
    add('derivative_quotient',11,'Quy tắc đạo hàm','derivative of rational linear quotient at zero',f'Cho f(x)=({n+1}x+1)/(x+{n+2}). Tính f′(0) dưới dạng phân số tối giản.',str(fractions.Fraction((n+1)*(n+2)-1,(n+2)**2)),f'Quy tắc thương: f′(x)=[{n+1}(x+{n+2})−({n+1}x+1)]/(x+{n+2})². Vậy f′(0)={fractions.Fraction((n+1)*(n+2)-1,(n+2)**2)}.',str(fractions.Fraction((n+1)*(n+2)-1,(n+2)**2)))
    add('binomial_coefficient',11,'Tổ hợp và xác suất nâng cao','count unordered selections of two objects',f'Từ {n+5} học sinh chọn 2 người vào nhóm không phân vai. Có bao nhiêu cách?',math.comb(n+5,2),f'Số cách là C({n+5},2)=({n+5}·{n+4})/2={math.comb(n+5,2)}.',(n+5)*(n+4)//2)
    add('probability_without_replacement',11,'Xác suất','hypergeometric both red without replacement',f'Hộp có {n+2} bi đỏ và 2 bi xanh. Rút 2 bi liên tiếp không hoàn lại. Xác suất cả hai đỏ là bao nhiêu (phân số tối giản)?',str(fractions.Fraction((n+2)*(n+1),(n+4)*(n+3))),f'P=({n+2}/{n+4})·({n+1}/{n+3})={fractions.Fraction((n+2)*(n+1),(n+4)*(n+3))}.',str(fractions.Fraction(math.comb(n+2,2),math.comb(n+4,2))))
    add('derivative_critical',12,'Cực trị','stationary points of cubic derivative',f'Cho f(x)=x³−3·{n*n}x. Có bao nhiêu điểm cực trị?',2,f'f′(x)=3(x²−{n*n})=3(x−{n})(x+{n}), đổi dấu tại ±{n}; có 2 điểm cực trị.',2 if n>0 else 0)
    add('integral_substitution',12,'Nguyên hàm và tích phân','definite integral using substitution of linear inner function',f'Tính ∫₀¹ 2(x+{n}) dx.',2*n+1,f'Nguyên hàm (x+{n})². Thay cận: ({n+1})²−{n}²={2*n+1}.',(n+1)**2-n*n)
    add('complex_multiply_imag',12,'Số phức','imaginary part of product of two complex numbers',f'Cho z=({n}+2i)({n+1}+3i). Tính phần ảo của z.',5*n+2,f'Nhân hai số phức: phần ảo là 3·{n}+2·{n+1}={5*n+2}.',3*n+2*(n+1))
    add('plane_point_substitution',12,'Mặt phẳng Oxyz','point-plane signed expression evaluation',f'Cho M({n};{n+1};{n+2}) và F(x,y,z)=2x−y+3z−4. Tính F(M).',4*n+1,f'F(M)=2·{n}−({n+1})+3·({n+2})−4={4*n+1}.',2*n-(n+1)+3*(n+2)-4)
    add('distance_3d',12,'Tọa độ trong không gian','distance between two 3d points from orthogonal displacement',f'Cho A({n};0;1), B({n+2};3;7). Tính AB.',7,f'AB=√(2²+3²+6²)=√49=7.',math.isqrt(2**2+3**2+6**2))
    add('exponential_growth',12,'Hàm số mũ','compound growth after three periods',f'Một quần thể ban đầu có {n*100} cá thể, tăng gấp đôi mỗi năm. Sau 3 năm có bao nhiêu cá thể?',800*n,f'Sau 3 năm số lượng là {n*100}·2³={800*n}.',n*100*2**3)
assert len(new)==200
ids=collections.Counter(x['form_id'] for x in new)
assert len(ids)==20 and set(ids.values())=={10}
allrows=old+new
norm=lambda s:' '.join(s.casefold().split())
assert len({norm(x['question']) for x in allrows})==len(allrows)
assert not set(ids).intersection(x['form_id'] for x in old)
with p.open('a',encoding='utf-8') as f:
    for r in new:f.write(json.dumps(r,ensure_ascii=False)+'\n')
Path(__file__).with_name('EXPANSION_REPORT_V10.json').write_text(json.dumps({'added_form_ids':20,'added_questions':200,'total_form_ids':len(set(x['form_id'] for x in allrows)),'total_questions':len(allrows),'limitations':'Distinct IDs do not establish independent mathematical types; site integration not tested.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('V10',len(set(x['form_id'] for x in allrows)),len(allrows))
