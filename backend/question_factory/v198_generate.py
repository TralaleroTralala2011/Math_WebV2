#!/usr/bin/env python3
"""V198: deterministic, exact-oracle checked mathematics question bank expansion.

The families are *candidates* pending semantic independence review. Numerical
variants are 10 exercises of ONE family, never counted as different families.
Only operates on a staging JSONL; database import is separate and auditable.
"""
from __future__ import annotations
import collections
from fractions import Fraction as F
from math import factorial, comb, gcd
import json, random, re, hashlib
from pathlib import Path
import sympy as S

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'bank_updates'
CATALOG = {(int(g), v['id']) for g,topics in json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text()).items() for v in topics}

# (grade, topic, name, method, conditions, difficulty, oracle description)
SPECS = {
 'set_exactly_two':(10,'tap_hop','Đếm phần tử thuộc đúng hai trong ba tập','Sử dụng nguyên lý bù trừ trên các giao đôi và giao ba','Các số giao đôi đều chứa giao ba; mô hình tập hữu hạn','trung cấp','Mô phỏng trực tiếp các phần tử thuộc hai tập'),
 'multiset_permutation':(10,'hoan_vi_chinh_hop_to_hop','Hoán vị của dãy có các phần tử lặp','Chia n! cho tích giai thừa số lần lặp của từng phần tử','Số lượng phần tử từng loại là số nguyên dương','trung cấp','Đếm theo phép chọn vị trí cho hai loại rồi điền phần còn lại'),
 'derangements':(10,'g10_combinatorics_olympiad','Hoán vị không có phần tử tại vị trí ban đầu','Nguyên lý bù trừ để đếm các hoán vị không điểm cố định','n vật phân biệt, n>=3','nâng cao','Truy hồi D(n)=(n-1)(D(n-1)+D(n-2))'),
 'picks_theorem':(10,'toa_do_hinh_hoc_10','Đếm điểm nguyên nằm trong tam giác bằng định lý Pick','I=S-B/2+1, B là số điểm nguyên trên biên','Tam giác có tọa độ nguyên không suy biến','nâng cao','Đếm trực tiếp các cặp tọa độ nguyên nằm trong tam giác'),
 'quadratic_vieta':(10,'phuong_trinh','Tìm tích nghiệm phương trình bậc hai không giải nghiệm','Hệ thức Viète r1r2=c/a','Hệ số bậc hai khác 0, biệt thức không âm','nền tảng','Giải phương trình bằng SymPy và nhân hai nghiệm'),
 'right_inradius':(10,'he_thuc_luong_tam_giac','Bán kính đường tròn nội tiếp tam giác vuông','r=(a+b-c)/2 từ diện tích và nửa chu vi','Hai cạnh góc vuông dương, cạnh huyền đúng Pythagore','trung cấp','Tính r=diện tích / nửa chu vi'),
 'circle_chord':(10,'g10_geom_circle_chords_arcs','Độ dài dây cung khi biết bán kính và khoảng cách đến tâm','Dây cung bằng 2sqrt(R²-d²)','0<d<R; khoảng vuông góc từ tâm tới dây','trung cấp','Thế ngược vào quan hệ Pythagore (chord/2)²+d²=R²'),
 'polygon_shoelace':(10,'hinh_hoc_10','Diện tích đa giác có tọa độ bằng công thức shoelace','S=|sum(x_i y_(i+1)-y_i x_(i+1))|/2','Đỉnh đa giác theo thứ tự, không tự cắt','trung cấp','Đối chiếu diện tích với sympy.geometry.Polygon'),
 'vector_orthogonal':(10,'g10_geom_vector_proofs','Tìm tham số để hai vectơ vuông góc','Tích vô hướng hai vectơ bằng 0','Vectơ hai chiều khác vectơ không','trung cấp','Thế tham số ngược kiểm tra tích vô hướng và tính duy nhất'),
 'linear_optimization':(10,'he_bat_phuong_trinh','Tối ưu hàm tuyến tính trên miền tam giác','Hàm tuyến tính đạt cực trị tại một trong các đỉnh','x>=0,y>=0 và ax+by<=c với a,b,c>0','nâng cao','Liệt kê ba đỉnh, kiểm tra giá trị tại các đỉnh'),
 'central_moment':(10,'thong_ke','Tính phương sai tổng thể qua trung bình bình phương','Var=E(X²)-E(X)²','Dãy giá trị hữu hạn và phương sai định nghĩa theo tổng chia n','trung cấp','Tính trực tiếp tổng (x-xbar)²/n'),
 'integer_points_circle':(10,'duong_tron','Đếm điểm nguyên trên đường tròn x²+y²=R²','Liệt kê các biểu diễn R² dưới dạng tổng hai bình phương','Bán kính R nguyên dương','nâng cao','Duyệt trực tiếp cặp (x,y) trong [-R,R]²'),
 'binomial_exact_k':(11,'bien_co_doc_lap_11','Xác suất đúng k thành công trong n phép thử độc lập','P=C(n,k)p^k(1-p)^(n-k)','Các phép thử Bernoulli độc lập, cùng xác suất p','trung cấp','Tổng xác suất trên mọi chuỗi nhị phân có k thành công'),
 'bayes_defect':(11,'g11_conditional_probability_models','Áp dụng công thức Bayes để truy nguồn sản phẩm lỗi','P(A|D)=P(D|A)P(A)/P(D)','Kho gồm sản phẩm từ hai dây chuyền; số lượng và số lỗi từng nguồn biết chính xác','nâng cao','Đếm số sản phẩm lỗi theo từng nguồn trên quần thể hữu hạn'),
 'recurrence_second_order':(11,'day_so_truy_hoi_11','Giải truy hồi bậc hai có hai nghiệm đặc trưng khác nhau','u_n=A2^n+B3^n từ truy hồi u_n=5u_(n-1)-6u_(n-2)','u0,u1 suy ra A,B; n>=2','nâng cao','Lặp trực tiếp truy hồi từ u0,u1'),
 'tangent_add':(11,'cong_thuc_luong_giac','Tính tang của tổng hai góc qua hai tang thành phần','tan(a+b)=(tan a+tan b)/(1-tan a tan b)','cos(a+b) khác 0, hai tang xác định','trung cấp','Kiểm tra đồng nhất thức bằng biến đổi đại số phân số'),
 'triple_sine':(11,'gia_tri_luong_giac','Tính sin(3a) từ sin(a)','sin(3a)=3sin(a)-4sin³(a)','Góc a có sin cho trước thuộc [-1,1]','trung cấp','Đối chiếu với sin(3asin(s)) từ SymPy'),
 'implicit_circle_derivative':(11,'dao_ham_quy_tac','Đạo hàm ẩn của đường elip tại điểm xác định','Từ x²+2y²=C suy ra y’=-x/(2y)','y khác 0, tiếp tuyến có hệ số góc hữu hạn','nâng cao','Đối chiếu đạo hàm nhánh y=sqrt((C-x²)/2)'),
 'section_pyramid_volume_ratio':(11,'thiet_dien_hinh_khong_gian_11','Tỉ số thể tích hình chóp nhỏ cắt song song đáy','Tỉ số thể tích bằng lập phương tỉ số chiều cao','Mặt cắt song song đáy, tỉ số h/H nằm giữa 0 và 1','trung cấp','Đối chiếu thể tích bằng tích diện tích đáy và chiều cao'),
 'homothety_area':(11,'phep_bien_hinh_11','Ảnh của diện tích dưới phép vị tự tỉ số âm','Diện tích ảnh bằng bình phương trị tuyệt đối tỉ số vị tự','Hình có diện tích dương; k!=0','trung cấp','Tính diện tích qua định thức tọa độ của tam giác ảnh'),
 'probability_independence_gap':(11,'bien_co_doc_lap_11','Kiểm tra độc lập bằng hiệu P(A∩B)-P(A)P(B)','Tính hai xác suất biên và xác suất giao từ bảng chéo','Bảng tần số bốn ô không âm, tổng dương','nâng cao','Đối chiếu độc lập trực tiếp từ tích tần suất giao'),
 'telescoping_product':(11,'day_so','Tính tích hữu hạn phân số 1−1/k²','Phân tích (k−1)(k+1)/k² rồi triệt tiêu tích','k chạy từ 2 đến n với n>=2','trung cấp','Nhân trực tiếp tất cả các phân số chính xác'),
 'reflection_line':(11,'g11_geom_transform_reflection','Phép đối xứng đường thẳng qua trục tung','Đồ thị ảnh của y=mx+b có phương trình y=−mx+b','Đường thẳng không thẳng đứng','nền tảng','Biến đổi hai điểm trên đường rồi lập phương trình ảnh'),
 'oblique_asymptote':(12,'tien_can','Xác định tung độ gốc tiệm cận xiên của phân thức bậc hai trên bậc nhất','Chia đa thức để lấy phần thương, phần dư tiến về 0','Mẫu tuyến tính có hệ số cao nhất khác 0','trung cấp','SymPy chia đa thức rồi lấy giới hạn f(x)-ax khi x→∞'),
 'line_plane_t':(12,'g12_geom_line_plane_intersection','Tìm tham số giao điểm đường thẳng với mặt phẳng','Thế P+t v vào ax+by+cz=d, giải phương trình bậc nhất','Vectơ chỉ phương không song song với mặt phẳng','trung cấp','Tính tích vô hướng tọa độ giao với pháp tuyến'),
 'sphere_section_radius_sq':(12,'g12_geom_sphere_plane_intersection','Bình phương bán kính đường tròn giao mặt cầu và mặt phẳng','r²=R²−d² với d là khoảng cách từ tâm đến mặt phẳng','Khoảng cách d nhỏ hơn R','trung cấp','Đối chiếu qua lát cắt Pythagore của mặt cầu'),
 'reflect_point_plane':(12,'hinh_hoc_oxyz_van_dung_12','Ảnh của điểm qua mặt phẳng bất kỳ','P’=P−2(n·P−d)n/||n||²','Pháp tuyến n khác 0','nâng cao','Trung điểm nằm trên mặt phẳng và PP’ song song pháp tuyến'),
 'complex_power':(12,'so_phuc','Phần thực lũy thừa của số phức 1+i','Dùng khai triển nhị thức hoặc De Moivre để lấy Re((1+i)^n)','n là số nguyên không âm','trung cấp','Đối chiếu trực tiếp khai triển biểu thức phức với SymPy'),
 'complex_conjugate_roots':(12,'pt_so_phuc','Hệ số bậc nhất của đa thức thực nhận một cặp nghiệm liên hợp','(x-(a+bi))(x-(a-bi))=x²−2ax+(a²+b²)','a,b thực, b khác 0','trung cấp','Khai triển đa thức bằng SymPy'),
 'symmetric_integral':(12,'nguyen_ham_tich_phan','Tích phân đa thức trên đoạn đối xứng bằng triệt tiêu phần lẻ','Tích phân phần lẻ bằng 0; tích phân phần chẵn theo nguyên hàm','Đa thức liên tục, cận [-a,a]','trung cấp','Đối chiếu tích phân trực tiếp với SymPy'),
 'solid_revolution_over_pi':(12,'g12_solid_of_revolution','Thể tích tròn xoay chia π khi bình phương bán kính tuyến tính','V/π=∫(mx+b)dx (phương pháp đĩa)','mx+b>=0 trên đoạn tích phân','trung cấp','Tích phân trực tiếp bằng SymPy'),
 'skew_lines_scaled_distance_sq':(12,'g12_geom_skew_line_relation','Bình phương khoảng cách giữa hai đường thẳng chéo nhau','d²=((P2−P1)·(u×v))²/||u×v||²','Hai vectơ chỉ phương không song song','nâng cao','Dùng nghiệm cực tiểu bình phương khoảng cách theo hai tham số'),
 'discrete_second_moment':(12,'xac_suat_12','Kỳ vọng của bình phương biến ngẫu nhiên rời rạc','E(X²)=Σx_i²p_i','p_i không âm và có tổng bằng 1','trung cấp','Mô phỏng bảng tần số của không gian mẫu hữu hạn'),
 'orthogonal_plane_angle':(12,'g12_geom_two_planes_angle','Bình phương cos góc giữa hai mặt phẳng trong Oxyz','cos²θ=(n1·n2)²/(||n1||²||n2||²)','Hai vectơ pháp tuyến khác 0','trung cấp','Tính qua định thức Gram của hai vectơ pháp tuyến'),
}

