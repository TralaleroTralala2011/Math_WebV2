# MATH_WEB V73 – Chỉnh sửa MathGeo Studio dựa trên V72

## Bản nền
`MATH_WEB_V72_GITHUB_ACTIONS_CI_HOTFIX_20261116.zip`.

## Nội dung thay đổi
- Chỉnh logic dựng khung dây mặt cầu: dùng 64 đỉnh trên mỗi vĩ tuyến, 7 vòng vĩ tuyến, nối các kinh tuyến với cả hai cực N/S; nét phía sau phân biệt bằng gạch đứt, hình chiếu biên mặt cầu là đường tròn.
- Cải thiện khung dây trụ/nón; tránh hiển thị tên hàng trăm điểm lưới kỹ thuật trên hình hoặc bảng thống kê.
- Mỗi lần chọn mẫu mới: đặt lại camera, kéo xoay, pan/zoom và căn vừa hình, không để lại trạng thái từ mẫu trước.
- Thêm thao tác xoay quanh Oz ±15°, hỗ trợ hoàn tác/làm lại; lưu góc xoay Z trong snapshot.
- Thu gọn các đoạn trục Ox/Oy/Oz trong vùng nhìn thấy trên màn hình nhỏ; không gây mất nhãn trục do tràn mép.
- Đúng hình học: đáy của mẫu chóp S.ABCD là hình vuông (hai cạnh vuông góc và bằng nhau); bát diện đều có 12 cạnh bằng nhau.
- Giữ nguyên tọa độ nội bộ từ dữ kiện AI; chuẩn hóa bảng hiển thị điểm theo cùng đơn vị với ô nhập 3D (1 đơn vị = 24 pixel mô hình).

## Phạm vi thay đổi
Chỉ chỉnh `geometry-studio.html`. Không sửa backend, database, Word, ngân hàng câu hỏi, Battle hoặc hệ thống xác thực.

## Kiểm thử
- Node.js: `node --check` trên mã JavaScript nhúng: đạt.
- Chromium headless 1280 × 852 và 393 × 852: chọn đủ 13 mẫu 3D, chuyển 2D/3D, dựng điểm và cạnh, undo/redo, xoay Oz, AI dựng điểm Oxyz và hình thang AB=2CD: đạt; không ghi nhận lỗi JavaScript trong các lượt thử.
- Bất biến hình học mẫu: đáy chóp vuông góc và hai cạnh bằng nhau; bát diện đều có 12 cạnh dài √20000 đơn vị hình nội bộ (khoảng 141,421): đạt.
- Pytest Hình học: 30/30 bài đạt (`test_geometry_diagrams.py`, `test_geometry_curriculum.py`, `test_geometry_45_topic_expansion.py`, `test_neon_v21_geometry_personalization.py`).

## Giới hạn
Các kiểm thử được chạy cục bộ trong môi trường Chromium có mô phỏng layout; chưa thử 2 tài khoản thật trên GitHub Pages/Render, chưa kiểm định toàn bộ ngân hàng câu hỏi. Không thể xác nhận mọi chức năng trên website tuyệt đối không còn lỗi. Hãy kiểm tra trang trực tiếp sau deploy và giữ sao lưu database.
