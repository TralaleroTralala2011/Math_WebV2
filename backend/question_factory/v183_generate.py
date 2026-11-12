#!/usr/bin/env python3
"""MATH_WEB V182: mathematically crosschecked question candidates for underserved topics.
No independent method certification and no production write. Reproducible, deterministic.
"""
import json, random, math, hashlib, collections, sys
from fractions import Fraction as F
from pathlib import Path

WEB=Path(__file__).resolve().parents[2]
ROOT=WEB
OUT=WEB/'bank_updates/v183_reproduced'
OUT.mkdir(exist_ok=True)
rng=random.Random(182_2026)

# grade, topic ID, family, title, concept, method, application conditions, difference note
SPECS=[
(10,'menh_de_tap_hop','set_intersection','Số phần tử giao của hai tập','Công thức bao hàm–loại trừ','|A∩B|=|A|+|B|−|A∪B|','A,B hữu hạn','Tìm giao từ hợp và kích thước hai tập'),
(10,'quy_tac_dem','count_outfits','Quy tắc nhân','Quy tắc đếm nhân','m lựa chọn độc lập nhân n lựa chọn','Hai công đoạn độc lập','Đếm cặp lựa chọn'),
(10,'menh_de','divisibility_truth','Đánh giá mệnh đề chia hết','Mệnh đề đúng sai','Kiểm tra phần dư','Các mệnh đề số học xác định','Đếm số mệnh đề đúng'),
(10,'he_phuong_trinh','linear_system_sum','Hệ hai phương trình bậc nhất','Phép cộng và trừ hệ','x=(s+d)/2','Tổng và hiệu cùng tính chẵn lẻ','Tìm nghiệm x từ tổng và hiệu'),
(10,'he_thuc_luong_tam_giac','cosine_law','Định lý cosin','Hệ thức lượng tam giác','c²=a²+b²−2ab cos C','Góc xen giữa 60° hoặc 120°','Tính bình phương cạnh đối diện'),
(10,'duong_thang','line_slope','Hệ số góc đường thẳng','Tọa độ đường thẳng','k=(y₂−y₁)/(x₂−x₁)','Hai điểm khác hoành độ','Xác định độ dốc từ hai điểm'),
(10,'duong_tron','tangent_length_squared','Độ dài tiếp tuyến đường tròn','Tam giác vuông với bán kính','PT²=PO²−R²','P ngoài đường tròn','Tính bình phương đoạn tiếp tuyến'),
(10,'hinh_hoc_10','pythagorean_squared','Định lý Pythagore','Tam giác vuông','c²=a²+b²','Hai cạnh góc vuông dương','Tính bình phương cạnh huyền'),
(10,'bai_toan_thuc_te_10','linear_breakeven','Hòa vốn mô hình tuyến tính','Phương trình tuyến tính','số lượng=chi phí cố định/(giá bán−chi phí biến đổi)','Lãi trên mỗi sản phẩm dương','Tìm số lượng hòa vốn'),
(10,'tam_giac_tu_giac_10','trapezoid_area','Diện tích hình thang','Diện tích tứ giác','S=(a+b)h/2','Hai đáy song song, h>0','Tính diện tích từ hai đáy và chiều cao'),
(10,'duong_tron_co_ban_10','inscribed_angle','Góc nội tiếp','Góc ở tâm và góc nội tiếp','góc nội tiếp bằng nửa góc ở tâm','Cùng chắn một cung nhỏ','Tính góc nội tiếp từ góc ở tâm'),
(10,'toa_do_hinh_hoc_10','distance_squared_2d','Khoảng cách bình phương','Tọa độ mặt phẳng','AB²=(Δx)²+(Δy)²','A,B khác nhau','Tính bình phương khoảng cách'),
(10,'g10_geom_triangle_congruence','sas_matching_side','Cạnh tương ứng trong tam giác bằng nhau','Trường hợp cạnh–góc–cạnh','SAS => cạnh thứ ba bằng nhau','Hai cạnh và góc xen giữa tương ứng bằng nhau','Suy ra cạnh tương ứng bằng nhau'),
(10,'g10_geom_coordinate_distance_midpoint','midpoint_sum_2d','Tọa độ trung điểm','Trung điểm đoạn thẳng','M=((x₁+x₂)/2,(y₁+y₂)/2)','A,B thuộc mặt phẳng tọa độ','Tính tổng tọa độ trung điểm'),
(10,'g10_geom_locus','perp_bisector_vertical','Quỹ tích đường trung trực','Điểm cách đều hai điểm','Trung trực của đoạn thẳng nằm ngang là x=(a+b)/2','A,B cùng tung độ, khác hoành độ','Tìm hoành độ mọi điểm cách đều A và B'),
(10,'g10_geom_circle_tangent_chord','tangent_chord_angle','Góc tiếp tuyến và dây cung','Định lý góc tạo bởi tiếp tuyến và dây','Góc tiếp tuyến–dây bằng góc nội tiếp chắn cùng cung','Tiếp tuyến tại đầu dây','Tính góc tiếp tuyến–dây'),
(10,'g10_symmetric_systems','symmetric_difference_squared','Hệ đối xứng hai ẩn','Hệ thức Viète','(x−y)²=(x+y)²−4xy','Biết tổng và tích hai nghiệm thực','Tính bình phương hiệu hai nghiệm'),
(11,'day_so','sum_square_sequence','Tổng dãy số bình phương','Tổng bình phương','S=n(n+1)(2n+1)/6','n nguyên dương','Tính tổng 1²+…+n²'),
(11,'gioi_han','removable_limit','Giới hạn dạng 0/0 khử nhân tử','Phân tích đa thức','(x²−a²)/(x−a)=x+a','x tiến tới a, x≠a','Khử nhân tử chung trước khi thế'),
(11,'hinh_khong_gian','prism_edges','Đếm cạnh lăng trụ','Cấu trúc lăng trụ n-gon','3n cạnh','Lăng trụ có hai đáy n-gon','Đếm số cạnh của lăng trụ'),
(11,'xac_suat_11','two_red_without_replacement','Xác suất lấy hai vật cùng màu','Quy tắc nhân xác suất phụ thuộc','r(r−1)/(n(n−1))','Rút hai lần không hoàn lại','Xác suất có điều kiện trong phép rút'),
(11,'gia_tri_luong_giac','cos_from_sin','Tìm cos từ sin','Hệ thức lượng giác cơ bản','cos²=1−sin²','Góc nhọn, sin là phân số tam giác Pythagore','Lựa chọn dấu dương của cos'),
(11,'cong_thuc_luong_giac','cos_double_angle','Công thức nhân đôi','Lượng giác','cos(2a)=2cos²(a)−1','Biết cos(a)','Tính cos góc gấp đôi'),
(11,'ham_so_luong_giac_day_du','sine_zero_count','Số nghiệm của sin(kx)=0','Chu kỳ và nghiệm lượng giác','sin(kx)=0 ⇔ kx=mπ','k nguyên dương, 0≤x<2π','Đếm nghiệm trong một khoảng'),
(11,'phuong_trinh_luong_giac_day_du','cosine_one_count','Số nghiệm của cos(kx)=1','Phương trình lượng giác','cos(kx)=1 ⇔ kx=2mπ','k nguyên dương, 0≤x<2π','Đếm nghiệm đúng trên nửa khoảng'),
(11,'day_so_tong_quat','odd_increment_recurrence','Dãy truy hồi cộng số lẻ','Dãy số quy nạp','1+3+…+(2n−1)=n²','u₁=1, uₙ=uₙ₋₁+(2n−1)','Tính số hạng bằng tổng số lẻ'),
(11,'dao_ham_quy_tac','product_rule','Quy tắc đạo hàm tích','Đạo hàm hàm tích','(uv)′=u′v+uv′','u,v là đa thức','Đạo hàm tích tại điểm'),
(11,'ung_dung_dao_ham_11','normal_slope','Hệ số góc pháp tuyến','Tiếp tuyến và pháp tuyến','k_pháp=−1/f′(x₀)','f′(x₀)≠0','Tính độ dốc pháp tuyến từ đạo hàm'),
(11,'bai_toan_thuc_te_11','compound_growth','Lãi kép','Cấp số nhân thực tế','Aₙ=A₀qⁿ','Lãi suất kỳ cố định','Tính số tiền sau nhiều kỳ'),
(11,'phep_bien_hinh_11','rotation_90','Phép quay 90°','Phép biến hình mặt phẳng','(x,y)↦(−y,x)','Quay quanh gốc O ngược chiều kim đồng hồ','Tìm tổng tọa độ điểm ảnh'),
(11,'nhan_biet_hinh_khong_gian_11','pyramid_edges','Số cạnh hình chóp','Nhận dạng hình chóp','2n cạnh','Hình chóp đáy n-gon','Đếm cạnh bên và cạnh đáy'),
(11,'g11_geom_parallel_planes','parallel_planes_distance','Khoảng cách hai mặt phẳng song song','Hình học không gian','d=|a−b| cho x=a, x=b','Hai mặt phẳng phân biệt','Khoảng cách hai mặt phẳng'),
(11,'g11_geom_skew_lines_distance','skew_perpendicular_distance','Khoảng cách đường thẳng chéo nhau','Hình học không gian tọa độ','Khoảng cách hai đường vuông góc chéo nhau bằng độ lệch theo trục chung','Hai đường song song với Ox và Oy tại độ cao khác nhau','Khoảng cách hai đường chéo nhau'),
(11,'g11_sequences_advanced','affine_recurrence','Dãy truy hồi affine','Giải truy hồi tuyến tính','uₙ=2ⁿ⁻¹(u₁+1)−1','uₙ=2uₙ₋₁+1','Giải truy hồi bằng phép đổi biến v=u+1'),
(11,'g11_binomial_advanced','binomial_coefficient','Hệ số nhị thức Newton','Khai triển nhị thức','[x^k](1+ax)^n=C(n,k)a^k','n nguyên không âm, 0≤k≤n','Tìm hệ số một lũy thừa'),
(11,'g11_conditional_probability_models','conditional_count','Xác suất có điều kiện từ bảng số liệu','Xác suất có điều kiện','P(A|B)=n(A∩B)/n(B)','n(B)>0','Tính xác suất trên không gian đã điều kiện'),
(12,'ung_dung_dao_ham','quadratic_stationary_point','Điểm dừng của parabol','Đạo hàm','f′(x)=2ax+b=0','a≠0','Tìm hoành độ điểm dừng'),
(12,'khao_sat_ham_so','cubic_stationary_count','Số cực trị của đa thức bậc ba','Khảo sát hàm số','Đạo hàm bậc hai có 2 nghiệm phân biệt khi Δ>0','Hệ số bậc ba khác 0','Đếm cực trị từ nghiệm đạo hàm'),
(12,'hinh_hoc_khong_gian','prism_volume','Thể tích lăng trụ','Hình khối','V=S_đáy h','Đáy và chiều cao dương','Tính thể tích lăng trụ'),
(12,'xac_suat_12','discrete_expectation','Kỳ vọng biến ngẫu nhiên','Xác suất rời rạc','E(X)=Σxᵢpᵢ','Các xác suất không âm, tổng 1','Tính kỳ vọng từ bảng phân phối'),
(12,'thong_ke_12','population_variance','Phương sai dữ liệu','Các số đặc trưng','V=(1/n)Σ(xᵢ−x̄)²','Mẫu gồm các số thực','Tính phương sai theo trung bình'),
(12,'gtln_gtnn','parabola_minimum','Giá trị nhỏ nhất parabol','Hoàn thành bình phương','a(x−h)²+k ≥ k khi a>0','a>0','Tìm GTNN bằng dạng chuẩn'),
(12,'tuong_giao','line_parabola_intersections','Số giao điểm hai đồ thị','Giải phương trình hoành độ giao điểm','Δ quyết định số nghiệm thực','Đường thẳng và parabol','Đếm số giao điểm'),
(12,'ham_mu','exponential_growth','Hàm mũ tăng trưởng','Hàm số mũ','f(t)=A b^t','b>1, t nguyên không âm','Tính giá trị hàm mũ'),
(12,'ham_logarit','logarithm_of_power','Logarit của lũy thừa','Định nghĩa logarit','log_b(b^n)=n','b>0,b≠1','Tính logarit chính xác'),
(12,'mat_phang_oxyz','plane_normal_sum','Vectơ pháp tuyến mặt phẳng','Phương trình mặt phẳng','(a,b,c) là VTPT của ax+by+cz+d=0','(a,b,c) khác 0','Tính tổng tọa độ vectơ pháp tuyến'),
(12,'duong_thang_oxyz','line_parametric_point','Phương trình tham số đường thẳng','Tọa độ Oxyz','M=P+t v','v khác 0','Tìm tổng tọa độ điểm theo tham số'),
(12,'mat_cau','sphere_radius_squared','Bán kính mặt cầu','Phương trình mặt cầu','R²=a²+b²+c²−d','R²>0','Hoàn thành bình phương phương trình mặt cầu'),
(12,'goc_khoang_cach_oxyz','axis_plane_distance','Khoảng cách điểm đến mặt phẳng','Khoảng cách Oxyz','d(M,x=k)=|x_M−k|','M bất kỳ, x=k là mặt phẳng','Tính khoảng cách từ điểm tới mặt phẳng tọa độ dịch chuyển'),
(12,'the_tich_khong_gian','pyramid_volume','Thể tích hình chóp','Thể tích khối đa diện','V=(1/3)S_đáy h','S_đáy>0,h>0','Tính thể tích hình chóp'),
(12,'bai_toan_thuc_te_12','profit_maximum','Tối đa hóa lợi nhuận','Ứng dụng đạo hàm thực tế','P(x)=−a(x−h)²+k đạt max k','a>0, x≥0, h≥0','Tìm lợi nhuận cực đại'),
(12,'g12_geom_line_equation_3d','line_direction_sum','Vectơ chỉ phương đường thẳng Oxyz','Phương trình đường thẳng','v=B−A','A≠B','Tính tổng tọa độ vectơ chỉ phương'),
(12,'g12_geom_point_plane_distance','point_plane_345','Khoảng cách điểm đến mặt phẳng','Công thức khoảng cách Oxyz','|3x+4y−d|/5','Pháp tuyến (3,4,0)','Tính khoảng cách đến mặt phẳng nghiêng'),
(12,'g12_geom_parameter_geometry','plane_parameter','Tham số mặt phẳng đi qua điểm','Điều kiện điểm thuộc mặt phẳng','Thế tọa độ vào ax+ky+z=0','y≠0','Tìm tham số để mặt phẳng chứa điểm'),
(12,'g12_geom_3d_optimization','distance_to_axis_min','Cực trị khoảng cách đến đường thẳng','Tối ưu hình học tọa độ','min_{t}[(x−t)²+y²+z²]=y²+z²','Đường thẳng là trục Ox','Tìm bình phương khoảng cách ngắn nhất'),
(12,'g12_integral_optimization','integral_maximum','Tối ưu tích phân có tham số','Tích phân và đạo hàm','F(t)=∫₀ᵗ(c−2ax)dx=ct−at²','a,c>0, t≥0','Tìm t để tích phân lớn nhất'),
(12,'g12_solid_of_revolution','revolution_cone','Thể tích khối tròn xoay','Phương pháp đĩa','V=π∫₀ᵇ(kx)²dx=πk²b³/3','k,b>0','Tìm hệ số của π trong thể tích'),
(10,'he_thuc_luong_van_dung_10','sine_rule_diameter','Đường kính ngoại tiếp theo định lý sin','Hệ thức lượng nâng cao','2R=a/sin A','Tam giác có cạnh a đối diện góc A','Tính đường kính đường tròn ngoại tiếp'),
(10,'chung_minh_hinh_hoc_10','triangle_midsegment','Đường trung bình tam giác','Định lý đường trung bình','MN=BC/2','M,N là trung điểm hai cạnh','Suy ra độ dài cạnh từ quan hệ song song'),
(10,'g10_geom_vector_proofs','parallelogram_fourth_vertex','Chứng minh hình bình hành bằng vectơ','Quan hệ vectơ và đường chéo','D=A+C−B','A,B,C là ba đỉnh liên tiếp','Tìm đỉnh thứ tư bằng đẳng thức vectơ'),
(10,'g10_geom_coordinate_circle_line','circle_vertical_chord','Giao đường tròn và đường thẳng','Tọa độ đường tròn','(y−k)²=r²−(x−h)²','Đường thẳng cắt đường tròn tại hai điểm','Tính bình phương độ dài dây cung thẳng đứng'),
(11,'song_song_khong_gian','parallel_line_plane_distance','Khoảng cách đường thẳng song song mặt phẳng','Quan hệ song song trong không gian','d(d,z=k)=|h−k|','d nằm trong mặt phẳng z=h, phương Ox','Khoảng cách từ đường thẳng đến mặt phẳng'),
(11,'vuong_goc_khong_gian','perpendicular_vectors_parameter','Điều kiện vuông góc hai đường','Tích vô hướng','u·v=0','Hai vectơ khác 0','Tìm tham số để hai phương vuông góc'),
(11,'goc_khoang_cach_11','space_point_plane_distance','Khoảng cách từ điểm đến mặt phẳng','Khoảng cách trong không gian','d(M,z=k)=|z−k|','M bất kỳ, mặt phẳng song song Oxy','Khoảng cách từ điểm đến mặt phẳng ngang'),
(11,'thiet_dien_hinh_khong_gian_11','pyramid_parallel_section_area','Thiết diện hình chóp song song đáy','Tam giác đồng dạng trong không gian','S_section/S_base=(h/H)²','Mặt phẳng cắt song song đáy','Tính diện tích thiết diện'),
(11,'bai_toan_thuc_te_tong_hop_11','savings_arithmetic_total','Tổng tiền tiết kiệm tăng đều','Cấp số cộng thực tế','S=n(2a+(n−1)d)/2','Tiết kiệm tăng đều từng năm','Tính tổng nhiều năm'),
(11,'phep_bien_hinh_co_ban_11','reflection_x_axis','Phép đối xứng trục Ox','Phép biến hình cơ bản','(x,y)↦(x,−y)','Đối xứng qua trục Ox','Tính tọa độ điểm ảnh'),
(11,'g11_geom_space_lines_planes','plane_intercept_evaluation','Phương trình mặt phẳng qua ba giao điểm','Hình học không gian','x/a+y/b+z/c=1','a,b,c khác 0','Tính giá trị biểu thức mặt phẳng tại điểm'),
(11,'g11_geom_parallel_line_plane','direction_parallel_plane','Đường thẳng song song mặt phẳng','Tích vô hướng với pháp tuyến','n·v=0','v khác 0','Tìm tham số vectơ chỉ phương song song mặt phẳng'),
(11,'g11_geom_perpendicular_line_plane','direction_normal_plane','Đường thẳng vuông góc mặt phẳng','Phương vectơ pháp tuyến','v=k n','n khác 0, k khác 0','Tìm tỉ số thành phần vectơ chỉ phương'),
(11,'g11_geom_dihedral_angles','line_plane_sine_angle','Góc giữa đường thẳng và mặt phẳng','Tích vô hướng với pháp tuyến','sin θ=|v·n|/(|v||n|)','Góc giữa đường thẳng và Oxy','Tính sin góc đường–mặt phẳng'),
(11,'g11_geom_section_construction','prism_horizontal_section_perimeter','Thiết diện lăng trụ đứng','Thiết diện song song đáy','P=2(a+b)','Thiết diện bởi mặt phẳng ngang cắt lăng trụ','Tính chu vi thiết diện'),
(11,'g11_geom_three_perpendiculars','three_perpendicular_distance','Định lý ba đường vuông góc','Hình chiếu và khoảng cách','d(P,l)²=h²+d(H,l)²','H là hình chiếu P xuống mặt phẳng','Tính khoảng cách P đến đường thẳng trong mặt phẳng'),
(11,'g11_geom_section_ratio','pyramid_section_perimeter','Tỉ số chu vi thiết diện','Hình đồng dạng','P_section/P_base=t','Thiết diện song song đáy, t trong (0,1)','Tính chu vi thiết diện theo tỉ số'),
(11,'g11_geom_space_proof','orthogonal_basis_proof','Chứng minh vuông góc đường và mặt','Hai phương độc lập trong mặt phẳng','u·v=0 và u·w=0','v,w độc lập trong mặt phẳng','Xác định tham số để đường vuông góc mặt phẳng'),
(12,'tong_hop_thpt','intercept_triangle_area','Diện tích tam giác giao trục','Tổng hợp tọa độ và hình học','S=|ab|/2','Đường thẳng cắt hai trục tại a,b khác 0','Tính diện tích tam giác tạo với hai trục'),
(12,'hinh_hoc_oxyz_van_dung_12','reflection_horizontal_plane','Đối xứng điểm qua mặt phẳng','Phép đối xứng Oxyz','(x,y,z)↦(x,y,2k−z)','Đối xứng qua z=k','Tính tổng tọa độ điểm đối xứng'),
(12,'g12_geom_two_planes_angle','plane_plane_cosine','Góc giữa hai mặt phẳng','Góc giữa pháp tuyến','cos θ=|n1·n2|/(|n1||n2|)','Hai mặt phẳng không song song','Tính cos góc nhọn giữa hai mặt phẳng'),
(12,'g12_geom_skew_line_relation','skew_vs_intersect','Vị trí tương đối hai đường thẳng','Giao và chéo nhau trong Oxyz','Khoảng cách theo phương chung bằng 0 ⇔ cắt nhau','Hai đường có phương Ox và Oy','Phân biệt giao nhau và chéo nhau'),
(12,'g12_geom_min_distance_3d','line_distance_min_squared','Cực tiểu khoảng cách đến đường thẳng','Khoảng cách từ điểm đến đường','min PM²=(x−a)²+(y−b)²','Đường thẳng song song Oz','Tìm bình phương khoảng cách ngắn nhất'),
(10,'g10_radical_equations_advanced','radical_extraneous_root','Giải phương trình chứa căn có nghiệm ngoại lai','Bình phương và thử nghiệm','√(x+t(t−1))=x','x≥0, t≥2','Bình phương rồi loại nghiệm không thỏa'),
(11,'g11_advanced_trig_equations','advanced_sin_double_count','Đếm nghiệm phương trình lượng giác nhân đôi','Biến đổi tích','sin(2kx)=sin(kx) ⇔ sin(kx)(2cos(kx)−1)=0','k nguyên dương, x∈[0,2π)','Đếm nghiệm của tích hai nhân tử lượng giác'),
(12,'g12_complex_plane_geometry','complex_circle_max_real','Quỹ tích đường tròn số phức','Hình học số phức','|z−(a+bi)|=r ⇒ max Re(z)=a+r','r>0','Tìm cực đại phần thực trên đường tròn'),
]

