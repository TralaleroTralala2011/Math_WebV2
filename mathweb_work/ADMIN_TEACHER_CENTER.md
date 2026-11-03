# MATH WEB · Trung tâm điều hành học tập

Bản nâng cấp tiếp nối dự án hiện có, giữ lại các trang và luồng cũ, đồng thời thêm phần quản lý học tập và giao bài.

## Tính năng mới

- **Kho câu hỏi tập trung:** câu hỏi được tạo trực tiếp trong Admin, AI nền và các luồng AI luyện tập/đấu online sẽ được lưu vào `admin_question_bank` khi có thể chuẩn hóa. Kho chống trùng lặp theo khối và nội dung câu hỏi. Câu hỏi AI cần được giáo viên rà soát trước khi dùng chính thức.
- **Trung tâm sư phạm trong Admin:** xem hiệu suất theo học sinh/chủ đề, lượt học, độ chính xác, bài tập đã nộp/chưa nộp và kết quả trung bình. Gợi ý ôn tập được xếp từ những chủ đề có độ chính xác thấp.
- **Giao bài:** chọn khối, chủ đề thư viện, độ khó, dạng câu, số câu, hạn nộp và học sinh nhận bài. Để trống danh sách ID học sinh sẽ giao cho tất cả tài khoản học sinh đang hoạt động.
- **Trang `learning.html`:** học sinh xem lộ trình gợi ý, thống kê theo chủ đề, bài tập được giao, làm bài, nộp bài và xem phản hồi/lời giải sau khi nộp. Đáp án không được gửi xuống trình duyệt trước khi nộp.
- **Đánh giá:** ghi trạng thái, số câu đúng, điểm phần trăm, thời gian làm bài, câu trả lời và phần suy luận học sinh tự trình bày để giáo viên xem xét. Việc suy luận dựa trên dữ liệu đã ghi nhận, không phải đánh giá năng lực tuyệt đối.
- **Nhật ký quản trị:** xem lộ trình và thao tác giao bài được ghi lại.

## API mới

- `GET /api/admin/learning/overview` (Admin): tổng quan người học, chủ đề cần hỗ trợ và bài tập.
- `POST /api/admin/learning/assignments` (Admin): tạo/giao bài.
- `GET /api/admin/learning/assignments` (Admin): danh sách bài.
- `GET /api/admin/learning/assignments/{id}/results` (Admin): kết quả từng học sinh.
- `GET /api/admin/learning/path` (Học sinh): lộ trình cá nhân hóa từ lịch sử luyện tập.
- `GET /api/admin/learning/assignments/mine` (Học sinh): bài tập được giao.
- `POST /api/admin/learning/assignments/{id}/start` (Học sinh): tạo/lấy bộ câu hỏi của bài.
- `POST /api/admin/learning/assignments/{id}/submit` (Học sinh): nộp câu trả lời và chấm điểm.

## Chạy local trên Windows

1. Mở PowerShell ở thư mục dự án.
2. Cài dependencies backend nếu chưa có: `python -m pip install -r backend/requirements.txt`.
3. Chạy backend: `cd backend`, sau đó `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
4. Mở terminal thứ hai ở thư mục gốc dự án, chạy `python -m http.server 5500`.
5. Mở `http://127.0.0.1:5500/login.html`, đăng nhập theo cơ chế hiện có. Admin mở trang quản trị `admin.html`; học sinh mở `learning.html` hoặc chọn **Hành trình học tập** ở thanh điều hướng.

## Giới hạn cần biết

- Cá nhân hóa hiện dựa trên lịch sử phiên/lượt chơi và độ chính xác đã được backend lưu. Nếu một hoạt động không ghi kết quả, nó không thể được phân tích.
- Thời gian được ghi chính xác cho bài tập giao qua trang `learning.html`; các lượt chơi cũ có thể không có thời lượng đủ tin cậy.
- Kho câu hỏi tích lũy các câu AI được sinh qua các endpoint đã tích hợp và tác vụ nền. Những bộ câu hỏi từ các luồng khác chưa được lưu vào ngân hàng sẽ không tự xuất hiện hồi tố.
- Bộ máy AI nội bộ không tự truy cập Internet. Câu hỏi sinh tự động có thể sai, trùng ý hoặc có lời giải chưa đạt chuẩn, nên cần kiểm duyệt. Chấm điểm hiện tự động chủ yếu theo đáp án đã chuẩn hóa; phần suy luận là bằng chứng để giáo viên xem xét, chưa phải hệ thống AI tự động chấm lập luận toán học.
- Hệ thống bạn bè, trò chuyện và đấu online hiện có được giữ lại; các kiểm thử hiện có cho luồng kết bạn/chat và matchmaking vẫn chạy qua bộ test.
