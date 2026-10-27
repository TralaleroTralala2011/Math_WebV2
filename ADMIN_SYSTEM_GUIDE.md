# MATH WEB Admin System

## Truy cập
1. Khởi động backend theo `LOCAL_RUN.md` hoặc `START_BACKEND.bat`.
2. Khởi động frontend theo `START_FRONTEND.bat`.
3. Mở `admin.html` trên cùng frontend.
4. Đăng nhập bằng `admin19022011` với mật khẩu bootstrap `adminsitinh`.
5. Đổi mật khẩu ngay trong nút **Đổi mật khẩu**. Không dùng mật khẩu mặc định trên máy chủ công khai.

## Chức năng
- Tổng quan số tài khoản, trạng thái, hoạt động học tập và ngân hàng câu hỏi.
- Tìm tài khoản theo username, Player ID hoặc ID; xem điểm, level, XP, số câu đúng/sai/bỏ trống, kết quả theo chủ đề và lịch sử các phiên đã lưu.
- Cấm/mở cấm tài khoản. Tài khoản bị cấm bị từ chối ở login và các API xác thực, kể cả token đã cấp trước đó. Tài khoản admin không thể bị cấm qua API quản trị.
- Đặt lại mật khẩu người dùng; không thể dùng chức năng này để đổi mật khẩu admin.
- Thêm/xóa câu hỏi trong ngân hàng quản trị, kèm khối, chủ đề, độ khó, loại câu, lựa chọn, đáp án, lời giải và nguồn. Câu hỏi phù hợp được đưa vào nguồn của bộ sinh câu hỏi.
- Nhật ký thao tác quản trị và truy cập hồ sơ học tập.

## Quyền và bảo mật
- Quyền được kiểm tra ở backend, không tin vào giao diện hoặc `localStorage`.
- Tài khoản quản trị duy nhất có username `admin19022011`; API công khai không có thao tác tạo thêm admin. Cơ sở dữ liệu có unique index cho role admin.
- Mật khẩu được lưu dưới dạng PBKDF2-HMAC-SHA256 với salt, không lưu mật khẩu dạng chữ thường.
- Trước khi triển khai công khai, đổi mật khẩu admin, đặt `MATH_WEB_SECRET_KEY` ngẫu nhiên mạnh, bật HTTPS, hạn chế CORS theo domain thực tế và sao lưu database.
- Trang quản trị hiển thị các dữ liệu học tập đã được backend ghi nhận. Nó không thể khôi phục dữ liệu chưa từng được lưu. Nội dung chat riêng không được đưa vào bảng quản trị này.

## Lưu ý khi thêm câu hỏi
- Dùng đúng tên chủ đề tương ứng với kho kiến thức, ví dụ `Hàm số lượng giác`. Để trống mã trò chơi nếu câu hỏi dành cho luyện tập chung; nếu điền `game_id`, câu hỏi chỉ được chọn cho đúng trò chơi đó.
- Với trắc nghiệm, nhập 4 lựa chọn duy nhất; `Đáp án đúng` có thể là `A`, `B`, `C`, `D` hoặc nội dung lựa chọn chính xác.
- Với đúng/sai, nhập 4 mệnh đề ở ô lựa chọn, mỗi dòng một mệnh đề; đáp án dạng `Đúng,Sai,Đúng,Sai` hoặc `true,false,true,false`.
- Câu hỏi tự luận/trả lời ngắn cần đáp án chuẩn và lời giải để hệ thống chấm/giải thích đáng tin cậy.