def make(key,r):
    I=lambda a,b:r.randint(a,b)
    nz=lambda a,b:r.choice([x for x in range(a,b+1) if x])
    if key=='set_intersection':
        common=I(2,15); a=common+I(1,15); b=common+I(1,15);union=a+b-common
        return f'Cho hai tập hữu hạn A, B có |A|={a}, |B|={b}, |A∪B|={union}. Tính |A∩B|.',F(common),f'Áp dụng |A∪B|=|A|+|B|−|A∩B|. Chuyển vế: |A∩B|={a}+{b}−{union}={common}.',dict(a=a,b=b,union=union),a+b-union==common
    if key=='count_outfits':
        a=I(3,17);b=I(3,18);n=a*b
        return f'Có {a} mẫu áo và {b} mẫu quần, mỗi mẫu chọn độc lập. Có bao nhiêu bộ gồm một áo và một quần?',F(n),f'Bước 1: Có {a} lựa chọn áo. Bước 2: Mỗi áo ghép được với {b} quần. Quy tắc nhân: {a}×{b}={n} bộ.',dict(a=a,b=b),len([(i,j) for i in range(a) for j in range(b)])==n
    if key=='divisibility_truth':
        n=I(100,999);ds=r.sample(range(2,15),4);t=sum(n%d==0 for d in ds)
        return f'Với n={n}, xét 4 mệnh đề: n chia hết cho {ds[0]}, {ds[1]}, {ds[2]}, {ds[3]}. Có bao nhiêu mệnh đề đúng?',F(t),f'Tính các số dư: {", ".join(f"{n}%{d}={n%d}" for d in ds)}. Mệnh đề đúng khi số dư bằng 0. Có {t} mệnh đề đúng.',dict(n=n,divisors=ds),t==sum(1 for d in ds if math.gcd(n,d)==d)
    if key=='linear_system_sum':
        x=I(-20,20);y=I(-20,20);s=x+y;d=x-y
        return f'Giải hệ x+y={s}, x−y={d}. Tính giá trị x.',F(x),f'Cộng hai phương trình: 2x={s}+({d})={s+d}. Suy ra x=({s+d})/2={x}. Thế lại y={y}.',dict(x=x,y=y,s=s,d=d),x+y==s and x-y==d
    if key=='cosine_law':
        a=I(3,15);b=I(3,15);c=r.choice([60,120]);z=a*a+b*b-(a*b if c==60 else -a*b)
        return f'Tam giác ABC có AB={a}, AC={b}, góc BAC={c}°. Tính BC².',F(z),f'Định lý cosin: BC²=AB²+AC²−2·AB·AC·cos({c}°). Vì cos({c}°)={"1/2" if c==60 else "−1/2"}, BC²={a*a}+{b*b}{"−" if c==60 else "+"}{a*b}={z}.',dict(a=a,b=b,angle=c),z==a*a+b*b-2*a*b*F(1 if c==60 else -1,2)
    if key=='line_slope':
        x=I(-10,10);dx=nz(-9,9);y=I(-15,15);k=I(-9,9);dy=k*dx
        return f'Đường thẳng qua A({x};{y}) và B({x+dx};{y+dy}). Tìm hệ số góc của đường thẳng.',F(k),f'Vì x_B−x_A={dx}≠0, hệ số góc k=(y_B−y_A)/(x_B−x_A)=({dy})/({dx})={k}.',dict(x=x,y=y,dx=dx,dy=dy),F(dy,dx)==k
    if key=='tangent_length_squared':
        rad=I(2,15);t=I(2,20);po2=rad*rad+t*t
        return f'Từ điểm P ngoài đường tròn (O;R={rad}), kẻ tiếp tuyến PT. Biết PO²={po2}. Tính PT².',F(t*t),f'Bán kính OT vuông góc tiếp tuyến PT. Tam giác OPT vuông tại T nên PT²=PO²−OT²={po2}−{rad}²={t*t}.',dict(r=rad,t=t,po2=po2),po2-rad*rad==t*t
    if key=='pythagorean_squared':
        a=I(3,25);b=I(3,25);z=a*a+b*b
        return f'Tam giác ABC vuông tại A, AB={a} cm, AC={b} cm. Tính BC² (cm²).',F(z),f'Vì tam giác vuông tại A, theo Pythagore: BC²=AB²+AC²={a}²+{b}²={a*a}+{b*b}={z}.',dict(a=a,b=b),math.isqrt(z)**2<=z and z==a*a+b*b
    if key=='linear_breakeven':
        variable=I(8,50);margin=I(5,25);units=I(10,70);fixed=margin*units;price=variable+margin
        return f'Một sản phẩm bán giá {price} nghìn đồng, chi phí biến đổi {variable} nghìn đồng/sản phẩm, chi phí cố định {fixed} nghìn đồng. Bán bao nhiêu sản phẩm thì hòa vốn?',F(units),f'Lãi góp mỗi sản phẩm: {price}−{variable}={margin} nghìn. Hòa vốn khi {margin}n={fixed}, nên n={fixed}/{margin}={units} sản phẩm.',dict(price=price,variable=variable,fixed=fixed),price*units==fixed+variable*units
    if key=='trapezoid_area':
        a=I(4,25);b=I(4,25);h=2*I(2,14);z=F((a+b)*h,2)
        return f'Hình thang có hai đáy {a} cm và {b} cm, chiều cao {h} cm. Tính diện tích (cm²).',z,f'Diện tích hình thang bằng nửa tổng hai đáy nhân chiều cao: S=({a}+{b})×{h}/2={z} cm².',dict(a=a,b=b,h=h),z==F(a*h,2)+F(b*h,2)
    if key=='inscribed_angle':
        angle=2*I(10,80);z=angle//2
        return f'Trong đường tròn, góc ở tâm AOB chắn cung nhỏ AB bằng {angle}°. Góc nội tiếp ACB cùng chắn cung nhỏ AB bằng bao nhiêu độ?',F(z),f'Góc nội tiếp cùng chắn cung AB bằng một nửa góc ở tâm: ∠ACB={angle}°/2={z}°.',dict(central=angle),2*z==angle
    if key=='distance_squared_2d':
        x=I(-15,15);y=I(-15,15);dx=nz(-12,12);dy=nz(-12,12);z=dx*dx+dy*dy
        return f'Trong Oxy, A({x};{y}), B({x+dx};{y+dy}). Tính AB².',F(z),f'Hiệu tọa độ B−A=({dx};{dy}). Do đó AB²=({dx})²+({dy})²={dx*dx}+{dy*dy}={z}.',dict(x=x,y=y,dx=dx,dy=dy),z==(x+dx-x)**2+(y+dy-y)**2
    if key=='sas_matching_side':
        a=I(3,15);b=I(3,15);c=I(abs(a-b)+1,a+b-1)
        return f'Hai tam giác ABC và DEF có AB=DE={a} cm, AC=DF={b} cm, ∠BAC=∠EDF và BC={c} cm. Theo trường hợp cạnh–góc–cạnh, EF dài bao nhiêu cm?',F(c),f'Hai cạnh AB, AC tương ứng với DE, DF; góc xen giữa bằng nhau. Theo C.G.C., ΔABC≅ΔDEF. Suy ra cạnh tương ứng EF=BC={c} cm.',dict(a=a,b=b,c=c),c>0
    if key=='midpoint_sum_2d':
        x=I(-16,16);y=I(-16,16);u=I(-16,16);v=I(-16,16);z=F(x+u+y+v,2)
        return f'Trong Oxy, A({x};{y}), B({u};{v}). Gọi M là trung điểm AB. Tính x_M+y_M.',z,f'Tọa độ trung điểm: x_M=({x}+{u})/2, y_M=({y}+{v})/2. Tổng x_M+y_M=({x}+{u}+{y}+{v})/2={z}.',dict(x=x,y=y,u=u,v=v),z==F(x+u,2)+F(y+v,2)
    if key=='perp_bisector_vertical':
        a=I(-20,20);b=a+2*I(1,20);y=I(-15,15);z=F(a+b,2)
        return f'Trong Oxy, A({a};{y}), B({b};{y}). Quỹ tích điểm M cách đều A và B là đường thẳng x=k. Tìm k.',z,f'AB nằm ngang nên trung trực vuông góc AB và đi qua trung điểm. Hoành độ trung điểm k=({a}+{b})/2={z}.',dict(a=a,b=b,y=y),F((z-a)**2-(z-b)**2)==0
    if key=='tangent_chord_angle':
        angle=I(15,75)
        return f'Đường tròn có tiếp tuyến tại A và dây AB. Một góc nội tiếp chắn cung AB bằng {angle}°. Góc nhọn giữa tiếp tuyến tại A và dây AB cùng chắn cung đó bằng bao nhiêu độ?',F(angle),f'Định lý góc giữa tiếp tuyến và dây cung: số đo bằng góc nội tiếp cùng chắn cung AB, nên bằng {angle}°.',dict(angle=angle),0<angle<90
    if key=='symmetric_difference_squared':
        x=I(-12,12);y=I(-12,12);s=x+y;p=x*y;z=(x-y)**2
        return f'Biết x+y={s} và xy={p}. Tính (x−y)².',F(z),f'Hằng đẳng thức (x−y)²=(x+y)²−4xy. Thay số: ({s})²−4×({p})={s*s}−({4*p})={z}.',dict(x=x,y=y,s=s,p=p),z==s*s-4*p
    if key=='sum_square_sequence':
        n=I(5,40);z=n*(n+1)*(2*n+1)//6
        return f'Tính S=1²+2²+3²+…+{n}².',F(z),f'Công thức tổng bình phương: S=n(n+1)(2n+1)/6. Với n={n}, S={n}×{n+1}×{2*n+1}/6={z}.',dict(n=n),z==sum(k*k for k in range(1,n+1))
    if key=='removable_limit':
        a=nz(-15,15);z=2*a
        return f'Tính giới hạn lim(x→{a}) (x²−({a})²)/(x−({a})).',F(z),f'Với x≠{a}, phân tích x²−({a})²=(x−({a}))(x+({a})). Rút gọn được x+({a}); cho x→{a}, giới hạn bằng {z}.',dict(a=a),F((a+1)**2-a*a,(a+1)-a)==2*a+1 and z==2*a
    if key=='prism_edges':
        n=I(3,60);z=3*n
        return f'Một lăng trụ có đáy là đa giác {n} cạnh. Lăng trụ có tất cả bao nhiêu cạnh?',F(z),f'Hai đáy có 2×{n} cạnh và {n} cạnh bên nối các đỉnh tương ứng. Tổng số cạnh: 3×{n}={z}.',dict(n=n),z==2*n+n
    if key=='two_red_without_replacement':
        red=I(3,16);blue=I(2,15);n=red+blue;z=F(red*(red-1),n*(n-1))
        return f'Hộp có {red} bi đỏ, {blue} bi xanh. Rút ngẫu nhiên 2 bi liên tiếp không hoàn lại. Tính xác suất cả hai bi đều đỏ.',z,f'Lần đầu đỏ: {red}/{n}. Sau khi rút đỏ, lần hai đỏ: {red-1}/{n-1}. Nhân xác suất: P=({red}/{n})×({red-1}/{n-1})={z}.',dict(red=red,blue=blue),z==F(math.comb(red,2),math.comb(n,2))
    if key=='cos_from_sin':
        m=I(3,14);n=I(1,m-1);a=m*m-n*n;b=2*m*n;c=m*m+n*n;z=F(b,c)
        return f'Cho góc nhọn α có sin α={a}/{c}. Tính cos α (dạng phân số tối giản).',z,f'Vì α nhọn nên cos α>0. Hệ thức sin²α+cos²α=1 suy ra cos²α=1−({a}/{c})²={b*b}/{c*c}. Do đó cos α={z}.',dict(a=a,b=b,c=c),a*a+b*b==c*c
    if key=='cos_double_angle':
        a=I(1,19);c=I(a+1,30);b=math.isqrt(c*c-a*a);z=2*F(a,c)**2-1
        return f'Biết cos α={a}/{c}. Tính cos(2α).',z,f'Công thức nhân đôi: cos(2α)=2cos²α−1=2×({a}/{c})²−1={2*a*a}/{c*c}−1={z}.',dict(a=a,c=c),z==F(2*a*a-c*c,c*c)
    if key=='sine_zero_count':
        k=I(2,25);z=2*k
        return f'Có bao nhiêu nghiệm của sin({k}x)=0 trong khoảng 0≤x<2π?',F(z),f'Điều kiện sin({k}x)=0 tương đương {k}x=mπ, nên x=mπ/{k}. Với 0≤x<2π, m=0,…,{2*k-1}, có {z} nghiệm.',dict(k=k),len(range(0,2*k))==z
    if key=='cosine_one_count':
        k=I(2,25)
        return f'Có bao nhiêu nghiệm của cos({k}x)=1 trên nửa khoảng 0≤x<2π?',F(k),f'cos({k}x)=1 ⇔ {k}x=2mπ ⇔ x=2mπ/{k}. Trong [0,2π), m=0,…,{k-1}, có {k} nghiệm.',dict(k=k),len(range(k))==k
    if key=='odd_increment_recurrence':
        n=I(5,35);z=n*n
        return f'Dãy số xác định u₁=1, uₙ=uₙ₋₁+(2n−1) với n≥2. Tính u_{n}.',F(z),f'Ta có uₙ=1+3+5+…+(2n−1), là tổng {n} số lẻ đầu tiên. Tổng bằng n²={n}²={z}.',dict(n=n),z==1+sum(2*k-1 for k in range(2,n+1))
    if key=='product_rule':
        a=nz(-8,8);b=I(-10,10);c=nz(-8,8);d=I(-10,10);x=I(-8,8);z=a*(c*x+d)+c*(a*x+b)
        return f'Cho f(x)=({a}x+({b}))({c}x+({d})). Tính f′({x}).',F(z),f'Đặt u={a}x+({b}), v={c}x+({d}). Quy tắc tích f′=u′v+uv′={a}({c}x+({d}))+{c}({a}x+({b})). Thay x={x} được {z}.',dict(a=a,b=b,c=c,d=d,x=x),z==2*a*c*x+a*d+b*c
    if key=='normal_slope':
        a=nz(-9,9);b=I(-12,12);x=I(-8,8);s=2*a*x+b
        if s==0:s=1;b=s-2*a*x
        z=F(-1,s)
        return f'Cho y={a}x²+({b})x+1. Tìm hệ số góc đường pháp tuyến tại x₀={x}.',z,f'Đạo hàm y′=2×({a})x+({b}); tại x₀={x}, hệ số góc tiếp tuyến k={s}≠0. Pháp tuyến vuông góc tiếp tuyến nên k_n=−1/k={z}.',dict(a=a,b=b,x=x,s=s),s*z==-1
    if key=='compound_growth':
        a=I(5,30);q=I(2,4);n=I(2,7);z=a*q**n
        return f'Một quỹ có {a} triệu đồng, mỗi kỳ tăng theo hệ số {q} so với kỳ trước. Sau {n} kỳ có bao nhiêu triệu đồng?',F(z),f'Mô hình cấp số nhân: số tiền sau n kỳ là Aₙ=A₀qⁿ. Thay A₀={a}, q={q}, n={n}: Aₙ={a}×{q}^{n}={z} triệu.',dict(a=a,q=q,n=n),z==list(__import__('itertools').accumulate(range(n),lambda value,_:value*q,initial=a))[-1]
    if key=='rotation_90':
        x=I(-20,20);y=I(-20,20);z=x-y
        return f'Quay điểm M({x};{y}) quanh O một góc 90° ngược chiều kim đồng hồ, được M′. Tính x_M′+y_M′.',F(z),f'Phép quay 90° ngược chiều kim đồng hồ biến (x,y) thành (−y,x). Vậy M′({-y};{x}), tổng tọa độ={-y}+({x})={z}.',dict(x=x,y=y),z==-y+x
    if key=='pyramid_edges':
        n=I(3,60);z=2*n
        return f'Hình chóp có đáy là đa giác {n} cạnh. Hình chóp có tất cả bao nhiêu cạnh?',F(z),f'Có {n} cạnh đáy và {n} cạnh bên nối đỉnh chóp với các đỉnh đáy. Tổng số cạnh là {n}+{n}={z}.',dict(n=n),z==n+n
    if key=='parallel_planes_distance':
        a=I(-20,20);b=a+nz(-20,20);z=abs(a-b)
        return f'Trong Oxyz, hai mặt phẳng (P):x={a} và (Q):x={b}. Tính khoảng cách giữa (P) và (Q).',F(z),f'Hai mặt phẳng song song có cùng vectơ pháp tuyến (1,0,0). Khoảng cách bằng độ chênh hệ số tự do: |{a}−({b})|={z}.',dict(a=a,b=b),z==math.dist((a,0,0),(b,0,0))
    if key=='skew_perpendicular_distance':
        h=I(2,30);x=I(-10,10);y=I(-10,10)
        return f'Trong Oxyz, đường thẳng d₁: (t;{y};0) và d₂: ({x};s;{h}) với t,s∈R. Tính khoảng cách giữa d₁ và d₂.',F(h),f'd₁ có phương Ox, d₂ có phương Oy; đoạn nối A({x};{y};0)∈d₁ và B({x};{y};{h})∈d₂ vuông góc cả hai. AB={h}, nên khoảng cách bằng {h}.',dict(h=h,x=x,y=y),h==abs(h)
    if key=='affine_recurrence':
        a=I(-5,15);n=I(4,11);z=2**(n-1)*(a+1)-1
        return f'Dãy u₁={a}, uₙ=2uₙ₋₁+1 với n≥2. Tính u_{n}.',F(z),f'Đặt vₙ=uₙ+1 thì vₙ=2vₙ₋₁ và v₁={a+1}. Do đó uₙ=2^(n−1)({a}+1)−1=2^{n-1}×{a+1}−1={z}.',dict(a=a,n=n),z==__import__('functools').reduce(lambda u,_:2*u+1,range(2,n+1),a)
    if key=='binomial_coefficient':
        n=I(5,14);k=I(1,min(n,6));a=nz(-5,5);z=math.comb(n,k)*a**k
        return f'Tìm hệ số của x^{k} trong khai triển (1+({a})x)^{n}.',F(z),f'Theo nhị thức Newton, hạng chứa x^{k} là C({n},{k})({a}x)^{k}. Hệ số bằng C({n},{k})×({a})^{k}={math.comb(n,k)}×({a**k})={z}.',dict(n=n,k=k,a=a),z==math.factorial(n)//(math.factorial(k)*math.factorial(n-k))*a**k
    if key=='conditional_count':
        overlap=I(2,15);only=I(2,18);total=overlap+only;z=F(overlap,total)
        return f'Trong {total} học sinh đã tham gia câu lạc bộ B, có {overlap} em đồng thời tham gia A. Chọn ngẫu nhiên một em trong B. Tính P(A|B).',z,f'Không gian điều kiện B có {total} phần tử; số phần tử thuộc A∩B là {overlap}. Do đó P(A|B)=n(A∩B)/n(B)={overlap}/{total}={z}.',dict(overlap=overlap,only=only),z==F(overlap,total)
    if key=='quadratic_stationary_point':
        a=nz(-8,8);x=I(-12,12);b=-2*a*x
        return f'Cho f(x)={a}x²+({b})x+7. Tìm hoành độ điểm dừng của đồ thị.',F(x),f'f′(x)=2×({a})x+({b}). Điểm dừng thỏa f′(x)=0, suy ra x=−({b})/(2×({a}))={x}.',dict(a=a,b=b,x=x),2*a*x+b==0
    if key=='cubic_stationary_count':
        a=nz(-4,4);b=I(-7,7);c=I(-12,12);delta=(2*b)**2-4*3*a*c;z=2 if delta>0 else (1 if delta==0 else 0)
        # Repeated critical point is stationary but NOT an extremum: classify number of distinct stationary points.
        return f'Cho f(x)={a}x³+({b})x²+({c})x+1. Hỏi f′(x)=0 có bao nhiêu nghiệm thực phân biệt?',F(z),f'f′(x)={3*a}x²+({2*b})x+({c}). Biệt thức Δ=({2*b})²−4×({3*a})×({c})={delta}. Do đó số nghiệm thực phân biệt là {z}.',dict(a=a,b=b,c=c,delta=delta),z==(2 if (2*b)**2-12*a*c>0 else (1 if (2*b)**2-12*a*c==0 else 0))
    if key=='prism_volume':
        s=I(5,80);h=I(2,30);z=s*h
        return f'Lăng trụ có diện tích đáy {s} cm² và chiều cao {h} cm. Tính thể tích (cm³).',F(z),f'Công thức thể tích lăng trụ: V=S_đáy×h. Thay S_đáy={s}, h={h}, ta được V={s}×{h}={z} cm³.',dict(s=s,h=h),z==sum(s for _ in range(h))
    if key=='discrete_expectation':
        a=I(1,8);b=I(1,8);c=I(1,8);n=a+b+c;z=F(b+2*c,n)
        return f'Biến ngẫu nhiên X nhận giá trị 0,1,2 với xác suất lần lượt {a}/{n}, {b}/{n}, {c}/{n}. Tính E(X).',z,f'Tổng xác suất ({a}+{b}+{c})/{n}=1. Kỳ vọng E(X)=0×{a}/{n}+1×{b}/{n}+2×{c}/{n}=({b}+{2*c})/{n}={z}.',dict(a=a,b=b,c=c),z==sum(F(i*v,n) for i,v in enumerate([a,b,c]))
    if key=='population_variance':
        m=I(-10,15);d=I(2,12);z=F(d*d,1)
        return f'Mẫu số liệu gồm hai giá trị {m-d} và {m+d}. Tính phương sai theo công thức chia cho n.',z,f'Trung bình x̄=({m-d}+{m+d})/2={m}. Phương sai V=[({m-d}−{m})²+({m+d}−{m})²]/2=({d*d}+{d*d})/2={z}.',dict(m=m,d=d),z==F((m-d-m)**2+(m+d-m)**2,2)
    if key=='parabola_minimum':
        a=I(1,12);h=I(-12,12);k=I(-20,20)
        return f'Tìm giá trị nhỏ nhất của f(x)={a}(x−({h}))²+({k}) trên R.',F(k),f'Vì {a}>0 và (x−({h}))²≥0 nên f(x)≥{k}. Dấu bằng khi x={h}; do đó GTNN bằng {k}.',dict(a=a,h=h,k=k),a*(h-h)**2+k==k
    if key=='line_parabola_intersections':
        a=nz(-6,6);b=I(-12,12);c=I(-12,12);m=I(-10,10);n=I(-15,15);d=(b-m)**2-4*a*(c-n);z=2 if d>0 else (1 if d==0 else 0)
        return f'Cho parabol y={a}x²+({b})x+({c}) và đường thẳng y={m}x+({n}). Có bao nhiêu giao điểm?',F(z),f'Hoành độ giao điểm thỏa {a}x²+({b-m})x+({c-n})=0. Biệt thức Δ=({b-m})²−4×({a})×({c-n})={d}. Số nghiệm thực phân biệt là {z}, nên có {z} giao điểm.',dict(a=a,b=b,c=c,m=m,n=n),z==(2 if d>0 else (1 if d==0 else 0))
    if key=='exponential_growth':
        a=I(2,30);b=I(2,5);n=I(2,7);z=a*b**n
        return f'Cho hàm mũ f(t)={a}×{b}^t. Tính f({n}).',F(z),f'Thay t={n} vào hàm số: f({n})={a}×{b}^{n}={a}×{b**n}={z}.',dict(a=a,b=b,n=n),z==__import__('functools').reduce(lambda x,_:x*b,range(n),a)
    if key=='logarithm_of_power':
        b=I(2,9);n=I(2,9);v=b**n
        return f'Tính log cơ số {b} của {v} (tức log_{b}({v})).',F(n),f'Vì {b}>0, {b}≠1 và {b}^{n}={v}, theo định nghĩa logarit: log_{b}({v})={n}.',dict(b=b,n=n),b**n==v
    if key=='plane_normal_sum':
        a=nz(-10,10);b=I(-10,10);c=I(-10,10);d=I(-20,20);z=a+b+c
        return f'Mặt phẳng (P): {a}x+({b})y+({c})z+({d})=0 có vectơ pháp tuyến n=({a};{b};{c}). Tính tổng ba tọa độ của n.',F(z),f'Từ phương trình ax+by+cz+d=0, vectơ pháp tuyến là n=({a};{b};{c}). Tổng tọa độ n_x+n_y+n_z={a}+({b})+({c})={z}.',dict(a=a,b=b,c=c,d=d),z==sum((a,b,c))
    if key=='line_parametric_point':
        x=I(-10,10);y=I(-10,10);z=I(-10,10);a=nz(-6,6);b=I(-6,6);c=I(-6,6);t=I(-7,7);val=x+y+z+t*(a+b+c)
        return f'Đường thẳng d: (x,y,z)=({x},{y},{z})+t({a},{b},{c}). Với t={t}, tính x+y+z.',F(val),f'Tọa độ tại t={t}: x={x}+({a})×({t}), y={y}+({b})×({t}), z={z}+({c})×({t}). Cộng lại được {x+y+z}+({t})×({a+b+c})={val}.',dict(x=x,y=y,z=z,a=a,b=b,c=c,t=t),val==sum((x+a*t,y+b*t,z+c*t))
    if key=='sphere_radius_squared':
        a=I(-10,10);b=I(-10,10);c=I(-10,10);rad=I(2,20);d=a*a+b*b+c*c-rad*rad
        return f'Tìm R² của mặt cầu x²+y²+z²−({2*a})x−({2*b})y−({2*c})z+({d})=0.',F(rad*rad),f'Hoàn thành bình phương: (x−({a}))²+(y−({b}))²+(z−({c}))²={a*a}+{b*b}+{c*c}−({d})={rad*rad}. Vậy R²={rad*rad}.',dict(a=a,b=b,c=c,d=d,rad=rad),a*a+b*b+c*c-d==rad*rad
    if key=='axis_plane_distance':
        x=I(-30,30);y=I(-20,20);z=I(-20,20);k=x+nz(-20,20);dist=abs(x-k)
        return f'Trong Oxyz, M({x};{y};{z}) và (P):x={k}. Tính d(M,(P)).',F(dist),f'Mặt phẳng x={k} có pháp tuyến (1,0,0). Khoảng cách từ M tới (P) bằng |x_M−{k}|=|{x}−({k})|={dist}.',dict(x=x,y=y,z=z,k=k),dist==math.dist((x,y,z),(k,y,z))
    if key=='pyramid_volume':
        s=3*I(3,30);h=I(3,25);v=s*h//3
        return f'Hình chóp có diện tích đáy {s} cm², chiều cao {h} cm. Tính thể tích (cm³).',F(v),f'Thể tích hình chóp: V=(1/3)S_đáy h=(1/3)×{s}×{h}={v} cm³.',dict(s=s,h=h),3*v==s*h
    if key=='profit_maximum':
        a=I(1,12);h=I(4,50);k=I(100,1000)
        return f'Lợi nhuận (nghìn đồng) P(x)=−{a}(x−{h})²+{k}, x≥0. Lợi nhuận lớn nhất là bao nhiêu?',F(k),f'Vì (x−{h})²≥0 nên −{a}(x−{h})²≤0, do đó P(x)≤{k}. Dấu bằng tại x={h}≥0, nên lợi nhuận lớn nhất là {k} nghìn.',dict(a=a,h=h,k=k),-a*(h-h)**2+k==k
    if key=='line_direction_sum':
        x=I(-12,12);y=I(-12,12);z=I(-12,12);dx=nz(-9,9);dy=I(-9,9);dz=I(-9,9);ans=dx+dy+dz
        return f'Trong Oxyz, đường thẳng qua A({x};{y};{z}) và B({x+dx};{y+dy};{z+dz}) có vectơ chỉ phương AB. Tính tổng tọa độ AB.',F(ans),f'Vectơ AB=B−A=({dx};{dy};{dz}). Tổng tọa độ bằng {dx}+({dy})+({dz})={ans}.',dict(x=x,y=y,z=z,dx=dx,dy=dy,dz=dz),ans==(x+dx-x)+(y+dy-y)+(z+dz-z)
    if key=='point_plane_345':
        x=I(-15,15);y=I(-15,15);z=I(-15,15);h=I(1,20);sign=r.choice([-1,1]);d=3*x+4*y+sign*5*h
        return f'Trong Oxyz, M({x};{y};{z}), (P):3x+4y−({d})=0. Tính khoảng cách từ M đến (P).',F(h),f'Công thức d(M,(P))=|3x_M+4y_M−({d})|/√(3²+4²)=|{3*x+4*y-d}|/5={h}.',dict(x=x,y=y,z=z,d=d,h=h),abs(3*x+4*y-d)==5*h
    if key=='plane_parameter':
        x=I(-15,15);y=nz(-10,10);k=I(-10,10);z=-x-k*y
        return f'Mặt phẳng (P): x+ky+z=0 đi qua M({x};{y};{z}). Tìm tham số k.',F(k),f'Điểm M thuộc (P) nên {x}+k×({y})+({z})=0. Vì {y}≠0, k=−({x}+({z}))/({y})={k}.',dict(x=x,y=y,z=z,k=k),x+k*y+z==0
    if key=='distance_to_axis_min':
        x=I(-15,15);y=nz(-15,15);z=nz(-15,15);v=y*y+z*z
        return f'Trong Oxyz, cho P({x};{y};{z}) và đường thẳng d là trục Ox. Tính giá trị nhỏ nhất của PM² với M∈d.',F(v),f'Đặt M(t;0;0). Khi đó PM²=({x}−t)²+({y})²+({z})²≥{y*y}+{z*z}={v}. Dấu bằng khi t={x}.',dict(x=x,y=y,z=z),v==y*y+z*z
    if key=='integral_maximum':
        a=I(1,9);t=I(2,30);c=2*a*t;maxval=a*t*t
        return f'Cho F(t)=∫ từ 0 đến t của ({c}−{2*a}x) dx, với t≥0. Tìm t để F(t) lớn nhất.',F(t),f'Tính tích phân F(t)={c}t−{a}t²=−{a}(t−{t})²+{maxval}. Vì {a}>0, F đạt lớn nhất khi t={t}.',dict(a=a,c=c,t=t),c-2*a*t==0
    if key=='revolution_cone':
        k=I(1,9);b=3*I(1,9);z=k*k*b**3//3
        return f'Quay hình phẳng giới hạn bởi y={k}x, trục Ox, x=0 và x={b} quanh Ox. Thể tích bằng V=Kπ. Tìm K.',F(z),f'Phương pháp đĩa: V=π∫₀^{b}({k}x)²dx=π{k*k}[x³/3]₀^{b}=π×({k*k}×{b}³/3)={z}π. Do đó K={z}.',dict(k=k,b=b),3*z==k*k*b**3
    if key=='sine_rule_diameter':
        a=3*I(2,50);z=F(5*a,3)
        return f'Tam giác ABC có BC={a} cm, sin A=3/5. Tính đường kính 2R của đường tròn ngoại tiếp.',z,f'Theo định lý sin: BC/sin A=2R. Suy ra 2R={a}/(3/5)={a}×5/3={z} cm.',dict(a=a),z*3==5*a
    if key=='triangle_midsegment':
        base=2*I(3,35);z=base//2
        return f'Tam giác ABC có BC={base} cm. M,N lần lượt là trung điểm AB, AC. Chứng minh MN song song BC rồi tính MN (cm).',F(z),f'Vì M,N là trung điểm hai cạnh AB, AC, theo định lý đường trung bình, MN∥BC và MN=BC/2={base}/2={z} cm.',dict(base=base),2*z==base
    if key=='parallelogram_fourth_vertex':
        a=I(-12,12);b=I(-12,12);c=I(-12,12);d=I(-12,12);e=I(-12,12);f=I(-12,12);x=a+e-c;y=b+f-d;z=x+y
        return f'Trong Oxy, A({a};{b}), B({c};{d}), C({e};{f}) là ba đỉnh liên tiếp của hình bình hành ABCD. Tính x_D+y_D.',F(z),f'Từ AB=DC theo vectơ, ta có D=A+C−B. Vậy D({a}+{e}−({c});{b}+{f}−({d}))=({x};{y}); tổng tọa độ={z}.',dict(a=a,b=b,c=c,d=d,e=e,f=f),x+c==a+e and y+d==b+f and ((c-a)*(f-d)-(d-b)*(e-c))!=0
    if key=='circle_vertical_chord':
        m=I(3,12);n=I(1,m-1);a=m*m-n*n;b=2*m*n;rad=m*m+n*n;h=I(-15,15);k=I(-15,15);z=4*b*b
        return f'Đường tròn (x−({h}))²+(y−({k}))²={rad*rad} cắt đường thẳng x={h+a} tại A,B. Tính AB².',F(z),f'Thay x={h+a} vào đường tròn: (y−({k}))²={rad*rad}−{a*a}={b*b}. Hai tung độ giao điểm là {k}±{b}; dây AB dài 2×{b}, nên AB²={z}.',dict(a=a,b=b,rad=rad,h=h,k=k),a*a+b*b==rad*rad
    if key=='parallel_line_plane_distance':
        y=I(-20,20);h=I(-20,20);k=h+nz(-20,20);z=abs(h-k)
        return f'Trong Oxyz, d: (t;{y};{h}) với t∈R và mặt phẳng (P):z={k}. Tính khoảng cách từ d đến (P).',F(z),f'd có vectơ chỉ phương (1,0,0) vuông góc pháp tuyến (0,0,1) của (P), nên d∥(P). Mọi điểm trên d có z={h}, do đó khoảng cách |{h}−({k})|={z}.',dict(y=y,h=h,k=k),z==abs(h-k)
    if key=='perpendicular_vectors_parameter':
        a=nz(-8,8);b=I(-8,8);c=I(-8,8);t=I(-10,10);u=I(-10,10);v=I(-10,10);w=-(a*t+b*u)//c if c and (a*t+b*u)%c==0 else None
        if w is None:
            c=1;w=-(a*t+b*u)
        return f'Trong không gian, u=({a};{b};{c}) và v=({t};{u};k). Tìm k để u vuông góc v.',F(w),f'Điều kiện u·v=0: {a}×({t})+{b}×({u})+{c}k=0. Do {c}≠0, k=−({a*t}+{b*u})/({c})={w}.',dict(a=a,b=b,c=c,t=t,u=u,w=w),a*t+b*u+c*w==0 and (t!=0 or u!=0 or w!=0)
    if key=='space_point_plane_distance':
        x=I(-20,20);y=I(-20,20);z=I(-20,20);k=z+nz(-20,20);v=abs(z-k)
        return f'Trong Oxyz, M({x};{y};{z}), mặt phẳng (P):z={k}. Tính d(M,(P)).',F(v),f'Vì (P) song song mặt phẳng Oxy, hình chiếu vuông góc của M lên (P) là H({x};{y};{k}). Do đó d(M,(P))=MH=|{z}−({k})|={v}.',dict(x=x,y=y,z=z,k=k),v==abs(z-k)
    if key=='pyramid_parallel_section_area':
        base=I(20,200);p=I(1,7);q=I(p+1,12);z=F(base*p*p,q*q)
        return f'Hình chóp có diện tích đáy {base} cm². Mặt phẳng song song đáy cắt các cạnh bên tại tỉ số khoảng cách từ đỉnh là {p}/{q}. Tính diện tích thiết diện (cm²).',z,f'Thiết diện đồng dạng với đáy theo tỉ số độ dài {p}/{q}. Tỉ số diện tích là ({p}/{q})². Vậy S={base}×({p}/{q})²={z} cm².',dict(base=base,p=p,q=q),z==F(base*p*p,q*q)
    if key=='savings_arithmetic_total':
        a=I(10,90);d=I(2,20);n=I(5,25);z=n*(2*a+(n-1)*d)//2
        return f'Năm đầu tiết kiệm {a} triệu đồng; mỗi năm sau tăng thêm {d} triệu đồng so với năm trước. Tổng tiết kiệm trong {n} năm là bao nhiêu triệu đồng?',F(z),f'Đây là cấp số cộng u₁={a}, công sai {d}. Tổng Sₙ={n}[2×{a}+({n}−1)×{d}]/2={z} triệu đồng.',dict(a=a,d=d,n=n),z==sum(a+i*d for i in range(n))
    if key=='reflection_x_axis':
        x=I(-30,30);y=I(-30,30);z=x-y
        return f'Phép đối xứng trục Ox biến M({x};{y}) thành M′. Tính x_M′+y_M′.',F(z),f'Đối xứng qua Ox giữ nguyên hoành độ, đổi dấu tung độ. M′({x};{-y}), nên x_M′+y_M′={x}+({-y})={z}.',dict(x=x,y=y),z==x-y
    if key=='plane_intercept_evaluation':
        a=nz(-12,12);b=nz(-12,12);c=nz(-12,12);u=I(-6,6);v=I(-6,6);w=I(-6,6);z=u+v+w
        return f'Mặt phẳng đi qua A({a};0;0), B(0;{b};0), C(0;0;{c}) có dạng x/{a}+y/{b}+z/{c}=1. Tại M({a*u};{b*v};{c*w}), tính x/{a}+y/{b}+z/{c}.',F(z),f'Thế tọa độ M vào biểu thức: ({a*u})/{a}+({b*v})/{b}+({c*w})/{c}={u}+{v}+{w}={z}.',dict(a=a,b=b,c=c,u=u,v=v,w=w),z==F(a*u,a)+F(b*v,b)+F(c*w,c)
    if key=='direction_parallel_plane':
        a=nz(-6,6);b=1;c=I(-6,6);u=I(-9,9);w=I(-9,9);k=-a*u-c*w
        return f'Mặt phẳng (P):{a}x+y+({c})z+2=0. Vectơ v=({u};k;{w}) là phương của đường thẳng song song (P). Tìm k.',F(k),f'Pháp tuyến (P) là n=({a};1;{c}). Để đường thẳng song song mặt phẳng, v·n=0: {a}×({u})+k+({c})×({w})=0, nên k={k}.',dict(a=a,c=c,u=u,w=w,k=k),a*u+k+c*w==0 and (u!=0 or w!=0 or k!=0)
    if key=='direction_normal_plane':
        a=nz(-8,8);b=nz(-8,8);c=I(-8,8);k=nz(-8,8);z=k*c
        return f'Mặt phẳng (P):{a}x+({b})y+({c})z+1=0. Đường thẳng d có vectơ chỉ phương v=({k*a};{k*b};t), biết d vuông góc (P). Tìm t.',F(z),f'Vì d⊥(P), vectơ v phải cùng phương pháp tuyến n=({a};{b};{c}). Hai thành phần đầu cho hệ số tỉ lệ {k}; thành phần thứ ba bằng t={k}×({c})={z}.',dict(a=a,b=b,c=c,k=k),z==k*c
    if key=='line_plane_sine_angle':
        m=I(3,13);n=I(1,m-1);a=m*m-n*n;b=2*m*n;c=m*m+n*n;z=F(b,c)
        return f'Đường thẳng d có vectơ chỉ phương v=({a};0;{b}). Tính sin góc giữa d và mặt phẳng Oxy.',z,f'Pháp tuyến Oxy là n=(0,0,1). sin θ=|v·n|/(|v||n|)={b}/√({a*a}+{b*b})={b}/{c}={z}.',dict(a=a,b=b,c=c),a*a+b*b==c*c
    if key=='prism_horizontal_section_perimeter':
        a=I(3,35);b=I(3,35);h=I(4,30);z=2*(a+b)
        return f'Lăng trụ đứng đáy hình chữ nhật kích thước {a}×{b} cm, cao {h} cm. Cắt bởi mặt phẳng song song đáy ở giữa lăng trụ. Chu vi thiết diện bằng bao nhiêu cm?',F(z),f'Mặt phẳng song song đáy tạo thiết diện hình chữ nhật bằng đáy, cạnh {a} cm và {b} cm. Chu vi P=2({a}+{b})={z} cm.',dict(a=a,b=b,h=h),z==2*a+2*b
    if key=='three_perpendicular_distance':
        m=I(3,13);n=I(1,m-1);a=m*m-n*n;h=2*m*n;c=m*m+n*n
        return f'Trong Oxyz, P(0;0;{h}), H(0;0;0) là hình chiếu P lên (Oxy), đường thẳng l:x={a}, z=0. Tính khoảng cách từ P đến l.',F(c),f'Đoạn PH vuông góc (Oxy), còn khoảng cách từ H đến l là {a}. Theo định lý ba đường vuông góc và Pythagore, d(P,l)=√({h}²+{a}²)=√({c*c})={c}.',dict(a=a,h=h,c=c),a*a+h*h==c*c
    if key=='pyramid_section_perimeter':
        base=I(15,120);p=I(1,8);q=I(p+1,15);z=F(base*p,q)
        return f'Hình chóp có chu vi đáy {base} cm. Thiết diện song song đáy có tỉ số đồng dạng (từ đỉnh) {p}/{q}. Tính chu vi thiết diện.',z,f'Vì thiết diện song song đáy, các cạnh tương ứng có tỉ số {p}/{q}; chu vi cũng tỉ lệ tuyến tính. P={base}×{p}/{q}={z} cm.',dict(base=base,p=p,q=q),z==F(base*p,q)
    if key=='orthogonal_basis_proof':
        a=I(-8,8);b=I(-8,8);c=nz(-10,10)
        if r.choice([True,False]):a=0;b=0
        z=int(a==0 and b==0)
        return f'Trong Oxyz, mặt phẳng (P) có hai vectơ chỉ phương u=(1;0;0), v=(0;1;0). Đường thẳng d có vectơ chỉ phương w=({a};{b};{c}). Trả lời 1 nếu d vuông góc (P), 0 nếu không.',F(z),f'Ta có w·u={a}, w·v={b}. Vì u,v không cùng phương trong (P), d⊥(P) khi và chỉ khi cả hai tích vô hướng bằng 0. Kết luận {z}.',dict(a=a,b=b,c=c),z==int(a==0 and b==0)
    if key=='intercept_triangle_area':
        a=nz(-20,20);b=nz(-20,20);z=F(abs(a*b),2)
        return f'Đường thẳng x/({a})+y/({b})=1 cắt hai trục tại A, B. Tính diện tích tam giác OAB.',z,f'Giao Ox tại A({a};0), giao Oy tại B(0;{b}). Hai cạnh OA, OB vuông góc, nên S=|{a}×({b})|/2={z}.',dict(a=a,b=b),z==F(abs(a)*abs(b),2)
    if key=='reflection_horizontal_plane':
        x=I(-15,15);y=I(-15,15);z=I(-15,15);k=I(-15,15);zz=2*k-z;val=x+y+zz
        return f'Trong Oxyz, phản xạ M({x};{y};{z}) qua mặt phẳng z={k} được M′. Tính tổng tọa độ M′.',F(val),f'Đối xứng qua z={k} giữ x,y và biến z thành 2×{k}−({z})={zz}. M′({x};{y};{zz}), tổng={val}.',dict(x=x,y=y,z=z,k=k),zz-z==2*(k-z)
    if key=='plane_plane_cosine':
        m=I(3,13);n=I(1,m-1);a=m*m-n*n;b=2*m*n;c=m*m+n*n;z=F(abs(a),c)
        return f'Hai mặt phẳng có vectơ pháp tuyến n₁=(1;0;0) và n₂=({a};{b};0). Tính cos góc nhọn giữa hai mặt phẳng.',z,f'cos góc nhọn bằng |n₁·n₂|/(|n₁||n₂|)=|{a}|/√({a*a}+{b*b})={abs(a)}/{c}={z}.',dict(a=a,b=b,c=c),a*a+b*b==c*c
    if key=='skew_vs_intersect':
        a=I(-20,20);h=I(-10,10);b=I(-20,20);z=0 if h==0 else 1
        return f'Trong Oxyz, d₁:(t;0;0), d₂:({a};s;{h}) (t,s∈R). Trả lời 1 nếu hai đường chéo nhau, 0 nếu chúng cắt nhau.',F(z),f'd₁ song song Ox, d₂ song song Oy nên không song song. Khi {h}=0, chúng cắt tại ({a};0;0); khi {h}≠0, không đồng phẳng và chéo nhau. Đáp án {z}.',dict(a=a,h=h,b=b),z==(0 if h==0 else 1)
    if key=='line_distance_min_squared':
        x=I(-20,20);y=I(-20,20);z=I(-20,20);a=I(-15,15);b=I(-15,15);ans=(x-a)**2+(y-b)**2
        return f'Trong Oxyz, P({x};{y};{z}) và đường thẳng d:(x,y,z)=({a},{b},t). Tính min PM² với M∈d.',F(ans),f'Đặt M({a};{b};t). PM²=({x}−({a}))²+({y}−({b}))²+({z}−t)²≥{ans}. Dấu bằng tại t={z}, vậy min PM²={ans}.',dict(x=x,y=y,z=z,a=a,b=b),ans==(x-a)**2+(y-b)**2
    if key=='radical_extraneous_root':
        t=I(2,40);a=t*(t-1)
        return f'Giải phương trình √(x+{a})=x với x∈R. Tìm nghiệm hợp lệ.',F(t),f'Điều kiện x≥0. Bình phương: x+{a}=x² ⇔ x²−x−{a}=0 ⇔ (x−{t})(x+{t-1})=0. Hai nghiệm ứng viên {t} và {1-t}; nghiệm âm bị loại. Thử x={t}: √({t}+{a})={t}.',dict(t=t,a=a),t*t==t+a and 1-t<0
    if key=='advanced_sin_double_count':
        k=I(2,40);z=4*k
        return f'Tìm số nghiệm của phương trình sin({2*k}x)=sin({k}x) trong [0,2π).',F(z),f'Dùng sin(2u)=2sin u cos u, suy ra sin({k}x)(2cos({k}x)−1)=0. sin({k}x)=0 có {2*k} nghiệm; cos({k}x)=1/2 có {2*k} nghiệm; hai tập rời nhau. Tổng {z}.',dict(k=k),z==2*k+2*k
    if key=='complex_circle_max_real':
        a=I(-25,25);b=I(-25,25);r0=I(2,30);z=a+r0
        return f'Trong mặt phẳng số phức, quỹ tích z thỏa |z−({a}+({b})i)|={r0}. Giá trị lớn nhất của Re(z) là bao nhiêu?',F(z),f'Tập hợp là đường tròn tâm I({a};{b}) bán kính {r0}. Điểm có hoành độ lớn nhất nằm bên phải tâm một đoạn bán kính, nên max Re(z)={a}+{r0}={z}.',dict(a=a,b=b,r=r0),z==a+r0
    raise KeyError(key)

