# MATH_WEB V29 | Đối chiếu V28 + Math_WebV2-main(5)

Ngày: 12/11/2026. **Kết quả: hoàn thành nhóm thay đổi được người dùng duyệt trong lượt này; chưa đạt 100% toàn bộ mục tiêu dài hạn của MATH_WEB.**

## Những thay đổi trực tiếp

1. **Trang chủ**: khôi phục giao diện Trang chủ truyền thống với hero “Học Toán thú vị hơn”, phần Học theo cách của bạn và các liên kết luyện tập. Không nạp V5–V28 NEON overlay trên `index.html`.
2. **Tài khoản**: chuyển dashboard “Chào mừng trở lại”, XP, streak 12 tuần, chủ đề tiếp theo, liên kết học tập, tiến độ các khối lớp, AI gia sư và gợi ý ôn tập sang `account.html`. Giữ nguyên hồ sơ, thống kê, bạn bè, nút Đăng xuất, các ID và logic hiện có. Điều chỉnh khoảng cách để taskbar desktop không che lời chào.
3. **Battle**: giữ HTML, CSS, JS truyền thống, bỏ V5–V28 overlay và đoạn giới thiệu được chèn thêm. Không sửa hệ thống đấu, ghép trận, WebSocket hay luật chơi.
4. **Taskbar desktop**: hiển thị lại navbar cũ ở tất cả trang người học đã nạp thiết kế chung, ẩn navbar tạo thêm từ V5 trên desktop; không thay CSS định vị của navbar cũ. Trên điện thoại giữ menu phù hợp màn hình.
5. **Notification**: giữ nguyên ID `notificationButton` và sự kiện trên nút chuông cũ ở desktop. Trên mobile, nút chuông dùng cơ chế chuyển tiếp click sang nút thật và đồng bộ badge, không xóa sự kiện cũ. Chưa kiểm thử sự kiện nhận thông báo thực trên backend nhiều tài khoản.
6. **Học thử**: banner chỉ hiện khi không có phiên học sinh/quản trị; vào thử không xóa token học sinh. Hỗ trợ khôi phục token dự phòng chỉ khi thực sự còn từ V28, không ghi đè phiên mới.
7. **Giữ đăng nhập**: dùng token phiên hiện có trong localStorage qua chuyển trang, kể cả vào nhầm login/register sẽ chuyển lại Tài khoản. Không lưu mật khẩu dưới dạng rõ. Đăng xuất dọn cả token dự phòng cũ; token hết hạn hoặc bị máy chủ từ chối vẫn cần đăng nhập lại, nhưng dữ liệu tài khoản trên máy chủ không bị mất.
8. **Đồng bộ**: thêm `css/v29-user-preferences.css` vào các trang người học còn dùng theme NEON. Giữ Admin tách biệt.

## Kiểm thử đã thực hiện

- Backend: `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'` đạt **230 passed, 1 deselected** trong lượt hoàn chỉnh đầu tiên (log `MATH_WEB_V29_BACKEND_TEST.log` nằm ngoài ZIP). Bốn kiểm thử UI hợp đồng kiểu cũ thất bại ở lượt đầu vì trái yêu cầu mới, được cập nhật để kiểm tra đúng hành vi mới và bổ sung bốn kiểm thử V29.
- Kiểm thử tập trung sau sửa cuối: **12 passed** (`test_neon_v29_user_preferences.py`, `test_neon_v27_usability.py`, `test_neon_v6_visual_contract.py`).
- Lượt hồi quy đầy đủ thứ hai sau sửa cuối không kết thúc trong giới hạn công cụ. Không được tính là lượt đạt.
- `node --check`: các JS liên quan đến dashboard, auth, trial, notification đều qua kiểm tra cú pháp.
- Kiểm thử Chromium cô lập bằng `page.set_content` và nạp local JS/CSS (vì Chromium chặn điều hướng HTTP/file trong môi trường): **1366×768 và 390×844** có dashboard + hồ sơ cũ, desktop navbar gốc, mobile navbar riêng, không tràn ngang, không báo lỗi JavaScript. Đây không phải kiểm thử end-to-end máy chủ.
- ZIP kiểm tra toàn vẹn CRC; không đóng gói database thực hay khóa bí mật.

## Chưa thể xác nhận hoặc chưa hoàn thành 100%

- Đề đầu vào chính thức cho 150 chủ đề thiếu đủ câu đã kiểm chứng độc lập. Không mở khóa bằng câu chưa kiểm duyệt.
- AI cá nhân hóa chưa được hiệu chuẩn bằng dữ liệu thực nghiệm; Question Factory chưa đủ 300.000 dạng độc lập.
- Battle và Chat chưa chạy kiểm thử hai thiết bị/người thật kết nối qua WebSocket.
- Không kiểm thử thực tế phiên xác thực với backend qua Chromium do chính sách chặn localhost/file; chỉ bảo đảm các đường dẫn mã hiện có không tự xóa token và có kiểm thử hồi quy/backend.
- Bản ZIP vẫn giữ các bản sao/hồ sơ cũ trong `mathweb_work` để tránh mất dữ liệu; có thể dọn dẹp riêng sau khi xác nhận không có script nào phụ thuộc.

## Cài đặt

Sao lưu `backend/database/` và các khóa cấu hình đang chạy trước khi thay mã. ZIP không mang theo database/khóa bí mật. Khởi động backend và frontend theo hướng dẫn của dự án, tránh chạy trực tiếp `file://` nếu cần API/WebSocket.
