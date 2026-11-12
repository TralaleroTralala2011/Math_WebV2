# MATH WEB Admin System

## Truy cập
1. Khởi động backend theo `LOCAL_RUN.md` hoặc `START_BACKEND.bat`.
2. Khởi động frontend theo `START_FRONTEND.bat`.
3. Mở `admin.html` trên cùng frontend.
4. Đăng nhập bằng `admin19022011` với mật khẩu được in ở cửa sổ backend khi khởi tạo DB lần đầu (hoặc biến môi trường `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD`).
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


## Thư viện và bản xem trước trong Admin

- Thư viện hiện là catalog 139 chủ đề, không phải giáo trình hoàn chỉnh cho từng chủ đề. Số câu trong cột quản trị chỉ đếm câu đã lưu vào `admin_question_bank`; số 0 không có nghĩa AI nội bộ không thể sinh câu, nhưng có nghĩa chưa có câu được quản trị lưu ở bảng đó cho chủ đề này.
- Mục **Web thử nghiệm** nhúng `index.html` để xem giao diện MathWeb ngay trong Admin và mở ở tab riêng. Bản xem trước dùng chung backend/cơ sở dữ liệu hiện tại, KHÔNG phải môi trường sandbox cách ly. Dùng tài khoản người học riêng để kiểm tra.
- Tác vụ AI hiện sinh câu bằng bộ máy nội bộ theo chu kỳ khi backend đang chạy. Nó không tự truy cập Internet để thu thập tài liệu. Để bật nghiên cứu web, cần tích hợp nhà cung cấp tìm kiếm hợp pháp, đặt API key ở biến môi trường backend, giới hạn domain, lưu nguồn/trích dẫn, kiểm tra trùng lặp và kiểm duyệt đáp án trước khi đưa vào ngân hàng. Không nhúng key vào frontend hoặc GitHub.
