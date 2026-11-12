# V18 · Hướng dẫn quản trị đề cố định

- Lớp 10 / 11 / 12 vẫn có ba ma trận riêng. Phải duyệt tối thiểu 3 câu mỗi mức, 2 dạng đã duyệt khác bản chất trong số **được chọn** và 2 kiểu trả lời/chủ đề.
- Khi chỉnh sửa ma trận hoặc thu hồi câu hỏi, đề cũ tự mất hiệu lực. Admin cần kiểm tra lại và xuất bản lần mới.
- Kết quả người thi: xem điểm, tóm tắt theo chủ đề/mức và gợi ý ôn; đáp án và lời giải chi tiết đề cố định được giữ riêng để hạn chế chia sẻ đáp án.
- Bài kiểm tra 30 câu từng chủ đề vẫn được xem đầy đủ câu, đáp án và lời giải sau khi nộp.
- Lưu bản nháp thường xuyên. Bài đầu vào 441–459 câu có thể gây mệt mỏi; nên tổ chức nhiều buổi làm có giám sát, không ép người học hoàn tất liên tục.
- `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'` để thử regression nhanh.
- Để bảo vệ khóa đáp án, triển khai tách frontend và backend/database. Đừng đưa gói kiểm duyệt riêng vào web root.
