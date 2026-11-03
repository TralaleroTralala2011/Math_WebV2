# MATH_WEB - Bản nâng cấp tài khoản, thông báo và Battle

## Những thay đổi trong bản này

1. **Sửa trạng thái tải trang tài khoản**
   - Trước đây HTML dùng `#accountLoadingState.account-loading-state` nhưng JavaScript chỉ ẩn `.account-loading`, vì vậy dòng “Đang tải thông tin tài khoản...” có thể nằm lại mãi.
   - Đồng bộ selector loading và error với ID/class thực tế trong `account.html`.
   - Nếu API hồ sơ tạm thời không trả dữ liệu, trang thử dùng hồ sơ đã lưu trong `localStorage` và hiển thị lỗi rõ ràng thay vì để giao diện mắc kẹt.

2. **Tìm kiếm Player ID**
   - Chuẩn hóa truy vấn ID không phân biệt chữ hoa/chữ thường ở các truy vấn hồ sơ người dùng và tìm người chơi Battle.
   - Giữ nguyên quy tắc không cho tìm chính tài khoản đang đăng nhập.

3. **Thông báo dạng game**
   - Bổ sung toast hình chữ nhật trượt vào từ góc trên bên phải.
   - Thông báo mới được kiểm tra định kỳ khi người dùng đang mở trang và đã đăng nhập.
   - Thông báo tin nhắn có thể mở đúng cuộc trò chuyện qua `chat.html?user_id=...`.
   - Thông báo lời mời Battle hiển thị nút Chấp nhận/Từ chối và bộ đếm 18 giây.
   - Nhấn thông báo trong khay thông báo sẽ điều hướng tới khu vực liên quan.

4. **Thời hạn lời mời Battle**
   - Lời mời chờ xác nhận hết hạn sau 18 giây ở Backend.
   - Chấp nhận sẽ chuyển trận sang trạng thái `STARTING`; từ chối hoặc hết hạn sẽ hủy lời mời.
   - Backend vẫn là nơi quyết định lời mời còn hiệu lực, không chỉ dựa vào bộ đếm giao diện.

## Kiểm tra đã thực hiện

- `node --check` cho các JavaScript đã chỉnh sửa.
- `python -m compileall` cho Backend.
- Bộ kiểm thử Backend: **90 passed, 4 warnings** (chạy với `PYTHONPATH=.` từ thư mục `backend`).

## Lưu ý

Đây là bản nâng cấp trực tiếp trên ZIP được cung cấp. Cần chạy thử hai tài khoản thật trên cùng Backend để kiểm tra luồng mời, chấp nhận, từ chối và hết hạn trên trình duyệt. Toast dùng polling định kỳ nên thời điểm hiển thị phụ thuộc chu kỳ kiểm tra và kết nối máy chủ.
