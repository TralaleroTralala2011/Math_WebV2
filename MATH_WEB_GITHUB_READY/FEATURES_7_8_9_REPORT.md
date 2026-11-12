# MATH_WEB: tính năng 7, 8, 9 (bản khởi tạo có thể chạy)

- Dựa trên FEATURES_4_5_6, giữ nguyên trang và API cũ.
- Truy cập `study-suite.html`; backend thêm `/api/study-suite`.
- Ngân hàng khởi tạo 9 câu số học/toán kiểm chứng thủ công; phân nhóm theo chủ đề, dạng, độ khó, nguồn. Chưa đạt mục tiêu 1.000 dạng/chủ đề và không tuyên bố phủ 150 chủ đề.
- Thi thử: chỉ người đăng nhập, giới hạn thời gian phía server, chấm đáp án số, khóa nộp lặp, báo điểm và lời giải. Đề 15/45 phút là cấu hình thời gian, chưa có blueprint đề học kỳ hoặc tốt nghiệp. Hết giờ hiện báo lỗi, chưa tự nộp.
- Ôn tập: tạo lịch từ kết quả thi, tăng/giảm khoảng cách theo đáp án; không tính XP.
- Lưu SQLite riêng `backend/database/study_suite.sqlite3`.
- Chưa hỗ trợ chấm tự luận/biểu thức, xác minh hình học tổng quát, nguồn Internet, quản trị duyệt nội dung, hoặc sinh đề theo ma trận chính thức.
- Chạy backend như trước và frontend `python -m http.server 5500`.
