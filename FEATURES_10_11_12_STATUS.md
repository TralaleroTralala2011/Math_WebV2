# Tính năng 10–12: Báo cáo triển khai có giới hạn

- 10: API tạo và duyệt bài học dành cho admin; giao bài tới tài khoản được chọn; người học xem bài giao và nhận xét. Không tự tuyên bố đã có hệ thống tài khoản giáo viên độc lập; tài khoản admin hiện đóng vai trò duyệt/giao.
- 11: Huy hiệu từ kết quả thi/ôn tập có thật. Không cộng XP trùng, không tạo nhiệm vụ theo chương hoặc hệ thống chống gian lận hoàn chỉnh.
- 12: API kiểm tra cấu trúc bài học, chủ đề trùng, câu hỏi trùng và thiếu đáp án. Chưa kiểm chứng toán học tổng quát, chưa tự động chặn mọi luồng xuất bản cũ.

Giao diện mới: `final-features.html`. API: `/api/final-features/*`. Bảo toàn các trang cũ. Chạy backend như trước.

## Những việc còn phải làm trước khi khẳng định hoàn thành 100%

- Kết nối tài khoản giáo viên riêng với phân quyền theo lớp; nộp bài và chấm bài tập thực tế.
- Nhiệm vụ theo chương, XP có giới hạn, chống cày điểm và kiểm thử chuỗi học tập.
- Quality gate tích hợp vào toàn bộ pipeline nhập/sinh câu hỏi, kiểm chứng đáp án bằng toán học, kiểm thử hồi quy giao diện và dữ liệu.
- Hoàn thiện nội dung thật cho 150 chủ đề và kho dạng bài ở quy mô đã yêu cầu; hiện còn nhiều nội dung chưa được xác minh.
