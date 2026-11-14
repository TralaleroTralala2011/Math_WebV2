# MATH_WEB V57 · V55 BASE · ACCOUNT SPACING + BATTLE THPT LIBRARY

Nguồn gốc: MATH_WEB V55 (không thay V56).

## Phạm vi sửa
- account.html: nạp CSS khoảng cách mới; không sửa HTML cấu trúc hoặc JS tài khoản.
- css/account-spacing-v57.css: gỡ các khoảng trống lớn giữa navbar, tổng quan học tập, thống kê tài khoản.
- battle.html: đổi sang controller và CSS thư viện Battle V57.
- js/battle-topic-bookshelf-v57.js: nối frontend Tủ sách THPT tới API có sẵn của backend (/topic-catalog, /match/{id}/topics).
- battle-topic-library.html: bản giao diện Tủ sách Toán THPT Full Features, tùy biến cho Battle. Chỉ dùng danh mục chủ đề thật từ máy chủ, không dùng danh mục tĩnh của mẫu để phát đề.
- css/battle-topic-bookshelf-v57.css: overlay giao diện chọn sách và trạng thái chờ đối thủ.

## Quy trình
Hai bên chấp nhận trận -> SELECTING -> giao diện chọn sách riêng ở từng máy -> mỗi người chọn 1–3 -> chốt hoặc hết 120 giây -> đếm ngược 3–2–1 -> gửi lựa chọn lên backend. Khi cả hai bên chốt, backend lấy danh mục hợp lệ, tạo chung bộ câu hỏi và mốc giờ -> PLAYING -> tự chuyển sang khu vực thi đấu. Người chốt trước đợi người còn lại.

## Bảo toàn
Không chỉnh backend, schema, ngân hàng câu hỏi, đăng nhập, tài khoản, phần chấm điểm hoặc game.
