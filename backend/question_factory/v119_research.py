"""V119: authored, topic-bound candidate methods. 10 deterministic examples per method.

These are candidate methods only: automatic mathematical checks do not certify
novelty against the archived bank, or replace an expert pedagogy review.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from collections import Counter
from pathlib import Path
from math import comb
import json, re
from sympy import Integer as I, Rational as R, simplify, sympify, sqrt, pi

@dataclass(frozen=True)
class Method:
    family: str
    topic: str
    title: str
    signature: str
    skill: str
    grade: int
    difficulty: str = 'trung cấp'
    real_world: bool = False

METHODS=[]
HANDLERS={}

def method(code, topic, title, signature, skill, grade, difficulty='trung cấp', real_world=False):
    def wrap(f):
        m=Method('v119_'+code, topic, title, signature, skill, grade, difficulty, real_world)
        if m.family in HANDLERS:raise ValueError(m.family)
        METHODS.append(m);HANDLERS[m.family]=f
        return f
    return wrap

# A: Sets. Ten *different* mathematical objectives, not ten presentation formats.
@method('set_symmetric_difference','tap_hop','Số phần tử hiệu đối xứng','set-symmetric-difference-two-set-count','|A △ B|=|A|+|B|−2|A∩B|',10)
def _(t):
    a=18+2*t;b=15+t;i=3+t//2
    return {'a':a,'b':b,'i':i}, f'Cho |A|={a}, |B|={b}, |A∩B|={i}. Tính số phần tử thuộc đúng một trong A và B.', I(a+b-2*i),f'Phần chỉ thuộc A có {a}-{i}, phần chỉ thuộc B có {b}-{i}. Cộng lại được {a+b-2*i} phần tử.'

@method('set_triple_union','tap_hop','Hợp ba tập dùng cộng trừ','set-three-way-inclusion-exclusion','|A∪B∪C| từ ba giao đôi và giao ba',10)
def _(t):
    a=20+2*t;b=21+t;c=23+t;ab=6+t//2;ac=5+t//2;bc=7+t//2;abc=2+t//4
    v=a+b+c-ab-ac-bc+abc
    return dict(a=a,b=b,c=c,ab=ab,ac=ac,bc=bc,abc=abc),f'Cho |A|={a}, |B|={b}, |C|={c}; |A∩B|={ab}, |A∩C|={ac}, |B∩C|={bc}, |A∩B∩C|={abc}. Tìm |A∪B∪C|.',I(v),f'Cộng ba số phần tử, trừ ba giao đôi rồi cộng lại giao ba: {a}+{b}+{c}−{ab}−{ac}−{bc}+{abc}={v}.'

@method('set_exactly_one_of_three','tap_hop','Đếm phần tử thuộc đúng một trong ba tập','set-exactly-one-three-membership-count','Tách đúng một theo cộng-trừ hai lần giao đôi',10)
def _(t):
    a=25+t;b=26+t;c=28+t;ab=6+t//2;ac=7+t//2;bc=8+t//2;abc=2+t//4
    v=a+b+c-2*(ab+ac+bc)+3*abc
    return dict(a=a,b=b,c=c,ab=ab,ac=ac,bc=bc,abc=abc),f'Ba tập hữu hạn có |A|={a}, |B|={b}, |C|={c}; |A∩B|={ab}, |A∩C|={ac}, |B∩C|={bc}, |A∩B∩C|={abc}. Có bao nhiêu phần tử thuộc đúng một tập?',I(v),f'Cộng kích thước ba tập, mỗi phần tử ở đúng hai bị đếm hai lần nên trừ hai lần tổng giao đôi; giao ba cần cộng ba lần. Kết quả = {v}.'

@method('set_universe_complement_union','tap_hop','Phần bù của hợp ba tập','set-universe-complement-of-triple-union','Lấy |U| trừ |A∪B∪C|',10)
def _(t):
    a=15+t;b=16+t;c=17+t;ab=4+t//3;ac=4+t//3;bc=5+t//3;abc=2
    union=a+b+c-ab-ac-bc+abc;u=union+10+t
    return dict(u=u,a=a,b=b,c=c,ab=ab,ac=ac,bc=bc,abc=abc),f'Trong tập U gồm {u} phần tử, ba tập con A,B,C có số phần tử {a},{b},{c}; giao đôi lần lượt {ab},{ac},{bc}, giao ba {abc}. Có bao nhiêu phần tử không thuộc tập nào?',I(u-union),f'Tính |A∪B∪C|={union} bằng nguyên lý cộng trừ. Số phần tử không thuộc tập nào là {u}−{union}={u-union}.'

@method('set_proper_nonempty_subsets','tap_hop','Số tập con thực sự và khác rỗng','set-count-nonempty-proper-subsets','Loại ∅ và tập ban đầu khỏi lũy thừa tập',10)
def _(t):
    n=t+3
    return {'n':n},f'Tập hợp X có {n} phần tử. Có bao nhiêu tập con của X khác rỗng và khác chính X?',I(2**n-2),f'Mỗi phần tử được chọn hoặc không chọn: có 2^{n} tập con. Loại tập rỗng và X, còn {2**n-2} tập.'

@method('set_k_subsets','tap_hop','Đếm các tập con k phần tử','set-binomial-k-subsets','Tổ hợp chập k của n khi thứ tự không quan trọng',10)
def _(t):
    n=t+7;k=3+t%3
    return dict(n=n,k=k),f'Tập X có {n} phần tử phân biệt. Có bao nhiêu tập con có đúng {k} phần tử?',I(comb(n,k)),f'Tập con không có thứ tự; chọn {k} trong {n} phần tử theo tổ hợp C({n},{k})={comb(n,k)}.'

@method('set_functions_domain_to_codomain','tap_hop','Số ánh xạ giữa hai tập hữu hạn','set-map-count-m-powers-n','Mỗi phần tử miền xác định chọn ảnh độc lập',10)
def _(t):
    n=3+t%5;m=2+t//2
    return dict(n=n,m=m),f'Cho hai tập X, Y có |X|={n}, |Y|={m}. Có bao nhiêu hàm số (ánh xạ) từ X đến Y?',I(m**n),f'Mỗi một trong {n} phần tử X có {m} lựa chọn giá trị ảnh trong Y, độc lập: {m}^{n}={m**n} hàm.'

@method('set_disjoint_cartesian_offdiagonal','tap_hop','Đếm cặp có thứ tự hai phần tử khác nhau','set-cartesian-square-off-diagonal','Tích Descartes A×A trừ đường chéo (a,a)',10)
def _(t):
    n=4+t
    return {'n':n},f'Cho A có {n} phần tử. Trong A×A có bao nhiêu cặp (x,y) với x≠y?',I(n*(n-1)),f'Tổng n² cặp có thứ tự, trong đó n cặp trên đường chéo có x=y. Còn n²−n={n*(n-1)} cặp.'

@method('set_union_difference_count','tap_hop','Số phần tử A trừ B','set-difference-cardinality-from-intersection','|A\\B|=|A|−|A∩B|',10)
def _(t):
    a=20+t;i=3+t//2;b=12+t
    return dict(a=a,b=b,i=i),f'Cho |A|={a}, |B|={b} và |A∩B|={i}. Tính |A\\B|.',I(a-i),f'Chỉ lấy các phần tử của A không nằm trong B, phải trừ giao: |A\\B|={a}−{i}={a-i}.'

@method('set_pairwise_disjoint_triple','tap_hop','Hợp ba tập đôi một rời nhau','set-union-pairwise-disjoint-additivity','Khi mọi giao đôi rỗng thì kích thước hợp là tổng',10)
def _(t):
    a=t+3;b=2*t+1;c=3*t+2
    return dict(a=a,b=b,c=c),f'Ba tập A, B, C đôi một không giao nhau, có |A|={a}, |B|={b}, |C|={c}. Tìm |A∪B∪C|.',I(a+b+c),f'Các tập đôi một rời nhau nên không có phần tử bị đếm hai lần. |A∪B∪C|={a}+{b}+{c}={a+b+c}.'

# B: Conditional probability and independence, with ten different goal operations.
@method('conditional_from_counts','bien_co_doc_lap_11','Xác suất có điều kiện từ bảng đếm','prob-conditional-event-empirical-frequency','P(A|B)=n(A∩B)/n(B)',11)
def _(t):
    b=20+2*t;j=5+t;total=b+20
    return dict(total=total,b=b,j=j),f'Trong {total} học sinh, {b} bạn tham gia câu lạc bộ B và có {j} bạn vừa ở B vừa chơi thể thao A. Chọn ngẫu nhiên một bạn trong B. Xác suất bạn đó chơi A là bao nhiêu?',R(j,b),f'Biết bạn thuộc B, không gian mẫu thu hẹp còn {b} người; thuận lợi {j} người. P(A|B)={j}/{b}={R(j,b)}.'

@method('joint_from_conditional','bien_co_doc_lap_11','Tính xác suất giao từ xác suất có điều kiện','prob-joint-from-conditional-multiplication','P(A∩B)=P(A|B)P(B)',11)
def _(t):
    p=R(t+1,4*(t+5));q=R(2+t%3,5)
    return dict(p=str(p),q=str(q)),f'Biết P(A|B)={p}, P(B)={q}. Tính P(A∩B).',p*q,f'Công thức nhân xác suất: P(A∩B)=P(A|B)·P(B)={p}·{q}={p*q}.'

@method('total_prob_two_sources','bien_co_doc_lap_11','Xác suất toàn phần theo hai nguồn','prob-total-two-source-weighted-sum','P(D)=P(A)P(D|A)+P(Ā)P(D|Ā)',11,real_world=True)
def _(t):
    p=R(t+1,3*(t+5));a=R(2,5);b=R(1,5+t%4);v=p*a+(1-p)*b
    return dict(p=str(p),a=str(a),b=str(b)),f'Xưởng A sản xuất {p} số sản phẩm. Tỉ lệ đạt chuẩn ở A là {a}, ở xưởng còn lại là {b}. Lấy ngẫu nhiên một sản phẩm, tính xác suất đạt chuẩn.',v,f'Chia thành hai nguồn A và không A: P(đạt)={p}·{a}+(1−{p})·{b}={v}.'

@method('bayes_posterior_inverse','bien_co_doc_lap_11','Suy luận nguồn bằng Bayes','prob-bayes-reverse-posterior-two-source','P(A|D)=P(D|A)P(A)/P(D)',11,real_world=True)
def _(t):
    p=R(1,t+2);a=R(3,4);b=R(1,4);v=p*a/(p*a+(1-p)*b)
    return dict(p=str(p),a=str(a),b=str(b)),f'Loại A chiếm {p} số linh kiện, xác suất đạt chuẩn của A là {a}, của loại khác là {b}. Biết linh kiện đã chọn đạt chuẩn, xác suất nó thuộc A là bao nhiêu?',v,f'Bayes: P(A|đạt)=({p}·{a})/[{p}·{a}+(1−{p})·{b}]={v}.'

@method('independent_joint','bien_co_doc_lap_11','Xác suất đồng thời của hai biến cố độc lập','prob-independent-intersection-product','P(A∩B)=P(A)P(B)',11)
def _(t):
    p=R(t+1,2*(t+3));q=R(2+t%3,7)
    return dict(p=str(p),q=str(q)),f'Hai biến cố A và B độc lập, P(A)={p}, P(B)={q}. Tính P(A∩B).',p*q,f'Do A và B độc lập: P(A∩B)=P(A)·P(B)={p}·{q}={p*q}.'

@method('independent_union','bien_co_doc_lap_11','Hợp hai biến cố độc lập','prob-independent-union-inclusion-exclusion','P(A∪B)=p+q−pq',11)
def _(t):
    p=R(1+t%4,7);q=R(2+t%3,8);v=p+q-p*q
    return dict(p=str(p),q=str(q)),f'A và B độc lập, P(A)={p}, P(B)={q}. Tính xác suất xảy ra ít nhất một trong hai.',v,f'Vì độc lập, giao có xác suất P(A)P(B)={p*q}. Vậy xác suất hợp = {p}+{q}−{p*q}={v}.'

@method('independent_neither','bien_co_doc_lap_11','Không biến cố nào xảy ra khi độc lập','prob-independent-neither-complement-product','P(Ā∩B̄)=(1−p)(1−q)',11)
def _(t):
    p=R(1+t%4,7);q=R(2+t%3,8);v=(1-p)*(1-q)
    return dict(p=str(p),q=str(q)),f'Hai phép thử độc lập có xác suất thành công lần lượt {p} và {q}. Tính xác suất không lần nào thành công.',v,f'Không thành công ở từng phép thử có xác suất 1−{p} và 1−{q}. Hai biến cố bù vẫn độc lập nên tích = {v}.'

@method('conditional_without_replacement','bien_co_doc_lap_11','Xác suất điều kiện rút vật không hoàn lại','prob-urn-conditional-without-replacement','Điều kiện lần đầu lấy đỏ làm thay đổi mẫu ở lần hai',11,real_world=True)
def _(t):
    red=5+t;blue=8+t
    return dict(red=red,blue=blue),f'Hộp có {red} bóng đỏ và {blue} bóng xanh. Rút hai bóng liên tiếp không hoàn lại. Biết bóng thứ nhất đỏ, xác suất bóng thứ hai đỏ bằng bao nhiêu?',R(red-1,red+blue-1),f'Sau khi lần đầu đỏ, hộp còn {red-1} bóng đỏ trong {red+blue-1} bóng. Xác suất = {R(red-1,red+blue-1)}.'

@method('posterior_negative_result','bien_co_doc_lap_11','Bayes khi quan sát kết quả âm tính','prob-bayes-negative-test-complement','P(A|¬D)=P(A)P(¬D|A)/P(¬D)',11,real_world=True)
def _(t):
    p=R(1,t+3);s=R(3,4);f=R(1,6);v=p*(1-s)/(p*(1-s)+(1-p)*(1-f))
    return dict(p=str(p),s=str(s),f=str(f)),f'Một sản phẩm lỗi với xác suất {p}; máy báo lỗi khi thật sự lỗi với xác suất {s}, báo lỗi nhầm khi sản phẩm tốt với xác suất {f}. Nếu máy không báo lỗi, xác suất sản phẩm vẫn lỗi là bao nhiêu?',v,f'P(¬báo|lỗi)=1−{s}; P(¬báo|tốt)=1−{f}. Bayes cho kết quả âm tính: {v}.'

@method('conditional_at_least_one_two_trials','bien_co_doc_lap_11','Xác suất cả hai xảy ra khi biết ít nhất một','prob-both-given-union-independent','P(A∩B|A∪B)=pq/(p+q−pq)',11)
def _(t):
    p=R(1+t%4,6);q=R(2+t%3,7);v=p*q/(p+q-p*q)
    return dict(p=str(p),q=str(q)),f'A,B độc lập với P(A)={p}, P(B)={q}. Biết có ít nhất một biến cố xảy ra, xác suất cả hai cùng xảy ra bằng bao nhiêu?',v,f'Vì A∩B⊂A∪B, xác suất có điều kiện bằng P(A∩B)/P(A∪B)=({p}·{q})/({p}+{q}−{p}·{q})={v}.'

# C: Complex numbers, ten different computational objectives.
@method('complex_modulus_squared','so_phuc','Bình phương môđun số phức','complex-square-modulus-conjugate-product','|a+bi|²=a²+b²',12)
def _(t):
    a=t+2;b=2*t-7
    return dict(a=a,b=b),f'Cho z={a}+({b})i. Tính |z|².',I(a*a+b*b),f'Từ z·z̄=a²+b² suy ra |z|²={a}²+({b})²={a*a+b*b}.'

@method('complex_conjugate_imag','so_phuc','Phần ảo của số phức liên hợp','complex-conjugate-negates-imaginary-component','Im(conj(a+bi))=−b',12)
def _(t):
    a=t+5;b=t-6
    return dict(a=a,b=b),f'Cho z={a}+({b})i. Tìm phần ảo của số phức liên hợp z̄.',I(-b),f'Số liên hợp là z̄={a}−({b})i, do đó phần ảo bằng −({b})={-b}.'

@method('complex_product_modulus_squared','so_phuc','Bình phương môđun tích số phức','complex-modulus-multiplicative-norm','|zw|²=|z|²|w|²',12)
def _(t):
    a=t;b=t+1;c=t-4;d=t+3
    return dict(a=a,b=b,c=c,d=d),f'Cho z={a}+{b}i, w=({c})+{d}i. Tính |zw|².',I((a*a+b*b)*(c*c+d*d)),f'Môđun có tính nhân, |zw|²=(a²+b²)(c²+d²)=({a*a+b*b})({c*c+d*d})={(a*a+b*b)*(c*c+d*d)}.'

@method('complex_quotient_real','so_phuc','Phần thực của thương hai số phức','complex-real-quotient-conjugate-denominator','Re((a+bi)/(c+di))=(ac+bd)/(c²+d²)',12)
def _(t):
    a=t+1;b=t-4;c=t+2;d=2+t%4;v=R(a*c+b*d,c*c+d*d)
    return dict(a=a,b=b,c=c,d=d),f'Với z=({a}+({b})i)/({c}+{d}i), hãy tính Re(z).',v,f'Nhân cả tử và mẫu với {c}−{d}i, phần thực thu được ({a}·{c}+({b})·{d})/({c}²+{d}²)={v}.'

@method('complex_quotient_imag','so_phuc','Phần ảo của thương hai số phức','complex-imag-quotient-conjugate-denominator','Im((a+bi)/(c+di))=(bc−ad)/(c²+d²)',12)
def _(t):
    a=t+3;b=t-6;c=t+2;d=t%4+2;v=R(b*c-a*d,c*c+d*d)
    return dict(a=a,b=b,c=c,d=d),f'Với z=({a}+({b})i)/({c}+{d}i), hãy tính Im(z).',v,f'Nhân liên hợp mẫu và tách phần ảo, Im(z)=[({b})·{c}−{a}·{d}]/({c}²+{d}²)={v}.'

@method('complex_inverse_real','so_phuc','Phần thực của nghịch đảo số phức','complex-reciprocal-real-component','Re(1/(a+bi))=a/(a²+b²)',12)
def _(t):
    a=t+1;b=2+t%5;v=R(a,a*a+b*b)
    return dict(a=a,b=b),f'Cho z={a}+{b}i. Tìm phần thực của 1/z.',v,f'1/z=(a−bi)/(a²+b²). Thay a={a}, b={b}, được Re(1/z)={v}.'

@method('complex_inverse_imag','so_phuc','Phần ảo của nghịch đảo số phức','complex-reciprocal-imag-component','Im(1/(a+bi))=−b/(a²+b²)',12)
def _(t):
    a=t+1;b=2+t%5;v=R(-b,a*a+b*b)
    return dict(a=a,b=b),f'Cho z={a}+{b}i. Tìm phần ảo của 1/z.',v,f'1/z=(a−bi)/(a²+b²). Hệ số của i bằng −{b}/({a}²+{b}²)={v}.'

@method('complex_distance_between_points','so_phuc','Khoảng cách hai điểm biểu diễn số phức','complex-distance-from-coordinate-difference','|z−w| theo Pythagoras trong mặt phẳng phức',12)
def _(t):
    a=t+3;b=t-2;c=t-1;d=t+2;v=sqrt((a-c)**2+(b-d)**2)
    return dict(a=a,b=b,c=c,d=d),f'Trong mặt phẳng phức, z={a}+({b})i và w=({c})+{d}i. Tính khoảng cách giữa hai điểm biểu diễn.',v,f'Khoảng cách là |z−w|=√[({a}−({c}))²+({b}−{d})²]={v}.'

@method('complex_rotate_by_i_real','so_phuc','Hoành độ sau khi quay điểm 90 độ','complex-multiplication-i-coordinate-rotation','Re(iz)=−Im(z)',12)
def _(t):
    a=t-5;b=t+3
    return dict(a=a,b=b),f'Nhân số phức z=({a})+{b}i với i tương ứng quay 90° ngược chiều kim đồng hồ. Hoành độ điểm biểu diễn iz bằng bao nhiêu?',I(-b),f'i·[({a})+{b}i]=−{b}+({a})i. Hoành độ (phần thực) bằng −{b}.'

@method('complex_circle_disk_area','so_phuc','Diện tích hình tròn quỹ tích môđun số phức','complex-locus-closed-disk-area','|z−z0|≤r là hình tròn bán kính r',12)
def _(t):
    a=t-4;b=t+1;r=2+t%5
    return dict(a=a,b=b,r=r),f'Điểm z thuộc miền |z−(({a})+{b}i)|≤{r}. Diện tích miền trong mặt phẳng phức bằng bao nhiêu?',I(r*r)*pi,f'Bất đẳng thức môđun mô tả hình tròn tâm ({a};{b}), bán kính {r}. Diện tích bằng πr²={r*r}π.'

BY_ID={m.family:m for m in METHODS}
FAMILIES=frozenset(BY_ID)
FORMATS=('tra_loi_ngan','trac_nghiem','dung_sai','tu_luan_ngan','van_dung')

def _hash(s):return sha256(re.sub(r'\s+',' ',s.strip().lower()).encode()).hexdigest()

def generate(family,ordinal,difficulty=None,seed_key=None):
    if family not in FAMILIES or type(ordinal) is not int or not 0<=ordinal<10:raise ValueError('invalid family/ordinal')
    m=BY_ID[family]
    p,stem,v,solution=HANDLERS[family](ordinal+2)
    v=simplify(v);num=str(v);answer=num;fmt=FORMATS[ordinal%5];extra={}
    if m.grade == 12: solution += ' Sử dụng các quy tắc số phức và hệ thức i²=−1, trả lời ở dạng chính xác.'
    if fmt=='trac_nghiem':
        alternatives=[]
        if m.grade == 11:
            # Probability distractors must remain in [0,1]. They represent
            # missing a condition, taking the complement, or scaling once.
            candidates=[1-v,v/2,(1+v)/2,v*2,v+R(1,10),v-R(1,10),v/3]
        elif m.grade == 12:
            # Common mistakes: dropping a factor, doubling, wrong sign, or
            # forgetting the square in the norm/area computation.
            candidates=[-v,v/2,2*v,v+1,v-1,3*v/2]
            if 'squared' in family or 'disk_area' in family:
                candidates=[v/2,2*v,v+1,v+2,3*v/2]
        else:
            candidates=[v+1,v-1,v+p.get('i',2),v-p.get('i',2),v+2,v*2]
        for x in candidates:
            x=simplify(x)
            if m.grade == 11 and not 0 <= float(x) <= 1:continue
            if m.grade == 10 and float(x)<0:continue
            if m.grade == 12 and ('squared' in family or 'disk_area' in family) and float(x)<0:continue
            if simplify(x-v)==0 or any(simplify(x-z)==0 for z in alternatives):continue
            alternatives.append(x)
            if len(alternatives)==3:break
        if len(alternatives)!=3:raise ValueError('no plausible options')
        index=(ordinal+1)%4
        options=[str(a) for a in alternatives];options.insert(index,num)
        extra={'options':options,'correct_index':index}
        stem+=' Chọn đáp án chính xác trong bốn phương án.'
        solution+=f' Đáp án đúng là {"ABCD"[index]}.'
    elif fmt=='dung_sai':
        assertion=v if ordinal<5 else v+1
        truth=bool(simplify(assertion-v)==0)
        stem+=f' Nhận định “Kết quả bằng {assertion}” là đúng hay sai?'
        answer='Đúng' if truth else 'Sai';extra={'assertion_value':str(assertion),'truth':truth}
        solution+=f' Do đó nhận định trên {"đúng" if truth else "sai"}.'
    elif fmt=='tu_luan_ngan':stem+=' Trình bày lập luận, ghi đáp án chính xác.'
    elif fmt=='van_dung':
        fmt='toan_thuc_te' if m.real_world else 'van_dung'
        stem+=' Giải thích cách thực hiện và nêu kết luận.'
    else:stem+=' Ghi đáp số ở dạng chính xác.'
    return dict(family=family,ordinal=ordinal,params=p,stem=stem,answer=answer,solution=solution,
        difficulty=difficulty or m.difficulty,question_type=fmt,numeric_result=num,topic_id=m.topic,
        method_signature=m.signature,skill=m.skill,method_review_status='pending-expert-review',
        independence_certified=False,seed_key=seed_key or '',fingerprint=_hash(stem),**extra)

def verify(data):
    try:
        family=data.get('family');ordinal=data.get('ordinal')
        if family not in FAMILIES or type(ordinal) is not int:return False,{'error':'invalid family/ordinal'}
        regenerated=generate(family,ordinal,data.get('difficulty'),data.get('seed_key'))
        if regenerated!=data:return False,{'error':'tampered record or incorrect deterministic generation'}
        from .v119_oracle import expected
        val=simplify(expected(family,data['params']))
        expected_ans=simplify(HANDLERS[family](ordinal+2)[2])
        if simplify(val-expected_ans)!=0:return False,{'error':'independent oracle mismatch'}
        if data['question_type']=='trac_nghiem':
            options=data['options'];idx=data['correct_index']
            if len(options)!=4 or len(set(options))!=4 or options[idx]!=data['numeric_result']:return False,{'error':'invalid multiple choice'}
            if sum(simplify(sympify(op)-val)==0 for op in options)!=1:return False,{'error':'incorrect multiple choice'}
        if data['question_type']=='dung_sai':
            truth=bool(simplify(sympify(data['assertion_value'])-val)==0)
            if truth!=data['truth'] or data['answer']!=('Đúng' if truth else 'Sai'):return False,{'error':'true/false answer mismatch'}
        if len(data['solution'])<45:return False,{'error':'solution too short'}
        return True,{'independent_parametric_oracle':True,'record_integrity':True,
                     'uniqueness_of_method':'not certified','publication_blocked':True}
    except Exception as e:return False,{'error':type(e).__name__+': '+str(e)}

def export(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    seen=set();format_counts=Counter()
    with (folder/'V119_NEW_CANDIDATE_FORMS.jsonl').open('w',encoding='utf8') as forms, (folder/'V119_NEW_QUESTIONS.jsonl').open('w',encoding='utf8') as questions:
        for m in METHODS:
            forms.write(json.dumps({**m.__dict__,'status':'pending-expert-review','independence_certified':False},ensure_ascii=False)+'\n')
            for ordinal in range(10):
                data=generate(m.family,ordinal)
                yes,proof=verify(data)
                if not yes:raise ValueError((m.family,ordinal,proof))
                if data['fingerprint'] in seen:raise ValueError('duplicate question text '+m.family)
                seen.add(data['fingerprint']);format_counts[data['question_type']]+=1
                questions.write(json.dumps({**data,'verification':proof},ensure_ascii=False)+'\n')
    return {'new_candidate_methods':len(METHODS),'verified_answer_questions':len(seen),
            'formats':dict(format_counts),'independence_certified':0}