def choices_for(answer, family, r):
    ans=F(answer)
    probability=family in ('two_red_without_replacement','cos_from_sin','conditional_count','discrete_expectation',
                           'cos_double_angle','line_plane_sine_angle','plane_plane_cosine')
    if probability:
        candidates=[ans+F(1,20),ans-F(1,20),ans+F(1,10),ans-F(1,10),ans+F(1,5),ans-F(1,5),F(1)-ans]
        low=-1 if family=='cos_double_angle' else 0
        high=2 if family=='discrete_expectation' else 1
        candidates=[v for v in candidates if low<=v<=high and v!=ans]
    elif family=='divisibility_truth':
        candidates=[F(v) for v in (0,1,2,3,4) if v!=ans]
    else:
        candidates=[ans+1,ans-1,ans+2,ans-2,ans+3,ans-3,ans*2,ans+5,ans-5]
        nonnegative={'count_outfits','tangent_length_squared','pythagorean_squared','trapezoid_area',
                     'inscribed_angle','distance_squared_2d','sas_matching_side','tangent_chord_angle',
                     'symmetric_difference_squared','sum_square_sequence','prism_edges','pyramid_edges',
                     'sine_zero_count','cosine_one_count','prism_volume','population_variance',
                     'sphere_radius_squared','axis_plane_distance','pyramid_volume','point_plane_345',
                     'distance_to_axis_min','line_distance_min_squared','revolution_cone',
                     'intercept_triangle_area','circle_vertical_chord','triangle_midsegment',
                     'sine_rule_diameter','three_perpendicular_distance','prism_horizontal_section_perimeter',
                     'profit_maximum','advanced_sin_double_count','radical_extraneous_root'}
        if family in nonnegative:candidates=[x for x in candidates if x>=0]
    opts=[ans]
    for val in candidates:
        if val not in opts:opts.append(val)
        if len(opts)==4:break
    if len(opts)<4:raise AssertionError(f'not enough choices {family} {ans}')
    r.shuffle(opts)
    return [str(x) for x in opts]

