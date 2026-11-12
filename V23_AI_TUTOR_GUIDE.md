# Hướng dẫn AI gia sư V23

- API mới: `GET /api/roadmap-v2/tutor-plan/10`, `/11`, `/12`, kèm `Authorization: Bearer <student token>`.
- Câu đã duyệt có đáp án đúng/sai sau khi nộp được dùng **một lần** cập nhật Bayesian Knowledge Tracing. Bỏ qua và làm lại vẫn có trong lịch sử, không tạo thêm bằng chứng thành thạo sai lệch.
- Sau đề đầu vào cố định, hệ thống đưa ra **ba chủ đề đang mở**, lý do ôn, mức độ cần luyện, kế hoạch 5 bước, liên kết tới học liệu và bài kiểm tra 30 câu. Mở chặng tiếp chỉ khi đủ 3 chủ đề đạt 25/30.
- API `GET /api/roadmap-v2/tutor-data/10` cho phép người học xuất hồ sơ riêng sang JSON; không xuất đề/đáp án.
- Nếu đề đầu vào chưa được duyệt độc lập, API không bịa thông tin năng lực và không mở lộ trình chính thức.
- Đây là cá nhân hóa thích ứng có giới hạn, **không phải AI được huấn luyện trên toàn bộ dữ liệu học sinh** hoặc bài kiểm tra đã chuẩn hóa tâm trắc.
