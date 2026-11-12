# MATH_WEB NEON V12 - Báo cáo kiểm định lộ trình

Nguồn: NEON V11 (giữ nguyên toàn bộ thành phần khác).

## Thay đổi thực tế
- API đánh giá đầu vào trả thêm `per_topic_evidence`: với mỗi chủ đề và mỗi mức độ có số câu đã kiểm chứng, tối thiểu 3, và trạng thái đủ/chưa đủ.
- API trả `confidence_label` để tránh hiểu nhầm kết quả bài kiểm tra chưa đủ dữ liệu là đánh giá năng lực chính xác.
- Giữ các cơ chế V11: 3 mức độ, lưu bài làm, học lực theo chủ đề, bài kiểm tra 30 câu, ngưỡng 25/30, quyền Admin.

## Kiểm thử
- Backend: 176 passed (pytest).
- ZIP: kiểm tra CRC.

## Chưa hoàn thành
- Không có đủ câu được duyệt cho toàn bộ 150 chủ đề, nên chưa thể xác nhận ba bộ đề đầu vào đánh giá năng lực chính xác.
- Chưa có kiểm thử Battle/Chat trên hai thiết bị thật, chưa kiểm thử giao diện đối chiếu từng ảnh.
- AI gia sư chưa tự huấn luyện lại mô hình; chỉ cập nhật thống kê năng lực.

## Bảo vệ dữ liệu
Không đóng gói database và khóa đăng nhập; sao lưu dữ liệu tài khoản trước khi nâng cấp.
