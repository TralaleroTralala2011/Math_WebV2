# KIỂM TRA ĐỘ PHÙ HỢP CHỦ ĐỀ VÀ CHỐNG TRÙNG

Bản cập nhật bổ sung **cổng kiểm tra độ phù hợp** vào `scripts/audit_2000_types.py`.

Mỗi câu trong ngân hàng JSON/JSONL cần có `topic_id`, `type_id`, `skill_id`, `reviewed_topic_id`, `topic_alignment_reviewed: true`, `structure_signature`, `question`, `answer`, `solution`.

- `skill_id`: kỹ năng toán học cụ thể mà câu kiểm tra, không phải nhãn chung như `toan`.
- `reviewed_topic_id`: ID chủ đề đã được người biên soạn kiểm tra.
- `topic_alignment_reviewed`: chỉ `true` khi người kiểm duyệt thực sự xác nhận câu hỏi thuộc đúng chủ đề.
- Một `type_id` + `structure_signature` xuất hiện ở nhiều chủ đề bị báo trùng liên chủ đề.
- Một câu trùng nguyên văn ở bất kỳ chủ đề nào bị báo lỗi.
- Chủ đề thiếu kiểm duyệt không đạt chuẩn số lượng.

**Giới hạn quan trọng:** các trường metadata do người cung cấp có thể khai sai. Bộ kiểm toán không tự chứng minh nội dung câu phù hợp với chủ đề, cũng không chứng minh lời giải đúng. Cần kiểm duyệt nội dung, bộ kiểm chứng toán học và kiểm thử bổ sung. Không được gắn `topic_alignment_reviewed: true` hàng loạt mà không kiểm duyệt.

Chạy: `python scripts/audit_2000_types.py path/to/bank.jsonl --output report.json`

Đây là nâng cấp kiểm soát chất lượng, **không phải** 3 triệu câu đã hoàn thành.
