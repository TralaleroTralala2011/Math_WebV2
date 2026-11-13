# MATH_WEB V49: kiểm tra và sửa lỗi có giới hạn

Nguồn: V48 Admin Redesign.

## Đã sửa
- Hiệu ứng chuyển trang không can thiệp liên kết có onclick, role=button, aria-controls, data-bs-toggle, hash hoặc vùng data-no-transition.
- Hiệu ứng đổi tab Admin chỉ chạy sau khi tab thực sự hiện, tránh chạy animation trên phần tử ẩn.
- Dùng giá trị scrollIntoView hợp lệ `auto` thay cho `instant` khi giảm chuyển động.
- Cập nhật kiểm thử ghép trận ngẫu nhiên không có ngân hàng: chấp nhận 503 thay vì kỳ vọng AI sinh câu hỏi (trái yêu cầu Battle ngân hàng-only).

## Kiểm thử thực hiện
- `node --check js/page-transitions-v47.js`: đạt.
- `node --check js/admin-v48.js`: đạt.
- `pytest backend/tests/test_audit_round4_static_server.py`: 1 đạt.
- `pytest backend/tests/test_api_integration.py`: 3 đạt, 1 thất bại đầu tiên tại `test_direct_battle_invite_accept_and_start` do ngân hàng thử nghiệm trống, backend trả 503. Chưa chạy hết các test.

## Chưa được xác nhận
- Không có kiểm thử E2E GitHub Pages + Render; mật khẩu Admin trên Render chưa được đặt lại.
- Battle cần bộ câu hỏi hợp lệ được nạp trước khi có thể ghép trận thực tế.
- Chưa chứng minh 100% không lỗi; không thay đổi dữ liệu ngân hàng hoặc quyền truy cập backend.
