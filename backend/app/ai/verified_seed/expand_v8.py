"""Curated V8 extension: 20 problem families with 10 worked examples each."""
import json, math
from fractions import Fraction
from pathlib import Path
p=Path(__file__).with_name('verified_seed_bank.jsonl')
old=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
new=[]
def add(fid,topic,grade,signature,q,answer,solution):
    new.append(dict(form_id='v8_'+fid,topic=topic,grade=grade,form_signature=signature,question=q,answer=str(answer),solution=solution,proof={'method':'deterministic arithmetic or exact rational identity; manual review still required'}))
def f(x):return str(x)
for n in range(1,11):
 a=n+2;b=n+3;c=n+5
 # 10th grade
 add('set_union_cardinality','Tập hợp',10,'cardinality of union from inclusion-exclusion',f'Lớp có {a+b+n} bạn học tiếng Anh, {b+n} bạn học tiếng Pháp, {n} bạn học cả hai. Có bao nhiêu bạn học ít nhất một trong hai?',a+2*b+n,f'Áp dụng |A∪B|=|A|+|B|-|A∩B|=({a+b+n})+({b+n})-{n}={a+2*b+n}.')
 add('linear_inequality','Bất phương trình',10,'solve positive-coefficient linear inequality for least integer',f'Tìm số nguyên nhỏ nhất x thỏa mãn {a}x+{b}>{a*(n+1)+b}.',n+2,f'Trừ {b}, chia cho {a}>0: x>{n+1}. Số nguyên nhỏ nhất là {n+2}.')
 add('quadratic_discriminant','Phương trình bậc hai',10,'calculate discriminant of quadratic polynomial',f'Tính biệt thức Δ của {a}x²+{2*b}x+{c}=0.',(2*b)**2-4*a*c,f'Δ=B²-4AC=({2*b})²-4×{a}×{c}={(2*b)**2-4*a*c}.')
 add('vector_linear_combination','Vectơ',10,'first coordinate of vector linear combination',f'Cho u=({a};{b}), v=({c};{-n}). Tính hoành độ của 2u-3v.',2*a-3*c,f'Hoành độ 2u-3v là 2×{a}-3×{c}={2*a-3*c}.')
 add('circle_area_annulus','Đường tròn',10,'area of annulus divided by pi',f'Hai đường tròn đồng tâm có bán kính {b} và {a}. Tính diện tích vành khăn chia cho π.',b*b-a*a,f'S=π(R²-r²)=π({b}²-{a}²)={b*b-a*a}π. Kết quả {b*b-a*a}.')
 add('line_intercept','Đường thẳng',10,'x intercept of line in intercept-friendly form',f'Đường thẳng y={a}x-{a*b} cắt trục Ox tại điểm có hoành độ bao nhiêu?',b,f'Cho y=0: {a}x-{a*b}=0, nên x={b}.')
 add('count_permutations','Quy tắc đếm',10,'ordered selection of two distinct objects',f'Có {c} cuốn sách khác nhau. Chọn hai cuốn đặt vào hai vị trí trái và phải. Có bao nhiêu cách?',c*(c-1),f'Vị trí trái có {c} lựa chọn, vị trí phải còn {c-1}; theo quy tắc nhân có {c*(c-1)} cách.')
 # 11th grade
 add('arithmetic_mean_terms','Cấp số cộng',11,'find arithmetic mean of two terms in arithmetic progression',f'Ba số {a}, x, {a+2*b} lập thành cấp số cộng. Tìm x.',a+b,f'Số giữa bằng trung bình cộng hai số ngoài: x=({a}+{a+2*b})/2={a+b}.')
 add('geometric_ratio','Cấp số nhân',11,'recover common ratio from consecutive nonzero terms',f'Cấp số nhân có u₃={a*b}, u₄={a*b*c}. Tìm công bội q.',c,f'Vì u₃≠0, q=u₄/u₃={a*b*c}/{a*b}={c}.')
 add('limit_polynomial_ratio','Giới hạn hàm số',11,'limit at infinity of ratio of equal-degree polynomials',f'Tính lim khi x→+∞ của ({a}x²+{b}x+1)/({c}x²+2). Viết kết quả dạng phân số tối giản.',f(Fraction(a,c)),f'Chia tử và mẫu cho x², các số hạng chứa 1/x và 1/x² tiến về 0. Giới hạn bằng {a}/{c}={f(Fraction(a,c))}.')
 add('derivative_product','Quy tắc đạo hàm',11,'evaluate product rule at zero',f'Cho f(x)=({a}x+{b})(x²+{c}x+1). Tính f\'(0).',a+b*c,f'Đặt u={a}x+{b}, v=x²+{c}x+1. f\'=u\'v+uv\'. Tại x=0: {a}×1+{b}×{c}={a+b*c}.')
 add('binomial_probability','Xác suất',11,'probability of exactly one success in two independent trials',f'Hai lần thử độc lập, xác suất thành công mỗi lần là 1/{b}. Tính xác suất đúng một lần thành công, dạng phân số tối giản.',f(Fraction(2*(b-1),b*b)),f'Có hai thứ tự thành công-thất bại. P=2×(1/{b})×({b-1}/{b})={f(Fraction(2*(b-1),b*b))}.')
 add('trig_cos_double','Công thức lượng giác',11,'cosine double angle from cosine of acute angle',f'Cho góc nhọn α có cos α={a}/{a+b}. Tính cos 2α dưới dạng phân số tối giản.',f(2*Fraction(a,a+b)**2-1),f'Dùng cos 2α=2cos²α-1=2×({a}/{a+b})²-1={f(2*Fraction(a,a+b)**2-1)}.')
 add('continuous_parameter','Hàm số liên tục',11,'choose point value to remove removable discontinuity',f'Cho f(x)=(x²-{a*a})/(x-{a}) khi x≠{a}, và f({a})=k. Tìm k để f liên tục tại x={a}.',2*a,f'Với x≠{a}, rút gọn (x-{a})(x+{a})/(x-{a})=x+{a}. Giới hạn tại {a} bằng {2*a}, nên k={2*a}.')
 # 12th grade
 add('integral_quadratic','Nguyên hàm và tích phân',12,'integral of quadratic polynomial on unit interval',f'Tính ∫ từ 0 đến 1 của ({3*a}x²+{2*b}x+{c}) dx.',a+b+c,f'Nguyên hàm là {a}x³+{b}x²+{c}x. Thay cận 1 và 0 được {a}+{b}+{c}={a+b+c}.')
 add('logarithm_equation','Phương trình logarit',12,'solve log equation using base power and linear argument',f'Giải log cơ số {a} của (x+{b})=2. Tìm x.',a*a-b,f'Theo định nghĩa logarit, x+{b}={a}²={a*a}. Suy ra x={a*a-b}, thỏa điều kiện x+{b}>0.')
 add('complex_division_real','Số phức',12,'real part of complex quotient with conjugate denominator',f'Tính phần thực của z=({a}+{b}i)/(1+i), dưới dạng phân số tối giản.',f(Fraction(a+b,2)),f'Nhân cả tử và mẫu với 1-i: z=[({a}+{b}i)(1-i)]/2. Phần thực bằng ({a}+{b})/2={f(Fraction(a+b,2))}.')
 add('sphere_surface','Hình khối và thể tích cơ bản',12,'sphere surface area divided by pi',f'Mặt cầu bán kính {a}. Tính diện tích mặt cầu chia cho π.',4*a*a,f'S=4πr²=4π×{a}²={4*a*a}π. S/π={4*a*a}.')
 add('plane_distance','Mặt phẳng Oxyz',12,'distance of point to coordinate plane Oxy',f'Trong Oxyz, khoảng cách từ M({a};{-b};{-c}) đến mặt phẳng Oxy bằng bao nhiêu?',c,f'Mặt phẳng Oxy có phương trình z=0. Khoảng cách bằng |z_M|=|-{c}|={c}.')
 add('derivative_monotonicity','Tính đơn điệu',12,'critical abscissa for increasing quadratic derivative',f'Cho f(x)=x²-{2*a}x+{b}. Hàm số đồng biến trên khoảng (k;+∞). Tìm k là nghiệm f\'(k)=0.',a,f'f\'(x)=2x-{2*a}; f\'(x)>0 khi x>{a}, nên k={a}.')
assert len(new)==200
oldids={r['form_id'] for r in old}; assert not oldids.intersection({r['form_id'] for r in new})
allrows=old+new
assert len({(r['form_id'],r['question']) for r in allrows})==len(allrows)
assert len({r['question'].strip().casefold() for r in allrows})==len(allrows)
assert all(r['answer'] and len(r['solution'])>15 for r in new)
assert len({r['form_signature'] for r in new})==20
p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in allrows),encoding='utf-8')
(Path(__file__).with_name('EXPANSION_REPORT_V8.json')).write_text(json.dumps({'previous_questions':len(old),'new_forms':20,'new_questions':len(new),'total_questions':len(allrows),'total_form_ids':len({r['form_id'] for r in allrows}),'note':'Form signatures are descriptive, not a proof of semantic independence; verify mathematical correctness and app integration separately.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Expanded',len(old),'to',len(allrows),'questions;',len({r['form_id'] for r in allrows}),'form IDs')
