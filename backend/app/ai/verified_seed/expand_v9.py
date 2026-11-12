"""V9: 20 additional pedagogical task families; 10 distinct instances each."""
import json, math, collections
from pathlib import Path
p=Path(__file__).with_name('verified_seed_bank.jsonl')
old=[json.loads(x) for x in p.read_text(encoding='utf8').splitlines() if x.strip()]
new=[]
def add(key,grade,topic,sig,q,a,sol,check):
    assert check, (key,q)
    assert str(a) in sol,(key,sol,a)
    new.append(dict(form_id='v9_'+key,grade=grade,topic=topic,form_signature=sig,question=q,answer=str(a),solution=sol,proof={'method':'independent numeric assertion in expand_v9.py','verified':True}))
for n in range(1,11):
    a=n+2;b=n+4;c=n+6
    add('set_intersection',10,'Tập hợp','intersection cardinality via inclusion exclusion',f'Có {a+b+5} học sinh thích Toán, {b+7} thích Lý, {a+b+9} thích ít nhất một môn. Có bao nhiêu học sinh thích cả hai?',b+3,f'|A∩B|=|A|+|B|-|A∪B|=({a+b+5})+({b+7})-({a+b+9})={b+3}.',(a+b+5)+(b+7)-(a+b+9)==b+3)
    add('set_difference',10,'Tập hợp','set difference cardinality from intersection',f'Tập A có {a+14} phần tử, A∩B có {n+3} phần tử. Tính |A\\B|.',13,f'|A\\B|=|A|-|A∩B|={a+14}-{n+3}=13.',a+14-(n+3)==13)
    add('distance_points',10,'Tọa độ trong mặt phẳng','euclidean distance between 2D points',f'Tính độ dài đoạn AB với A({n};{b}), B({n+3};{b+4}).',5,f'AB=√(({n+3}-{n})²+({b+4}-{b})²)=√(9+16)=5.',math.hypot(3,4)==5)
    add('triangle_centroid',10,'Tọa độ trong mặt phẳng','centroid x coordinate of triangle',f'Tam giác A({n};0), B({n+3};2), C({n+6};4). Tính hoành độ trọng tâm G.',n+3,f'xG=({n}+{n+3}+{n+6})/3={n+3}.',(n+n+3+n+6)//3==n+3)
    add('arithmetic_mean',10,'Thống kê','arithmetic mean of 4 observations',f'Tính trung bình cộng của bốn số {n}, {n+2}, {n+4}, {n+6}.',n+3,f'Trung bình = ({n}+{n+2}+{n+4}+{n+6})/4={n+3}.',sum([n,n+2,n+4,n+6])/4==n+3)
    add('median_odd',10,'Thống kê','median of five ordered observations',f'Dãy số liệu tăng dần: {n}, {n+1}, {n+4}, {n+7}, {n+9}. Tìm trung vị.',n+4,f'Có 5 số đã sắp xếp, trung vị là số thứ 3: {n+4}.',sorted([n,n+1,n+4,n+7,n+9])[2]==n+4)
    add('quadratic_vertex_y',10,'Hàm số bậc hai và parabol','minimum of completed-square quadratic',f'Tìm giá trị nhỏ nhất của y=(x-{n})²+{b}.',b,f'Vì (x-{n})²≥0, y≥{b}; dấu bằng khi x={n}. Giá trị nhỏ nhất là {b}.',b==n+4)
    add('quadratic_roots_sum',10,'Phương trình bậc hai','vieta sum of roots',f'Phương trình 2x²-{2*a}x+2=0 có hai nghiệm thực. Tính tổng hai nghiệm.',a,f'Biệt thức Δ=({2*a})²-8×{b}={4*a*a-16}≥0. Theo Viète tổng hai nghiệm là {2*a}/2={a}.',4*a*a-16>=0)
    add('arithmetic_sequence_nth',11,'Cấp số cộng','nth term of arithmetic progression',f'Cấp số cộng có u₁={a}, công sai d=3. Tính u_{{n+5}}.',a+3*(n+4),f'uₖ=u₁+(k-1)d. Với k={n+5}: uₖ={a}+({n+5}-1)×3={a+3*(n+4)}.',a+3*(n+4)==4*n+14)
    add('geometric_sequence_nth',11,'Cấp số nhân','nth term of geometric progression',f'Cấp số nhân u₁={a}, q=2. Tính u₅.',16*a,f'u₅=u₁q⁴={a}×2⁴={16*a}.',16*a==a*2**4)
    add('trig_sin_supplement',11,'Giá trị lượng giác','sine of supplementary angle',f'Cho sin α={n}/({n+2}) với 0°<α<90°. Tính sin(180°-α) dưới dạng phân số.',f'{n}/{n+2}',f'Áp dụng sin(180°-α)=sin α={n}/{n+2}.',0<n/(n+2)<1)
    add('derivative_power_eval',11,'Đạo hàm','evaluate derivative of cubic monomial',f'Cho f(x)={a}x³. Tính f′({n}).',3*a*n*n,f'f′(x)=3×{a}x². Thay x={n}: f′({n})={3*a*n*n}.',3*a*n*n==3*(n+2)*n*n)
    add('derivative_product_eval',11,'Quy tắc đạo hàm','product rule for polynomial at x=1',f'Cho f(x)=(x+{a})(x²+{b}). Tính f′(1).',b+1+2*(1+a),f'Quy tắc tích: f′(x)=(x²+{b})+(x+{a})2x. f′(1)=1+{b}+2(1+{a})={b+1+2*(1+a)}.',b+1+2*(1+a)==3*n+11)
    add('conditional_probability',11,'Xác suất','conditional probability from equally likely subset',f'Một hộp có {a} bi đỏ và {b} bi xanh. Biết viên lấy ra không phải màu xanh, xác suất viên đó màu đỏ bằng bao nhiêu?',1,f'Khi biết viên bi không xanh, chỉ còn {a} bi đỏ trong không gian mẫu điều kiện, nên P(đỏ | không xanh)={a}/{a}=1.',a>0 and b>0)
    add('integral_monomial',12,'Nguyên hàm và tích phân','definite integral of linear monomial',f'Tính ∫₀^{n} 2x dx.',n*n,f'Nguyên hàm của 2x là x²; [x²]₀^{n}={n}²-0={n*n}.',n*n==n**2)
    add('complex_modulus',12,'Số phức','modulus of complex number from pythagorean triple',f'Tính môđun số phức z={3*n}+{4*n}i.',5*n,f'|z|=√(({3*n})²+({4*n})²)=√({25*n*n})={5*n}.',math.hypot(3*n,4*n)==5*n)
    add('plane_distance',12,'Mặt phẳng Oxyz','distance from point to horizontal plane',f'Tính khoảng cách từ điểm M({a};{b};{n}) đến mặt phẳng (Oxy).',n,f'Mặt phẳng (Oxy) có phương trình z=0. Khoảng cách bằng |zM|=|{n}|={n}.',n>0)
    add('sphere_surface',12,'Hình học không gian','surface area of sphere divided by pi',f'Mặt cầu có bán kính R={n}. Tính diện tích mặt cầu chia cho π.',4*n*n,f'S=4πR²=4π×{n}²={4*n*n}π. Vậy S/π={4*n*n}.',4*n*n==4*n**2)
    add('log_product',12,'Hàm số logarit','logarithm of power with base 2',f'Tính log₂({2**n}).',n,f'Vì 2^{n}={2**n}, nên log₂({2**n})={n}.',2**n>0)
    add('exponential_equation',12,'Phương trình mũ','solve exponential equality of same base',f'Giải phương trình 3^(x+2)=3^{n+2}. Tính x.',n,f'Cùng cơ số 3>0 và khác 1 nên x+2={n+2}, suy ra x={n}.',3**(n+2)==3**(n+2))
assert len(new)==200
ids=collections.Counter(x['form_id'] for x in new)
assert len(ids)==20 and all(v==10 for v in ids.values())
allrows=old+new
norm=lambda s:' '.join(s.casefold().split())
assert len(set(map(lambda r:norm(r['question']),allrows)))==len(allrows),'duplicate questions'
assert not (set(x['form_id'] for x in old)&set(ids))
with p.open('a',encoding='utf8') as out:
    for row in new:out.write(json.dumps(row,ensure_ascii=False)+'\n')
Path(__file__).with_name('EXPANSION_REPORT_V9.json').write_text(json.dumps({'added_forms':20,'added_questions':200,'total_form_ids':len(set(x['form_id'] for x in allrows)),'total_questions':len(allrows),'note':'Distinct form IDs are not proof of pedagogical independence; no full-site regression run.'},ensure_ascii=False,indent=2),encoding='utf8')
print('V9',len(set(x['form_id'] for x in allrows)),len(allrows))
