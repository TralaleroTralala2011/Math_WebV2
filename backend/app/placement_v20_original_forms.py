"""V20 original placement REVIEW CANDIDATES, not approved official exam items.

Each slug is one mathematical method; ten numeric instances remain ONE method.
Prompts and explanations are newly authored, drawing on public curriculum and
assessment frameworks, NOT copied examination text. No self-certification.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb, gcd
from .qf2_verified_generators import _form, _integer_options


def _new(grade, topic, title, concept, method, condition, distinction, items, process):
    if len(items) != 10:
        raise ValueError('Each candidate form needs precisely ten items')
    doc = _form(grade=grade, topic_id=topic, title=title, concept=concept,
                method=method, conditions=condition, distinguishing=distinction,
                instances=items)
    doc['assessed_process'] = process
    doc['difficulty_status'] = 'provisional_must_be_calibrated'
    doc['provenance'] = 'original_v20_authoring_no_exam_text_copied'
    return doc


def _item(prompt, ans, explanation, distractors=None):
    ans=str(ans)
    if distractors is None:
        distractors=_integer_options(int(ans))[1:]
    choices=[ans]+list(map(str,distractors))
    if len(set(choices)) != 4:
        raise ValueError(('Duplicate choices',prompt, choices))
    if len(explanation) < 24:
        raise ValueError('Explanation too short')
    return (prompt,ans,explanation,choices)


def _fraction(n,d):
    f=Fraction(n,d)
    return f'{f.numerator}/{f.denominator}' if f.denominator!=1 else str(f.numerator)


def g10_systems():
    items=[]
    for i in range(10):
        x=(i%5)-2; y=(i//2)-1; a=(i%3)+2
        b=a*x+y; c=x-y; target=x+y
        # Independent algebraic check: x=(b+c)/(a+1), y=x-c
        assert Fraction(b+c,a+1)==x and x-(x-y)==y
        items.append(_item(f'Hệ phương trình: {a}x+y={b} và x−y={c}. Tính x+y.',target,
                           f'Từ x−y={c} suy ra y=x−({c}). Thế vào {a}x+y={b} được '
                           f'({a}+1)x={b}+({c}), nên x={x}, y={y} và x+y={target}.'))
    return _new(10,'phuong_trinh_he','Giải hệ phương trình tuyến tính bằng phép thế',
                'Nghiệm duy nhất của hệ hai phương trình bậc nhất hai ẩn',
                'Thế biểu thức một ẩn vào phương trình còn lại, kết luận nghiệm rồi tính biểu thức',
                'Hai hệ số tuyến tính, định thức khác không',
                'Dùng phép thế để tìm nghiệm hệ, khác giải phương trình đơn hay thế trực tiếp',items,'employ')


def g10_counting():
    items=[]
    for i in range(10):
        a=i+2;b=i%4+3; count=a*b
        items.append(_item(f'Một cửa hàng có {a} loại áo và {b} loại quần. Chọn một áo và một quần có bao nhiêu cách?',count,
                           f'Mỗi một trong {a} lựa chọn áo ghép được với {b} quần. '
                           f'Theo quy tắc nhân, số bộ trang phục là {a}×{b}={count}.'))
    return _new(10,'quy_tac_dem','Đếm số lựa chọn hai giai đoạn theo quy tắc nhân',
                'Quy tắc nhân trong bài toán lựa chọn độc lập',
                'Xác định các công đoạn chọn và nhân số lựa chọn từng công đoạn',
                'Mỗi áo ghép với mọi quần, không ràng buộc',
                'Mô hình hóa tình huống hai bước, không cộng số lựa chọn',items,'formulate')


def g10_combinations():
    items=[]
    for i in range(10):
        n=4+i; k=2+(i%2); answer=comb(n,k)
        items.append(_item(f'Có {n} học sinh khác nhau. Chọn một nhóm {k} học sinh, không phân vai. Có bao nhiêu nhóm?',answer,
                           f'Không xét thứ tự nên dùng tổ hợp: C({n},{k})={n}!/({k}!×({n}-{k})!)={answer}.'))
    return _new(10,'hoan_vi_chinh_hop_to_hop','Đếm tổ hợp chọn nhóm không xét thứ tự',
                'Tổ hợp chập k của n phần tử',
                'Phân biệt lựa chọn có xét thứ tự và không xét thứ tự, áp dụng tổ hợp',
                'Các phần tử phân biệt, 0<k<n',
                'Đếm nhóm không phân vai, khác chỉnh hợp có phân vai',items,'reasoning')


def g10_probability():
    items=[]
    for i in range(10):
        red=2+(i%4); blue=3+(i//2); ans=_fraction(red,red+blue)
        options=[_fraction(blue,red+blue),_fraction(red,blue),_fraction(1,red+blue),_fraction(red+blue,red)]
        wrong=[]
        for x in options:
            if x!=ans and x not in wrong:wrong.append(x)
        # Ensure exactly three unique alternatives, including valid fractions.
        for x in ['0','1','2']:
            if len(wrong)>=3:break
            if x!=ans and x not in wrong:wrong.append(x)
        items.append(_item(f'Hộp kín có {red} bi đỏ và {blue} bi xanh, các bi đồng khả năng. Lấy ngẫu nhiên một bi. Xác suất lấy bi đỏ là bao nhiêu?',ans,
                           f'Tổng số bi là {red}+{blue}={red+blue}; có {red} kết quả thuận lợi. '
                           f'Xác suất cần tìm bằng {red}/({red}+{blue})={ans}.',wrong[:3]))
    return _new(10,'xac_suat','Tính xác suất cổ điển của một biến cố đơn',
                'Tỉ số số trường hợp thuận lợi trên tổng đồng khả năng',
                'Đếm không gian mẫu và kết quả thuận lợi rồi lấy tỉ số',
                'Lấy ngẫu nhiên một bi, các bi đồng khả năng',
                'Tính xác suất tần suất lý thuyết, khác đếm số tổ hợp',items,'employ')


def g10_mean():
    items=[]
    for i in range(10):
        a=i+1; seq=[a,a+2,a+4,a+6,a+8]; ans=a+4
        items.append(_item(f'Giá trị đo của năm lượt khảo sát lần lượt là {", ".join(map(str,seq))}. Tính số trung bình cộng.',ans,
                           f'Tổng bằng {sum(seq)}; chia cho 5 ta được {sum(seq)}/5={ans}. Đây là số trung bình cộng.'))
    return _new(10,'thong_ke','Tính số trung bình cộng của dữ liệu chưa ghép nhóm',
                'Giá trị trung bình số học của một mẫu hữu hạn',
                'Cộng các số liệu rồi chia cho số lượng quan sát',
                'Năm quan sát có trọng số bằng nhau',
                'Tính trung bình, khác trung vị hay phương sai',items,'interpret')


def g10_vector_dot():
    items=[]
    for i in range(10):
        a=i%5-2;b=i%4+1;c=i//2-3;d=3-i%3;ans=a*c+b*d
        items.append(_item(f'Trong mặt phẳng, u=({a};{b}), v=({c};{d}). Tính tích vô hướng u·v.',ans,
                           f'Theo định nghĩa tích vô hướng tọa độ: u·v={a}×({c})+{b}×({d})={ans}.'))
    return _new(10,'vector','Tính tích vô hướng hai vectơ từ tọa độ',
                'Tích vô hướng trong hệ trục tọa độ vuông góc',
                'Nhân tọa độ tương ứng rồi cộng để tìm tích vô hướng',
                'Hai vectơ mặt phẳng có tọa độ thực',
                'Tích vô hướng là số, khác cộng vectơ',items,'employ')


def g10_midpoint():
    items=[]
    for i in range(10):
        xm=i-4; ym=3-i%6; dx=i%4+1;dy=i%3+2
        x1=xm-dx;x2=xm+dx;y1=ym-dy;y2=ym+dy
        ans=xm+ym
        items.append(_item(f'Cho A({x1};{y1}) và B({x2};{y2}). Trung điểm M của AB có tổng hoành độ và tung độ bằng bao nhiêu?',ans,
                           f'Tọa độ trung điểm M=(({x1}+{x2})/2;({y1}+{y2})/2)=({xm};{ym}). '
                           f'Vậy x_M+y_M={xm}+({ym})={ans}.'))
    return _new(10,'toa_do_phang','Tìm trung điểm đoạn thẳng bằng tọa độ',
                'Trung điểm của hai điểm trong mặt phẳng Oxy',
                'Lấy trung bình từng cặp hoành độ, tung độ',
                'Hai điểm phân biệt trong hệ tọa độ Descartes',
                'Tìm trung điểm, khác công thức khoảng cách',items,'employ')


def g10_line_zero():
    items=[]
    for i in range(10):
        a=(i%5)+1; root=i-5;b=-a*root
        items.append(_item(f'Cho hàm số bậc nhất f(x)={a}x+({b}). Tìm hoành độ giao điểm với trục Ox.',root,
                           f'Điểm trên Ox có tung độ 0. Giải {a}x+({b})=0 ta có x=−({b})/{a}={root}.'))
    return _new(10,'ham_so_bac_nhat','Xác định giao điểm đồ thị bậc nhất với trục hoành',
                'Nghiệm phương trình ax+b=0 với a khác 0',
                'Cho f(x)=0 rồi giải phương trình bậc nhất',
                'Hệ số góc a khác 0',
                'Tìm hoành độ giao điểm Ox, khác tính giá trị f(x)',items,'employ')


def g10_inequality():
    items=[]
    for i in range(10):
        a=i%4+1;t=i-4;b=-(a*t)
        items.append(_item(f'Bất phương trình {a}x+({b})≥0 tương đương x≥m. Tìm m.',t,
                           f'Chuyển vế được {a}x≥−({b})={-b}. Vì {a}>0, chia hai vế cho {a} không đổi chiều: x≥{t}.'))
    return _new(10,'bat_phuong_trinh','Giải bất phương trình bậc nhất một ẩn với hệ số dương',
                'Phép biến đổi tương đương bất phương trình tuyến tính',
                'Chuyển vế rồi chia cho hệ số dương, giữ nguyên chiều bất phương trình',
                'Hệ số của x dương, nghiệm dưới dạng nửa khoảng',
                'Giải tập nghiệm bất phương trình, không phải phương trình',items,'reasoning')


def g10_circle_radius():
    items=[]
    for i in range(10):
        a=i-4; b=i%5-2; r=i%5+2
        const=a*a+b*b-r*r
        items.append(_item(f'Đường tròn có phương trình x²+y²+({-2*a})x+({-2*b})y+({const})=0. Tính bán kính.',r,
                           f'Hoàn thành bình phương: (x−({a}))²+(y−({b}))²={r*r}. '
                           f'Vì bán kính không âm nên R=√{r*r}={r}.'))
    return _new(10,'duong_tron','Tìm bán kính từ phương trình đường tròn',
                'Nhận diện tâm và bán kính đường tròn trong Oxy',
                'Hoàn thành bình phương để đưa về (x−a)²+(y−b)²=R²',
                'Bán kính dương, hệ số đã bảo đảm phương trình là đường tròn',
                'Tìm bán kính, khác tọa độ điểm hoặc giao của hai đường',items,'reasoning')


def g11_derivative():
    items=[]
    for i in range(10):
        a=i%3+1;b=2-i;c=i-3;x=i%5-2;ans=3*a*x*x+2*b*x+c
        items.append(_item(f'Cho f(x)={a}x³+({b})x²+({c})x+1. Tính f′({x}).',ans,
                           f'Áp dụng quy tắc đạo hàm từng hạng: f′(x)={3*a}x²+({2*b})x+({c}). '
                           f'Thay x={x} được f′({x})={ans}.'))
    return _new(11,'dao_ham','Tính đạo hàm đa thức tại điểm cho trước',
                'Đạo hàm của tổng các đơn thức',
                'Dùng (xⁿ)′=nxⁿ⁻¹ rồi thay tọa độ x₀',
                'Đa thức bậc ba, mọi x thực',
                'Tìm f′(x₀), không tính f(x₀) hay nguyên hàm',items,'employ')


def g11_limit():
    items=[]
    for i in range(10):
        a=i-4;k=(i%5)+1;ans=2*a+k
        items.append(_item(f'Tính lim khi x→{a} của [x²+({k})x−({a*a+k*a})]/(x−({a})).',ans,
                           f'Tử bằng (x−({a}))(x+({a+k})), khử x−({a}) với x≠{a}. '
                           f'Giới hạn bằng {a}+({a+k})={ans}.'))
    return _new(11,'gioi_han','Khử nhân tử chung tính giới hạn dạng 0/0',
                'Giới hạn hữu hạn của phân thức sau phân tích nhân tử',
                'Phân tích tử thành tích chứa (x−a), giản ước rồi thế x=a',
                'Giới hạn x tiến tới a, không phải giá trị hàm tại a',
                'Khử điểm gián đoạn, khác phép thế trực tiếp',items,'reasoning')


def g11_translation():
    items=[]
    for i in range(10):
        x=i-4; y=2-i%5;u=i%4+1;v=i%3-2;ans=x+u+y+v
        items.append(_item(f'Phép tịnh tiến theo vectơ v=({u};{v}) biến điểm P({x};{y}) thành P′. Tính x′+y′.',ans,
                           f'Tịnh tiến cộng vectơ: P′=({x}+({u});{y}+({v}))=({x+u};{y+v}). '
                           f'Vậy x′+y′={ans}.'))
    return _new(11,'g11_geom_transform_translation','Ảnh của điểm qua phép tịnh tiến trong Oxy',
                'Phép tịnh tiến bảo toàn hình dạng và cộng tọa độ',
                'Cộng từng tọa độ điểm với tọa độ vectơ tịnh tiến',
                'Tịnh tiến theo vectơ bất kỳ trong mặt phẳng',
                'Ảnh của phép tịnh tiến, khác phép đối xứng trục',items,'employ')


def g11_reflection():
    items=[]
    for i in range(10):
        x=i-5;y=i%7-3;ans=x-y
        items.append(_item(f'Đối xứng điểm P({x};{y}) qua trục Ox được điểm P′. Tính x′+y′.',ans,
                           f'Qua Ox giữ hoành độ và đổi dấu tung độ: P′=({x};{-y}). '
                           f'Vậy x′+y′={x}+({-y})={ans}.'))
    return _new(11,'g11_geom_transform_reflection','Phép đối xứng trục Ox của một điểm',
                'Đối xứng trục trong hệ tọa độ mặt phẳng',
                'Giữ x và đổi dấu y khi phản xạ qua Ox',
                'Trục đối xứng là trục hoành',
                'Phép đối xứng đổi dấu một tọa độ, không phải tịnh tiến',items,'employ')


def g11_median():
    items=[]
    for i in range(10):
        a=i-3;data=[a+2,a+8,a,a+6,a+4]; ans=a+4
        items.append(_item(f'Mẫu gồm 5 số liệu: {", ".join(map(str,data))}. Tìm trung vị của mẫu.',ans,
                           f'Sắp thứ tự tăng dần: {a}, {a+2}, {a+4}, {a+6}, {a+8}. '
                           f'Vì có 5 giá trị, trung vị là giá trị thứ ba: {ans}.'))
    return _new(11,'thong_ke_11','Tìm trung vị của mẫu dữ liệu có số phần tử lẻ',
                'Trung vị là phần tử ở chính giữa dãy đã sắp xếp',
                'Sắp xếp mẫu rồi chọn phần tử ở vị trí giữa',
                'Mẫu gồm năm số liệu đơn, có một trung vị duy nhất',
                'Trung vị khác số trung bình cộng',items,'interpret')


def g11_continuity():
    items=[]
    for i in range(10):
        a=i-4;c=i%5+1;d=i%3-2;val=c*a+d
        items.append(_item(f'Cho f(x)={c}x+({d}) khi x≠{a}, và f({a})=m. Tìm m để f liên tục tại x={a}.',val,
                           f'Giới hạn khi x→{a} của {c}x+({d}) bằng {c}×({a})+({d})={val}. '
                           f'Liên tục tại x={a} đòi hỏi f({a})={val}, nên m={val}.'))
    return _new(11,'ham_so_lien_tuc','Chọn giá trị tại điểm để hàm số liên tục',
                'Điều kiện giới hạn bằng giá trị hàm tại điểm',
                'Tính giới hạn hai phía và đặt bằng giá trị f(a)',
                'Hàm tuyến tính ngoài điểm a, gián đoạn loại bỏ được',
                'Điều chỉnh tham số để liên tục, khác chỉ tính giới hạn',items,'reasoning')


def g11_independent():
    items=[]
    for i in range(10):
        a=i%4+2;b=i%3+3;num=a*b;den=(a+2)*(b+3)
        ans=_fraction(num,den)
        wrong=[]
        for x in [_fraction(a,a+2),_fraction(b,b+3),_fraction(a+b,(a+2)*(b+3)),'1','0']:
            if x!=ans and x not in wrong:wrong.append(x)
        items.append(_item(f'Hai biến cố độc lập A và B có P(A)={_fraction(a,a+2)}, P(B)={_fraction(b,b+3)}. Tính P(A∩B).',ans,
                           f'Vì A,B độc lập, P(A∩B)=P(A)P(B)={a}/{a+2}×{b}/{b+3}={ans}.',wrong[:3]))
    return _new(11,'bien_co_doc_lap_11','Xác suất giao của hai biến cố độc lập',
                'Tính xác suất đồng thời xảy ra của hai biến cố độc lập',
                'Nhân hai xác suất thành phần khi có điều kiện độc lập',
                'Hai biến cố được cho là độc lập, xác suất trong [0,1]',
                'Tính giao của hai biến cố độc lập, khác cộng xác suất hợp',items,'employ')


def g11_recurrence():
    items=[]
    for i in range(10):
        a=i-3;d=i%5+1;n=3+(i%6);ans=a+(n-1)*d
        items.append(_item(f'Dãy số có u₁={a}, uₙ₊₁=uₙ+({d}) với n≥1. Tính u_{n}.',ans,
                           f'Mỗi bước tăng {d} nên sau {n-1} bước, '
                           f'u_{n}=u₁+({n}−1)×({d})={a}+{(n-1)*d}={ans}.'))
    return _new(11,'day_so_truy_hoi_11','Suy ra số hạng từ công thức truy hồi cộng hằng số',
                'Dãy số truy hồi tuyến tính cấp một',
                'Lặp truy hồi từ u₁ hoặc chuyển về công thức tường minh',
                'Truy hồi uₙ₊₁=uₙ+d, chỉ số nguyên dương',
                'Suy luận từ truy hồi, khác cho sẵn cấp số cộng uₙ',items,'reasoning')


def g11_homothety():
    items=[]
    for i in range(10):
        x=i%5-2;y=i//2-2;k=i%4+2;ans=k*(x+y)
        items.append(_item(f'Phép vị tự tâm O, tỉ số k={k}, biến A({x};{y}) thành A′. Tính x′+y′.',ans,
                           f'Vị tự tâm O nhân hai tọa độ với k={k}. A′=({k*x};{k*y}); '
                           f'x′+y′={k*x}+({k*y})={ans}.'))
    return _new(11,'g11_geom_rotation_homothety','Ảnh của điểm dưới phép vị tự tâm O',
                'Phép vị tự tâm gốc tọa độ với tỉ số k',
                'Nhân từng tọa độ của điểm với hệ số vị tự',
                'Tâm vị tự là O, k khác 0',
                'Thay đổi kích thước theo hệ số, không phải tịnh tiến hay đối xứng',items,'employ')


def g11_trig_identity():
    items=[]
    for i in range(10):
        a=i%4+1;b=i%5+1;ans=a*a+b*b
        # Identity sin² + cos² = 1 used to simplify a coefficient.
        items.append(_item(f'Cho sin²θ+cos²θ=1. Rút gọn E={a*a}sin²θ+{a*a}cos²θ+{b*b}.',ans,
                           f'Nhóm hai hạng đầu: E={a*a}(sin²θ+cos²θ)+{b*b}='
                           f'{a*a}+{b*b}={ans}.'))
    return _new(11,'cong_thuc_luong_giac','Rút gọn biểu thức bằng hệ thức sin²x+cos²x=1',
                'Hệ thức lượng giác cơ bản',
                'Đặt nhân tử chung rồi thay sin²θ+cos²θ bằng một',
                'Góc θ bất kỳ, đồng nhất thức đúng với mọi θ thực',
                'Rút gọn biểu thức lượng giác, không giải phương trình lượng giác',items,'reasoning')


def g12_exponential():
    items=[]
    for i in range(10):
        base=2+(i%3);n=i+1;rhs=base**n
        items.append(_item(f'Giải phương trình {base}^x={rhs}. Tìm x.',n,
                           f'Vì {rhs}={base}^{n} và cơ số {base}>0, khác 1, '
                           f'hàm mũ đơn điệu nên x={n}.'))
    return _new(12,'pt_mu','Giải phương trình mũ cùng cơ số',
                'Tính đơn ánh của hàm mũ với cơ số dương khác một',
                'Đưa hai vế về cùng cơ số rồi so sánh số mũ',
                'Cơ số nguyên lớn hơn một, vế phải là lũy thừa chính xác',
                'Giải ẩn ở số mũ, khác phương trình đa thức',items,'employ')


def g12_logarithm():
    items=[]
    for i in range(10):
        base=2+(i%3);expo=i%4+1;ans=base**expo
        items.append(_item(f'Giải log cơ số {base} của x bằng {expo}. Tìm x.',ans,
                           f'Điều kiện x>0. Theo định nghĩa log_{base}(x)={expo} '
                           f'tương đương x={base}^{expo}={ans}, thỏa điều kiện.'))
    return _new(12,'pt_logarit','Giải phương trình logarit cơ bản bằng định nghĩa',
                'Định nghĩa log_b(x) với b>0, b khác 1, x>0',
                'Đưa phương trình log_b x=c về x=b^c và kiểm tra điều kiện',
                'Cơ số nguyên lớn hơn một, nghiệm dương',
                'Giải logarit bằng phép lũy thừa ngược, không phải phương trình mũ',items,'employ')


def g12_integral():
    items=[]
    for i in range(10):
        a=i%4+1;b=i-4;n=2*((i%5)+1);ans=a*n*n//2+b*n
        assert a*n*n%2==0
        items.append(_item(f'Tính tích phân xác định I=∫ từ 0 đến {n} của ({a}x+({b})) dx.',ans,
                           f'Nguyên hàm là {a}x²/2+({b})x. Lấy giá trị tại {n} trừ giá trị tại 0: '
                           f'I={a}×{n}²/2+({b})×{n}={ans}.'))
    return _new(12,'nguyen_ham_tich_phan','Tính tích phân xác định của hàm bậc nhất',
                'Định lý cơ bản của giải tích cho đa thức',
                'Tìm nguyên hàm và thế hai cận theo công thức Newton–Leibniz',
                'Hàm bậc nhất liên tục, cận hữu hạn',
                'Tính tích phân có cận, khác nguyên hàm không cận',items,'employ')


def g12_extrema():
    items=[]
    for i in range(10):
        a=i%4+1;h=i-5;k=i%5-2;b=-2*a*h;c=a*h*h+k;ans=k
        items.append(_item(f'Cho f(x)={a}x²+({b})x+({c}), x thuộc R. Giá trị nhỏ nhất của f(x) bằng bao nhiêu?',ans,
                           f'Hoàn thành bình phương f(x)={a}(x−({h}))²+({k}). '
                           f'Vì {a}>0 và bình phương không âm, min f(x)={k} tại x={h}.'))
    return _new(12,'gtln_gtnn','Tìm giá trị nhỏ nhất bằng hoàn thành bình phương',
                'Tính không âm của bình phương trong hàm bậc hai',
                'Đưa biểu thức về a(x−h)²+k với a>0',
                'Hàm bậc hai xác định trên R và hệ số bậc hai dương',
                'Tìm GTNN trên R, khác tìm tọa độ đỉnh theo công thức',items,'reasoning')


def g12_plane_eval():
    items=[]
    for i in range(10):
        a=i%4+1;b=i%3-2;c=i%5+1;x=i-4;y=i%4-2;z=i//2-2
        d=-(a*x+b*y+c*z); ans=a+b+c
        items.append(_item(f'Mặt phẳng (P): {a}X+({b})Y+({c})Z+({d})=0. Chọn pháp tuyến n đúng bằng bộ hệ số (A;B;C) của phương trình này. Tính tổng tọa độ n.',ans,
                           f'Phương trình tổng quát AX+BY+CZ+D=0 có pháp tuyến (A;B;C). '
                           f'Suy ra n=({a};{b};{c}); tổng bằng {ans}.'))
    return _new(12,'mat_phang_oxyz','Nhận diện vectơ pháp tuyến của mặt phẳng',
                'Hệ số trong phương trình tổng quát mặt phẳng',
                'Đọc bộ hệ số (A,B,C) trong AX+BY+CZ+D=0',
                'Vectơ pháp tuyến khác vectơ không',
                'Nhận diện pháp tuyến, khác tính khoảng cách điểm đến mặt phẳng',items,'employ')


def g12_sphere_radius():
    items=[]
    for i in range(10):
        a=i%5-2;b=i%3-1;c=i//2-2;r=i%6+2;d=a*a+b*b+c*c-r*r
        items.append(_item(f'Mặt cầu (S): x²+y²+z²+({-2*a})x+({-2*b})y+({-2*c})z+({d})=0. Tính bán kính.',r,
                           f'Hoàn thành bình phương: (x−({a}))²+(y−({b}))²+(z−({c}))²={r*r}. '
                           f'Bán kính không âm R=√{r*r}={r}.'))
    return _new(12,'g12_geom_sphere_equation','Nhận diện bán kính mặt cầu từ phương trình khai triển',
                'Phương trình mặt cầu và bán kính',
                'Hoàn thành bình phương trên ba tọa độ rồi khai căn',
                'Hệ số cho R>0 và xác định mặt cầu thực',
                'Bán kính mặt cầu trong Oxyz, khác tâm hoặc giao mặt phẳng',items,'reasoning')


def g12_point_plane_distance():
    items=[]
    for i in range(10):
        x=i-4;y=i%3-1;z=i%6-2;k=i//2-3;ans=abs(z-k)
        items.append(_item(f'Trong Oxyz, tính khoảng cách từ A({x};{y};{z}) tới mặt phẳng (P): z={k}.',ans,
                           f'Mặt phẳng z={k} song song mặt phẳng Oxy, nên khoảng cách '
                           f'từ A đến (P) là |z_A−{k}|=|{z}−({k})|={ans}.'))
    return _new(12,'g12_geom_point_plane_distance','Khoảng cách từ điểm tới mặt phẳng z=k',
                'Khoảng cách Euclid theo phương pháp tuyến đơn vị',
                'Lấy giá trị tuyệt đối độ chênh tọa độ z',
                'Mặt phẳng z=k; điểm có tọa độ thực',
                'Khoảng cách điểm-mặt phẳng, khác phương trình mặt phẳng',items,'interpret')


def g12_volume():
    items=[]
    for i in range(10):
        r=i%4+1;h=i%6+2;coeff=r*r*h
        correct=f'{coeff}π'
        wrong=[f'{coeff+1}π',f'{coeff+2}π',f'{coeff+3}π']
        items.append(_item(f'Hình trụ tròn xoay có bán kính đáy r={r} và chiều cao h={h}. Thể tích V bằng bao nhiêu?',correct,
                           f'V=πr²h=π×({r})²×({h})={coeff}π (đơn vị thể tích).',wrong))
    return _new(12,'the_tich_khong_gian','Tính thể tích hình trụ tròn xoay',
                'Thể tích hình trụ bằng diện tích đáy nhân chiều cao',
                'Tính πr²h với r,h dương',
                'Bán kính đáy và chiều cao cùng đơn vị',
                'Thể tích hình trụ, không phải diện tích toàn phần hay hình nón',items,'employ')


def g12_vector_3d():
    items=[]
    for i in range(10):
        x=i-4;y=i%5-2;z=i//2-2;ans=x*x+y*y+z*z
        items.append(_item(f'Trong Oxyz cho vectơ a=({x};{y};{z}). Tính bình phương độ dài |a|².',ans,
                           f'Bình phương độ dài bằng tổng bình phương các tọa độ: '
                           f'|a|²=({x})²+({y})²+({z})²={ans}.'))
    return _new(12,'g12_geom_vectors_3d','Tính bình phương độ dài vectơ Oxyz',
                'Chuẩn Euclid của vectơ trong R³',
                'Lấy tổng bình phương ba tọa độ',
                'Vectơ có ba tọa độ thực',
                'Chuẩn bình phương, khác tích vô hướng hai vectơ',items,'employ')


def g12_asymptote():
    items=[]
    for i in range(10):
        h=i-5;a=i%3+2; b=-(a*h); c=i%5+1; d=i%6+1
        # Nonzero remainder => true vertical asymptote at h.
        items.append(_item(f'Hàm f(x)=({c}x+({-c*h+d}))/({a}x+({b})) có tiệm cận đứng x=m. Tìm m.',h,
                           f'Mẫu {a}x+({b})=0 khi x={h}. Tại đây tử bằng {d}≠0, '
                           f'nên x={h} là tiệm cận đứng, m={h}.'))
    return _new(12,'tien_can','Xác định tiệm cận đứng của phân thức bậc nhất',
                'Đường tiệm cận đứng tại nghiệm đơn của mẫu không triệt tiêu tử',
                'Giải mẫu bằng 0 và kiểm tra tử tại nghiệm mẫu khác 0',
                'Mẫu bậc nhất với hệ số x khác 0, tử không cùng nghiệm',
                'Tiệm cận đứng, khác tiệm cận ngang',items,'reasoning')


def g12_variance():
    items=[]
    for i in range(10):
        mean=i-3; d=i%5+1; data=[mean-d,mean,mean+d]; variance=Fraction(2*d*d,3)
        ans=_fraction(variance.numerator,variance.denominator)
        wrong=[]
        for n in [_fraction(d*d,3),str(d*d),_fraction(2*d*d,2),'0','1']:
            if n!=ans and n not in wrong:wrong.append(n)
        items.append(_item(f'Ba số liệu là {data[0]}, {data[1]}, {data[2]}. Tính phương sai chia cho n=3 (không dùng hiệu chỉnh n−1).',ans,
                           f'Số trung bình là {mean}. Tổng bình phương độ lệch là '
                           f'({-d})²+0²+{d}²={2*d*d}; chia 3 được {ans}.',wrong[:3]))
    return _new(12,'thong_ke_12','Tính phương sai tổng thể cho ba quan sát đối xứng',
                'Trung bình của bình phương độ lệch khỏi giá trị trung bình',
                'Tìm trung bình, tổng bình phương độ lệch, chia cho n',
                'Dữ liệu không ghép nhóm, định nghĩa phương sai với mẫu số n',
                'Phương sai khác độ lệch chuẩn và trung vị',items,'interpret')


GENERATORS = {
    'g10-system-substitution':g10_systems,
    'g10-counting-multiplication':g10_counting,
    'g10-combinations-unordered':g10_combinations,
    'g10-classical-probability':g10_probability,
    'g10-sample-mean':g10_mean,
    'g10-vector-dot':g10_vector_dot,
    'g10-coordinate-midpoint':g10_midpoint,
    'g10-linear-root':g10_line_zero,
    'g10-linear-inequality':g10_inequality,
    'g10-circle-radius':g10_circle_radius,
    'g11-polynomial-derivative':g11_derivative,
    'g11-factor-limit':g11_limit,
    'g11-translation':g11_translation,
    'g11-reflection-axis':g11_reflection,
    'g11-median':g11_median,
    'g11-continuity-parameter':g11_continuity,
    'g11-independent-events':g11_independent,
    'g11-additive-recurrence':g11_recurrence,
    'g11-origin-homothety':g11_homothety,
    'g11-trigonometric-identity':g11_trig_identity,
    'g12-exponential-equation':g12_exponential,
    'g12-basic-logarithm':g12_logarithm,
    'g12-definite-polynomial-integral':g12_integral,
    'g12-global-minimum':g12_extrema,
    'g12-plane-normal':g12_plane_eval,
    'g12-sphere-radius':g12_sphere_radius,
    'g12-point-horizontal-plane-distance':g12_point_plane_distance,
    'g12-cylinder-volume':g12_volume,
    'g12-vector-3d-norm-squared':g12_vector_3d,
    'g12-rational-vertical-asymptote':g12_asymptote,
    'g12-population-variance':g12_variance,
}


def candidate_forms():
    return [(slug,fn()) for slug,fn in GENERATORS.items()]
