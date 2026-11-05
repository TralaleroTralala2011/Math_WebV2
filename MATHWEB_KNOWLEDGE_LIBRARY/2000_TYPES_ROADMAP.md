# Tiêu chuẩn chất lượng 2.000 dạng × 10 câu cho MATH_WEB

## Yêu cầu bắt buộc
- Mỗi chủ đề: ít nhất 2.000 **dạng toán khác nhau về phương pháp hoặc cấu trúc suy luận**.
- Mỗi dạng: ít nhất 10 câu hỏi khác nhau, được kiểm chứng đáp án và lời giải.
- Không tính đổi số, đổi tên biến, đảo thứ tự đáp án hoặc diễn đạt lại cùng một phương pháp thành dạng mới.
- Với 150 chủ đề hiện có: tối thiểu 300.000 dạng và 3.000.000 câu hỏi.
- Mỗi câu cần định danh chủ đề, dạng, cấu trúc, độ khó, nguồn gốc, lời giải, trạng thái kiểm định.

## Kiểm toán
Chạy `python scripts/audit_2000_types.py path/to/bank.jsonl --output coverage_report.json` từ thư mục gốc.
Mỗi dòng JSONL cần có `topic_id`, `type_id`, `structure_signature`, `question`, `answer`, `solution`.
Công cụ phát hiện câu hỏi trùng nguyên văn, ID dạng có chữ ký cấu trúc trùng nhau, dạng chưa đủ 10 câu và chủ đề chưa đủ 2.000 dạng.
**Cảnh báo:** chữ ký cấu trúc do người biên soạn khai báo, nên không thể tự chứng minh các dạng khác nhau về bản chất; kiểm toán toán học và phản biện chuyên môn vẫn bắt buộc.

## Trạng thái thực tế
Bản cập nhật này chỉ bổ sung **hệ thống kiểm toán và tiêu chuẩn nghiệm thu**, không tuyên bố đã có đủ 3 triệu câu hỏi.
Không có câu hỏi mới được tạo hàng loạt bằng cách thay số để giả đạt chỉ tiêu.
Trước khi triển khai quy mô lớn, cần thiết kế taxonomy riêng cho từng chủ đề, quy trình duyệt dạng, bộ giải/kiểm tra đáp án và nguồn nội dung có quyền sử dụng.