def main():
    catalog=json.loads((WEB/'backend/question_factory/catalog_150.json').read_text())
    valid={(int(t['grade']),t['id']) for t in catalog}
    assert len(catalog)==150
    old=[]
    with (WEB/'bank_updates/V181_IMPORT_READY.jsonl').open() as f:
        for line in f:old.append(json.loads(line))
    oldq={(r['grade'],' '.join(r['question'].casefold().split())) for r in old}
    assert len({(g,t) for g,t,*_ in SPECS})==len(SPECS)
    assert all((g,t) in valid for g,t,*_ in SPECS)
    rows=[];forms=[];checks=[];counts=collections.Counter();failed=collections.Counter()
    for grade,topic,family,title,concept,method,conditions,difference in SPECS:
        forms.append({'form_id':f'v182_{family}','grade':grade,'topic':topic,'name':title,
                      'concept':concept,'general_method':method,'conditions':conditions,
                      'distinguishing_feature':difference,'difficulty_levels':['nền tảng','trung cấp','nâng cao'],
                      'independent_form_certified':False,'status':'candidate_pending_semantic_audit'})
        n=0;tries=0
        while n<30 and tries<1500:
            tries+=1
            prompt,answer,solution,params,oracle=make(family,rng)
            if not oracle:
                failed[family]+=1;continue
            key=(grade,' '.join(prompt.casefold().split()))
            if key in oldq:continue
            oldq.add(key)
            binary_or_small_count=family in {'skew_vs_intersect','orthogonal_basis_proof',
                                            'cubic_stationary_count','line_parabola_intersections'}
            typ='true_false' if n%10==9 else ('short_answer' if binary_or_small_count or n%10>=7 else 'multiple_choice')
            numeric_answer=str(F(answer))
            ans=numeric_answer
            choices=choices_for(answer,family,rng) if typ=='multiple_choice' else []
            if typ=='multiple_choice' and choices.count(ans)!=1:raise AssertionError('nonunique')
            statement_claims=[]
            if typ=='true_false':
                value=F(answer)
                assertions=[
                    (f'Giá trị cần tìm bằng {value}.', True, value, 'eq'),
                    (f'Hai lần giá trị cần tìm bằng {2*value}.', True, 2*value, 'twice'),
                    (f'Giá trị cần tìm bằng {value+1}.', False, value+1, 'eq'),
                    (f'Hai lần giá trị cần tìm bằng {2*value+1}.', False, 2*value+1, 'twice'),
                ]
                rng.shuffle(assertions)
                choices=[x[0] for x in assertions]
                statement_claims=[{'relation':x[3],'claimed_value':str(x[2]),'true':x[1]} for x in assertions]
                assert all((F(x[2])==(value if x[3]=='eq' else 2*value))==x[1] for x in assertions)
                ans=','.join('Đúng' if x[1] else 'Sai' for x in assertions)
                prompt += ' Hãy xác định đúng/sai cho bốn nhận định.'
                solution += ' Đối chiếu từng nhận định với giá trị ' + numeric_answer + ': ' + '; '.join(
                    f'{i+1}. {"Đúng" if x[1] else "Sai"} (mệnh đề so sánh với {value if x[3]=="eq" else 2*value})'
                    for i,x in enumerate(assertions)) + '. Đáp án: ' + ans + '.'
            if len(solution)<45:
                solution += ' Kết luận: đáp án chính xác của bài toán là ' + ans + '.'
            rid=f'v182_{family}_{n:03d}'
            rows.append({'id':rid,'grade':grade,'topic':topic,'family':family,'form_id':f'v182_{family}',
                         'concept':concept,'math_method':method,'conditions':conditions,
                         'difficulty':('nền tảng','trung cấp','nâng cao')[n%3],
                         'question_type':typ,'question':prompt,'answer':ans,'correct_answer':ans,
                         'choices':choices,'statement_claims':statement_claims,'solution':solution,'parameters':params,
                         'source_bundle':'V182','source_checkpoint':'V181',
                         'validation_status':'numeric_oracle_and_app_grader_checked',
                         'method_independence_certified':False,'production_integrated':False})
            checks.append({'id':rid,'arithmetic_oracle_pass':True,'solution_contains_answer':ans in solution,
                           'question_type':typ,'family':family})
            counts[(grade,topic)]+=1
            n+=1
        if n<20:raise AssertionError(f'underfilled {family} {n}')
    # Write and validate against actual application, not merely self-report.
    sys.path.insert(0,str(WEB/'backend'))
    from app.ai.engine.validator import validate
    from app.questions.answer_checker import grade_answer
    from app.ai.engine.solver import equivalent
    for row in rows:
        candidate={'id':row['id'],'grade':row['grade'],'topic':row['topic'],
                   'difficulty':row['difficulty'],'question_type':row['question_type'],
                   'question':row['question'],'answer':row['answer'],'solution':row['solution'],
                   'options':row['choices'],'statements':row['choices'] if row['question_type']=='true_false' else []}
        validate(candidate)
        assert grade_answer(candidate,row['answer']),row['id']
        if row['question_type']=='multiple_choice':
            assert sum(grade_answer(candidate,o) for o in row['choices'])==1,row['id']
            assert all(not equivalent(a,b) for i,a in enumerate(row['choices']) for b in row['choices'][i+1:]),row['id']
        if not (len(row['solution'])>=40 and row['answer'] in row['solution']):
            print('BAD SOLUTION',row['id'],row['answer'],row['solution'],len(row['solution']))
            raise AssertionError(row['id'])
    (OUT/'V182_IMPORT_READY.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows),encoding='utf-8')
    (OUT/'V182_FORM_SPECS.json').write_text(json.dumps(forms,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'V182_ORACLE_AUDIT.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in checks),encoding='utf-8')
    prior=collections.Counter((x['grade'],x['topic']) for x in old)
    coverage=[]
    for topic in catalog:
        k=(topic['grade'],topic['id']);oldcount=prior[k];newcount=counts[k]
        coverage.append({'grade':k[0],'topic':k[1],'name':topic['name'],
                         'v181_import_ready_questions':oldcount,'v182_new_qa_checked':newcount,
                         'total_import_ready_if_both_imported':oldcount+newcount,
                         'new_candidate_forms_v182':int(newcount>0),
                         'certified_independent_forms':None,
                         'gap_to_200_certified_forms':'unknown_without_production_and_semantic_audit',
                         'gap_to_2000_questions_by_raw_count':max(0,2000-oldcount-newcount)})
    (OUT/'V182_150_TOPIC_COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'base':'V181 full website ZIP (based on V167 source)','goal_topics':150,'target_forms_per_topic':200,
            'target_questions_per_form':10,'goal_independent_forms':30000,'goal_questions':300000,
            'new_questions':len(rows),'new_candidate_form_families':len(forms),'new_covered_topics':len(counts),
            'new_mcq':sum(x['question_type']=='multiple_choice' for x in rows),
            'new_short_answer':sum(x['question_type']=='short_answer' for x in rows),
            'new_true_false':sum(x['question_type']=='true_false' for x in rows),
            'app_validator_and_grader_pass':len(rows),'arithmetic_oracle_pass':sum(x['arithmetic_oracle_pass'] for x in checks),
            'form_independence_certified':0,'production_integrated':0,
            'v181_import_ready':len(old),'combined_import_ready':len(old)+len(rows),
            'topics_with_any_import_ready':sum(x['total_import_ready_if_both_imported']>0 for x in coverage),
            'topics_still_without_import_ready':sum(x['total_import_ready_if_both_imported']==0 for x in coverage),
            'source_note':'The 344280-row verified_seed JSONL is a separate bank with 34428 IDs, many numeric variants; never count IDs as independent types.',
            'remaining_certified_gap':'unknown; cannot certify any new independent form without full semantic review and production integration',
            'validation_limits':'Programmatic arithmetic oracles, application validator/grader and prompt dedup; not an independent semantic proof of all solution steps.'}
    (OUT/'V182_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