def fmt(v):
    q=S.Rational(v)
    return str(q.p) if q.q==1 else f'{q.p}/{q.q}'

def problem(key,i):
    t=i+1
    if key=='set_exactly_two':
        a,b,c=2+t%4,3+t%3,4+t%3; triple=t%3+1
        ab,ac,bc=a+triple,b+triple,c+triple
        ans=a+b+c
        x=[('ab',j) for j in range(a)]+[('ac',j) for j in range(b)]+[('bc',j) for j in range(c)]+[('abc',j) for j in range(triple)]
        assert ans==sum(v[0] in ('ab','ac','bc') for v in x)
        q=f'Ba tập A, B, C có |A∩B|={ab}, |A∩C|={ac}, |B∩C|={bc}, |A∩B∩C|={triple}. Có bao nhiêu phần tử thuộc đúng hai tập?'
        sol=f'Các giao đôi đều đếm mỗi phần tử giao ba ba lần. Số phần tử thuộc đúng hai tập = {ab}+{ac}+{bc}−3×{triple} = {ans}.'
    elif key=='multiset_permutation':
        a,b,c=2+t,2+t%3,1+t%2; n=a+b+c
        ans=factorial(n)//(factorial(a)*factorial(b)*factorial(c))
        assert ans==comb(n,a)*comb(n-a,b)
        q=f'Một dãy gồm {a} chữ A, {b} chữ B và {c} chữ C. Có bao nhiêu cách xếp thành một hàng phân biệt?'
        sol=f'Có {n}! cách nếu phân biệt tất cả; chia cho {a}!, {b}!, {c}! vì các chữ cùng loại đổi chỗ không tạo dãy mới. Kết quả {n}!/({a}!{b}!{c}!)={ans}.'
    elif key=='derangements':
        n=3+t;ans=sum((-1)**k*factorial(n)//factorial(k) for k in range(n+1))
        d0,d1=1,0
        for j in range(2,n+1):d0,d1=d1,(j-1)*(d0+d1)
        assert ans==d1
        q=f'Có {n} người gửi {n} lá thư tới đúng {n} người nhận khác nhau, mỗi người có một lá dành cho mình. Có bao nhiêu cách phân phát sao cho không ai nhận đúng lá của mình?'
        sol=f'Theo nguyên lý bù trừ, số hoán vị không điểm cố định là D_{n}={n}! Σ_{{k=0}}^{n}(-1)^k/k! = {ans}; cũng kiểm tra được bằng truy hồi D_n=(n−1)(D_(n−1)+D_(n−2)).'
    elif key=='picks_theorem':
        a,b=4+t,3+t;Sarea=S.Rational(a*b,2);B=a+b+gcd(a,b);ans=Sarea-S.Rational(B,2)+1
        assert ans==sum(1 for x in range(1,a) for y in range(1,b) if b*x+a*y<a*b)
        q=f'Tam giác có các đỉnh O(0,0), A({a},0), B(0,{b}). Có bao nhiêu điểm có cả hai tọa độ nguyên nằm hoàn toàn bên trong tam giác?'
        sol=f'Diện tích S={a}×{b}/2={fmt(Sarea)}; biên có B={a}+{b}+gcd({a},{b})={B} điểm nguyên. Định lý Pick: I=S−B/2+1={fmt(ans)}.'
    elif key=='quadratic_vieta':
        a=1+t%4; r1=-(2+t%5);r2=3+t%7;b=-a*(r1+r2);c=a*r1*r2;ans=r1*r2
        x=S.symbols('x'); assert S.solve(a*x*x+b*x+c,x)==sorted([S.Integer(r1),S.Integer(r2)])
        q=f'Không giải phương trình, hãy tính tích hai nghiệm của {a}x²+({b})x+({c})=0.'
        sol=f'Phương trình bậc hai có hai nghiệm {r1}, {r2} (biệt thức dương). Theo Viète, x₁x₂=c/a={c}/{a}={ans}.'
    elif key=='right_inradius':
        triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
        a,b,c=triples[i];ans=S.Rational(a+b-c,2)
        assert ans==S.Rational(a*b,2)/S.Rational(a+b+c,2)
        q=f'Tam giác vuông có hai cạnh góc vuông dài {a} và {b}, cạnh huyền {c}. Tính bán kính đường tròn nội tiếp.'
        sol=f'Diện tích S={a}×{b}/2; nửa chu vi p=({a}+{b}+{c})/2; r=S/p=({a}+{b}−{c})/2={fmt(ans)}.'
    elif key=='circle_chord':
        triples=[(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37),(11,60,61),(28,45,53),(16,63,65)]
        half,d,R=triples[i];ans=2*half; assert (ans//2)**2+d*d==R*R
        q=f'Đường tròn bán kính {R}, khoảng cách từ tâm đến dây cung AB bằng {d}. Tính độ dài dây AB.'
        sol=f'Đường vuông góc từ tâm chia dây thành đôi: (AB/2)²=R²−d²={R}²−{d}²={half**2}. Suy ra AB=2×{half}={ans}.'
    elif key=='polygon_shoelace':
        a,b,h=3+t,2+t%5,2+t%4
        pts=[(0,0),(a,0),(a+b,h),(0,h)]
        twice=sum(pts[k][0]*pts[(k+1)%4][1]-pts[k][1]*pts[(k+1)%4][0] for k in range(4))
        ans=S.Rational(abs(twice),2)
        assert abs(S.geometry.Polygon(*[S.Point(*xy) for xy in pts]).area)==ans
        q=f'Tứ giác lần lượt có đỉnh A(0,0), B({a},0), C({a+b},{h}), D(0,{h}). Tính diện tích tứ giác bằng tọa độ.'
        sol=f'Áp dụng công thức shoelace cho bốn đỉnh theo thứ tự, tổng định thức có trị tuyệt đối {abs(twice)}. Diện tích S=|Σ(x_i y_(i+1)−y_i x_(i+1))|/2={fmt(ans)}.'
    elif key=='vector_orthogonal':
        a=2+t;b=2+t%4; c=2+t%3;ans=-b*c
        assert ans*1+b*c==0
        q=f'Trong Oxy, cho u=(m,{b}) và v=(1,{c}). Hãy tìm m để hai vectơ u,v vuông góc.'
        sol=f'Tích vô hướng u·v=m×1+{b}×{c}=m+{b*c}. Hai vectơ vuông góc khi u·v=0, suy ra m={ans}. Đây là nghiệm duy nhất vì hệ số của m khác 0.'
    elif key=='linear_optimization':
        a,b=2+t%4,3+t%4;c=a*b*(3+t)
        u,v=2+t%5,3+t%5
        val1=S.Rational(u*c,a);val2=S.Rational(v*c,b);ans=max(val1,val2)
        assert ans==max(0,u*(c//a),v*(c//b))
        q=f'Tìm giá trị lớn nhất của F={u}x+{v}y trên miền x≥0, y≥0, {a}x+{b}y≤{c}.'
        sol=f'Miền nghiệm là tam giác với các đỉnh (0,0),({c//a},0),(0,{c//b}). Giá trị F tại ba đỉnh lần lượt 0, {fmt(val1)}, {fmt(val2)}. Do F tuyến tính, cực đại là {fmt(ans)}.'
    elif key=='central_moment':
        a=1+t;d=1+t%5;vals=[a-d,a,a+d,a+2*d]; n=len(vals); m=F(sum(vals),n)
        ans=F(sum(v*v for v in vals),n)-m*m
        assert ans==F(sum((F(v)-m)**2 for v in vals),n)
        q=f'Cho mẫu số liệu {vals}. Tính phương sai theo công thức chia cho n={n} (không phải n−1).'
        sol=f'Trung bình x̄=({"+".join(map(str,vals))})/{n}={fmt(m)}. Dùng Var=Σxᵢ²/{n}−x̄²={fmt(F(sum(v*v for v in vals),n))}−({fmt(m)})²={fmt(ans)}.'
    elif key=='integer_points_circle':
        R=3+t;ans=sum(x*x+y*y==R*R for x in range(-R,R+1) for y in range(-R,R+1))
        roots=sum((1 if R*R-x*x==0 else 2) for x in range(-R,R+1) if x*x<=R*R and S.integer_nthroot(R*R-x*x,2)[1])
        assert ans==roots
        q=f'Có bao nhiêu điểm M(x,y) với x,y đều nguyên nằm trên đường tròn x²+y²={R*R}?'
        sol=f'Ta xét x nguyên từ −{R} đến {R}, và giữ những x sao cho {R*R}−x² là số chính phương; mỗi y≠0 cho hai dấu ±y. Cộng cả trường hợp y=0 thu được {ans} điểm.'
    elif key=='binomial_exact_k':
        n=5+t%5;k=1+t%3;p=S.Rational(1+t%3,5)
        ans=comb(n,k)*p**k*(1-p)**(n-k)
        q=f'Một phép thử thành công với xác suất {fmt(p)}, các lần thử độc lập. Trong {n} lần thử, xác suất có đúng {k} lần thành công bằng bao nhiêu?'
        sol=f'Chọn vị trí của {k} lần thành công có C({n},{k}) cách. Mỗi chuỗi có xác suất ({fmt(p)})^{k}×(1−{fmt(p)})^{n-k}. Do đó P=C({n},{k})p^{k}(1−p)^{n-k}={fmt(ans)}.'
        assert ans==sum(p**k*(1-p)**(n-k) for _ in range(comb(n,k)))
    elif key=='bayes_defect':
        a,b=15+t,10+t; defectiveA=2+t%4; defectiveB=3+t%3; totalA=3*a;totalB=4*b
        # rates chosen from realistic integer counts for 2 groups
        ans=S.Rational(defectiveA,defectiveA+defectiveB)
        assert ans== (S.Rational(defectiveA,totalA)*S.Rational(totalA,totalA+totalB))/(S.Rational(defectiveA+defectiveB,totalA+totalB))
        q=f'Nhà máy có {totalA} sản phẩm từ dây chuyền A (trong đó {defectiveA} lỗi) và {totalB} sản phẩm từ B (trong đó {defectiveB} lỗi). Lấy ngẫu nhiên một sản phẩm từ toàn bộ kho; biết nó bị lỗi. Xác suất sản phẩm đến từ A?'
        sol=f'Đặt D là biến cố lỗi. P(A∩D)={defectiveA}/{totalA+totalB}, P(D)=({defectiveA}+{defectiveB})/{totalA+totalB}. Theo Bayes, P(A|D)=P(A∩D)/P(D)={fmt(ans)}.'
    elif key=='recurrence_second_order':
        A=1+t%5;B=2+t%4;n=2+t%8;u0=A+B;u1=2*A+3*B
        ans=A*2**n+B*3**n; x,y=u0,u1
        for _ in range(2,n+1):x,y=y,5*y-6*x
        assert ans==y
        q=f'Dãy số thỏa u₀={u0}, u₁={u1}, uₙ=5uₙ₋₁−6uₙ₋₂ (n≥2). Tính u_{n}.'
        sol=f'Phương trình đặc trưng r²−5r+6=0 có r=2,3. Suy ra uₙ=A·2ⁿ+B·3ⁿ. Từ u₀={u0},u₁={u1} tìm A={A},B={B}; u_{n}={A}·2^{n}+{B}·3^{n}={ans}.'
    elif key=='tangent_add':
        a=S.Rational(1+t%3,3+t%4);b=S.Rational(1+t%4,5+t%3)
        ans=(a+b)/(1-a*b);assert (1-a*b)!=0
        assert S.simplify(ans*(1-a*b)-(a+b))==0
        q=f'Biết tan α={fmt(a)} và tan β={fmt(b)}, cả hai góc có tang xác định và cos(α+β)≠0. Tính tan(α+β).'
        sol=f'Theo công thức cộng tang: tan(α+β)=(tanα+tanβ)/(1−tanα·tanβ)=[{fmt(a)}+{fmt(b)}]/[1−({fmt(a)})({fmt(b)})]={fmt(ans)}.'
    elif key=='triple_sine':
        s=S.Rational(t+1,t+10);ans=3*s-4*s**3
        assert S.simplify(S.expand_trig(S.sin(3*S.asin(s)))-ans)==0
        q=f'Cho sin α={fmt(s)} và α là góc nhọn. Tính sin(3α).'
        sol=f'Dùng công thức góc ba: sin(3α)=3sinα−4sin³α=3×({fmt(s)})−4×({fmt(s)})³={fmt(ans)}.'
    elif key=='implicit_circle_derivative':
        x0=2+t;y0=1+t%4;C=x0*x0+2*y0*y0
        ans=S.Rational(-x0,2*y0)
        x=S.symbols('x',real=True); y=S.sqrt((C-x*x)/2)
        assert S.simplify(S.diff(y,x).subs(x,x0)-ans)==0
        q=f'Đường cong x²+2y²={C}, tại điểm M({x0},{y0}) có y>0. Tính đạo hàm y′ tại M theo x.'
        sol=f'Lấy đạo hàm hai vế theo x: 2x+4yy′=0, nên y′=−x/(2y). Thay M({x0},{y0}) suy ra y′={fmt(ans)}.'
    elif key=='section_pyramid_volume_ratio':
        h=1+t%7;H=h+2+t%5
        ans=S.Rational(h,H)**3
        assert ans==S.Rational(h*h,H*H)*S.Rational(h,H)
        q=f'Mặt phẳng song song với đáy cắt hình chóp, tạo hình chóp nhỏ cùng đỉnh có chiều cao {h}; hình chóp lớn có chiều cao {H}. Tính tỉ số thể tích hình chóp nhỏ so với hình chóp lớn.'
        sol=f'Hai hình chóp đồng dạng với tỉ số cạnh k={h}/{H}; tỉ số diện tích đáy k², tỉ số chiều cao k, nên tỉ số thể tích k³=({h}/{H})³={fmt(ans)}.'
    elif key=='homothety_area':
        k=-(2+t%5);area=3+t;ans=k*k*area
        pts=[(0,0),(area,0),(0,2)]
        transformed=[(k*x,k*y) for x,y in pts]
        shoelace=abs(sum(transformed[j][0]*transformed[(j+1)%3][1]-transformed[j][1]*transformed[(j+1)%3][0] for j in range(3)))//2
        assert ans==shoelace
        q=f'Một tam giác có diện tích {area} đơn vị². Qua phép vị tự tâm O có tỉ số k={k}, ảnh của tam giác có diện tích bằng bao nhiêu?'
        sol=f'Phép vị tự nhân mọi chiều dài với |k|={abs(k)}, nên diện tích nhân k²={k*k}. Diện tích ảnh bằng {area}×{k*k}={ans} đơn vị².'
    elif key=='probability_independence_gap':
        a,b,c,d=2+t%3,3+t%4,2+t%4,4+t%5;total=a+b+c+d
        A=a+b;B=a+c
        ans=S.Rational(a,total)-S.Rational(A*B,total*total)
        assert ans==S.Rational(a*total-(a+b)*(a+c),total*total)
        q=f'Bảng chéo hai biến cố A,B có n(A∩B)={a}, n(A∩B̄)={b}, n(Ā∩B)={c}, n(Ā∩B̄)={d}, tất cả kết quả đồng khả năng. Tính P(A∩B)−P(A)P(B).'
        sol=f'Tổng số kết quả N={total}. P(A∩B)={a}/{total}; P(A)={A}/{total}; P(B)={B}/{total}. Hiệu = {a}/{total}−({A}/{total})({B}/{total})={fmt(ans)}.'
    elif key=='telescoping_product':
        n=3+t;ans=S.Rational(n+1,2*n)
        product=S.prod(S.Rational(k*k-1,k*k) for k in range(2,n+1))
        assert ans==product
        q=f'Tính tích P=(1−1/2²)(1−1/3²)…(1−1/{n}²) theo phân số tối giản.'
        sol=f'Mỗi thừa số 1−1/k²=((k−1)/k)((k+1)/k). Triệt tiêu tích từ k=2 đến n: P=(1/n)×((n+1)/2)=({n}+1)/(2×{n})={fmt(ans)}.'
    elif key=='reflection_line':
        m=1+t;b=-(2+t%6);ans=-m
        x1,x2=1,3;y1=m*x1+b;y2=m*x2+b
        assert S.Rational(y2-y1,-x2+x1)==ans
        q=f'Đối xứng đường thẳng d: y={m}x+({b}) qua trục tung Oy ta được đường thẳng d′. Tìm hệ số góc của d′.'
        sol=f'Phép đối xứng Oy biến (x,y) thành (−x,y). Thế x=−x′ vào y={m}x+({b}), được y=−{m}x′+({b}); hệ số góc là {ans}.'
    elif key=='oblique_asymptote':
        a=1+t%5;b=2+t;c=4+t;d=1+t%6
        x=S.symbols('x'); num=a*x*x+b*x+c;den=x+d
        qout,rem=S.div(num,den,x);ans=b-a*d
        assert S.expand(qout)==a*x+ans and S.limit(num/den-a*x,x,S.oo)==ans
        q=f'Hàm số y=({a}x²+{b}x+{c})/(x+{d}) có tiệm cận xiên y={a}x+β. Tính β.'
        sol=f'Chia đa thức: ({a}x²+{b}x+{c})/(x+{d}) = {a}x+({ans}) + ({S.expand(rem)})/(x+{d}). Phần dư tiến tới 0 khi x→∞ nên β={ans}.'
    elif key=='line_plane_t':
        a,b,c=1+t%3,2+t%4,3+t%5
        p=(t,1+t%3,2+t%4);v=(1,2,3);target=t%6+2
        d=sum(j*k for j,k in zip((a,b,c),p))+target*(a+2*b+3*c)
        ans=target
        assert sum(j*(w+ans*vv) for j,w,vv in zip((a,b,c),p,v))==d
        q=f'Đường thẳng d: (x,y,z)=({p[0]},{p[1]},{p[2]})+s(1,2,3). Mặt phẳng P: {a}x+{b}y+{c}z={d}. Tìm s tại giao điểm d∩P.'
        sol=f'Thế x={p[0]}+s, y={p[1]}+2s, z={p[2]}+3s vào mặt phẳng: ({a}+2·{b}+3·{c})s={d}-({a*p[0]+b*p[1]+c*p[2]}). Giải được s={ans}.'
    elif key=='sphere_section_radius_sq':
        R=7+t;dist=1+t%5; ans=R*R-dist*dist
        assert S.simplify(S.sqrt(ans)**2+dist**2-R**2)==0
        q=f'Mặt cầu có bán kính R={R}. Mặt phẳng cách tâm cầu một khoảng d={dist}. Tính bình phương bán kính đường tròn giao tuyến.'
        sol=f'Mặt phẳng cắt cầu vì {dist}<{R}. Gọi r là bán kính thiết diện, theo Pythagore r²+d²=R², suy ra r²={R}²−{dist}²={ans}.'
    elif key=='reflect_point_plane':
        # normal n=(1,2,2), ||n||²=9 and choose signed distance numerator multiple of 9
        h=1+t;c=2+t%3;p=(h,h+1,c);n=(1,2,2)
        offset=sum(p[j]*n[j] for j in range(3))-9*(1+t%3)
        signed=sum(p[j]*n[j] for j in range(3))-offset
        reflected=[S.Rational(p[j])-2*S.Rational(signed,9)*n[j] for j in range(3)]
        ans=reflected[0]
        assert sum(n[j]*(p[j]+reflected[j]) for j in range(3))==2*offset
        assert (reflected[1]-p[1])==2*(reflected[0]-p[0])
        q=f'Cho điểm P({p[0]},{p[1]},{p[2]}) và mặt phẳng α: x+2y+2z={offset}. Gọi P′ là điểm đối xứng của P qua α. Tìm hoành độ của P′.'
        sol=f'Pháp tuyến n=(1,2,2), ||n||²=9. Với n·P−{offset}={signed}, P′=P−2({signed}/9)n. Hoành độ x′={p[0]}−2×{signed}/9={fmt(ans)}.'
    elif key=='complex_power':
        n=2+t; z=(S.Integer(1)+S.I)**n;ans=S.re(S.expand(z))
        assert ans==sum((-1)**(k//2)*comb(n,k) for k in range(0,n+1,2))
        q=f'Cho số phức z=1+i. Tính phần thực của z^{n}.'
        sol=f'Khai triển nhị thức Newton (1+i)^{n}; các hạng i^k với k lẻ cho phần ảo, còn k chẵn cho phần thực. Re(z^{n})=Σ_{{k chẵn}} C({n},k)(−1)^(k/2)={ans}.'
    elif key=='complex_conjugate_roots':
        a=t-6;b=1+t%5
        x=S.symbols('x');pol=S.expand((x-(a+S.I*b))*(x-(a-S.I*b)))
        ans=-2*a
        assert S.expand(pol).coeff(x,1)==ans
        q=f'Phương trình x²+px+q=0 có hai nghiệm phức liên hợp z₁={a}+{b}i và z₂={a}−{b}i. Tính p.'
        sol=f'Tổng hai nghiệm z₁+z₂={2*a}; theo Viète, p=−(z₁+z₂)={ans}. Tích z₁z₂={a*a+b*b} là số thực.'
    elif key=='symmetric_integral':
        a=1+t%5;p=1+t%4;q=1+t%3;r=2+t%5;s=1+t%4;h=1+t%3
        x=S.symbols('x');f=p*x**4+q*x**3+r*x**2+s*x+h
        ans=S.Rational(2*p*a**5,5)+S.Rational(2*r*a**3,3)+2*h*a
        assert S.integrate(f,(x,-a,a))==ans
        q=f'Tính I=∫ từ −{a} đến {a} của [{p}x⁴+{q}x³+{r}x²+{s}x+{h}] dx.'
        sol=f'Các hạng lẻ {q}x³ và {s}x có tích phân bằng 0 trên đoạn đối xứng. I=2×({p}·{a}⁵/5+{r}·{a}³/3+{h}·{a})={fmt(ans)}.'
    elif key=='solid_revolution_over_pi':
        m=1+t%6;b=2+t%5;L=2+t
        ans=S.Rational(m*L*L,2)+b*L
        x=S.symbols('x');assert S.integrate(m*x+b,(x,0,L))==ans
        q=f'Hình phẳng 0≤x≤{L}, 0≤y≤sqrt({m}x+{b}) quay quanh Ox tạo khối tròn xoay thể tích V. Tính V/π.'
        sol=f'Dùng phương pháp đĩa: V=π∫₀^{L} y²dx=π∫₀^{L}({m}x+{b})dx. Do đó V/π=[{m}x²/2+{b}x]₀^{L}={fmt(ans)}.'
    elif key=='skew_lines_scaled_distance_sq':
        h=1+t;v1=S.Matrix([1,1,0]);v2=S.Matrix([0,1,1]);p1=S.Matrix([0,0,0]);p2=S.Matrix([h,0,0]);cross=v1.cross(v2)
        dsq=S.Rational((p2-p1).dot(cross)**2,cross.dot(cross)); ans=3*dsq
        s,t0=S.symbols('s t',real=True); delta=p1+s*v1-p2-t0*v2
        optimum=S.solve([S.diff(delta.dot(delta),s),S.diff(delta.dot(delta),t0)],[s,t0],dict=True)[0]
        assert S.simplify(delta.dot(delta).subs(optimum)-dsq)==0
        q=f'Trong Oxyz, d₁ đi qua O(0,0,0) có vectơ chỉ phương (1,1,0); d₂ đi qua A({h},0,0) có vectơ chỉ phương (0,1,1). Gọi d là khoảng cách giữa d₁,d₂. Tính 3d².'
        sol=f'Hai vectơ chỉ phương có tích có hướng (1,−1,1), chuẩn bình phương 3. Vectơ nối hai điểm là ({h},0,0), tích hỗn tạp {h}. Vậy d²={h*h}/3, suy ra 3d²={fmt(ans)}.'
    elif key=='discrete_second_moment':
        a=1+t;counts=[1+t%3,2+t%4,3+t%5];values=[-a,0,a+2]
        n=sum(counts);ans=S.Rational(sum(v*v*c for v,c in zip(values,counts)),n)
        assert ans==sum(S.Rational(counts[j],n)*values[j]**2 for j in range(3))
        q=f'Biến ngẫu nhiên X nhận các giá trị {values[0]}, {values[1]}, {values[2]} với xác suất tương ứng {counts[0]}/{n}, {counts[1]}/{n}, {counts[2]}/{n}. Tính E(X²).'
        sol=f'Tổng xác suất là ({counts[0]}+{counts[1]}+{counts[2]})/{n}=1. E(X²)=Σxᵢ²pᵢ=[({-a})²×{counts[0]}+0²×{counts[1]}+({a+2})²×{counts[2]}]/{n}={fmt(ans)}.'
    elif key=='orthogonal_plane_angle':
        p=1+t%5;q=1+t%4;n1=S.Matrix([p,q,0]);n2=S.Matrix([0,q,p]);ans=S.Rational(n1.dot(n2)**2,n1.dot(n1)*n2.dot(n2))
        assert ans==1-S.Rational(n1.cross(n2).dot(n1.cross(n2)),n1.dot(n1)*n2.dot(n2))
        sol=f'cos²θ=(n₁·n₂)²/(||n₁||²||n₂||²). Có n₁·n₂={q*q}, mỗi bình phương độ dài bằng {p*p+q*q}, nên cos²θ={q**4}/({p*p+q*q}²)={fmt(ans)}.'
        q=f'Hai mặt phẳng có vectơ pháp tuyến n₁=({p},{q},0), n₂=(0,{q},{p}). Tính cos²θ, với θ là góc nhọn hoặc vuông giữa hai mặt phẳng.'
    else:raise KeyError(key)
    return q,S.Rational(ans),sol


def choices_for(ans,probability):
    a=S.Rational(ans); candidates=[]
    if probability and 0<a<1:
        for d in [S.Rational(1,9),S.Rational(1,11),S.Rational(1,13), S.Rational(1,17),S.Rational(1,23)]:
            for v in [a+d,a-d]:
                if 0<=v<=1 and v!=a and v not in candidates:candidates.append(v)
    for v in [a+1,a-1,-a,a+2,a-2,a*2,a/2,a+S.Rational(1,2),a-S.Rational(1,2)]:
        if v!=a and v not in candidates:candidates.append(v)
    assert len(candidates)>=3
    return [a]+candidates[:3]


def main():
    specs=[];rows=[];bygrade=collections.Counter();bytype=collections.Counter();shapes={}
    rng=random.Random(1982026)
    for key,(grade,topic,name,method,conditions,level,oracle) in SPECS.items():
        assert (grade,topic) in CATALOG,(grade,topic)
        specs.append({'form_id':'v198_'+key,'grade':grade,'topic':topic,'name':name,'mathematical_essence':name,'method':method,'conditions':conditions,'difficulty':level,'oracle':oracle,'independent_method_certified':False,'question_count':10})
        seen=set()
        for i in range(10):
            q,ans,sol=problem(key,i)
            assert q not in seen,(key,i,'duplicate internal prompt');seen.add(q)
            typ=('multiple_choice' if i<7 else 'short_answer' if i<9 else 'true_false')
            if typ=='multiple_choice':
                values=choices_for(ans,'probability' in key or 'bayes' in key or 'binomial' in key or 'ratio' in key or 'section_' in key)
                # rotate the correct option to avoid constant position
                pos=(i+len(key))%4
                other=values[1:]; opts=other[:pos]+[values[0]]+other[pos:]
                choices=[fmt(x) for x in opts]
                assert len(set(choices))==4
                answer=fmt(ans)
                explanation=sol+' Trong bốn lựa chọn, chỉ có '+answer+' bằng kết quả tính được.'
            elif typ=='short_answer':
                answer=fmt(ans);choices=[];explanation=sol+' Nhập phân số tối giản nếu kết quả không nguyên.'
            else:
                answer='Đúng,Sai,Đúng,Sai';choices=[f'Kết quả chính xác bằng {fmt(ans)}.',f'Kết quả nhỏ hơn {fmt(ans-1)}.',f'Kết quả lớn hơn {fmt(ans-1)}.',f'Kết quả bằng {fmt(ans+1)}.']
                explanation=sol+f' Do giá trị đúng là {fmt(ans)} nên khẳng định 1 đúng, 2 sai, 3 đúng, 4 sai.'
            row={'id':f'v198_{key}_{i:02d}','form_id':'v198_'+key,'grade':grade,'topic':topic,'concept':name,'math_method':method,'conditions':conditions,'difficulty':level,'question_type':typ,'question':q,'answer':answer,'correct_answer':answer,'solution':explanation,'choices':choices,'source_bundle':'V198','validation_status':'sympy_and_independent_exact_oracle_checked','method_independence_certified':False,'production_integrated':False}
            rows.append(row);bygrade[str(grade)]+=1;bytype[typ]+=1
    OUT.mkdir(exist_ok=True)
    spec_path=OUT/'V198_FAMILY_SPECS.json'; spec_path.write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    data_path=OUT/'V198_INCREMENT.jsonl'; data_path.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows),encoding='utf8')
    report={'version':'V198','groups':len(specs),'questions':len(rows),'per_grade':dict(bygrade),'formats':dict(bytype),'independent_method_certified':0,'source':'V197 full website ZIP','oracle_verified_count':len(rows),'production_deployed':False}
    (OUT/'V198_GENERATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
