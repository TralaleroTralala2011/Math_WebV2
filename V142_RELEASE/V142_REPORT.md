# MATH_WEB V142 | Kiểm toán chứng nhận dạng toán

Nguồn: MATH_WEB_GITHUB_READY_V141_RESEARCH_CERTIFIED_PROGRESS.zip (3315 mục ZIP).

## Thay đổi thực tế
- Bổ sung 4 chỉ số chẩn đoán trong `question_factory.storage.progress`: `certifications_without_approval`, `certifications_with_empty_evidence`, `verified_questions_on_unapproved_certified_methods`, `certification_integrity_warnings`.
- Giữ nguyên các chỉ số và API cũ để tránh làm hỏng chức năng. Các cảnh báo không phải bằng chứng chứng nhận toán học, chỉ phát hiện các bất thường cơ bản.
- Thêm 2 kiểm thử về chứng nhận thiếu duyệt/thiếu bằng chứng và chứng nhận có duyệt + bằng chứng không rỗng.
- 13/13 kiểm thử V140/V141/V142 liên quan đạt. Không chạy hồi quy toàn hệ thống, không thử Battle E2E.

## Ngân hàng câu hỏi
- 11 ứng viên V141, 110 câu nghiên cứu vẫn ở trạng thái chờ thẩm định, không xuất bản.
- Dạng toán độc lập mới được chứng nhận: 0. Câu mới được xuất bản: 0.
- Không tạo biến thể số liệu để tăng thành tích. Mục tiêu 300.000 dạng và 3.000.000 câu chưa đạt.

## Lượt sau
- Kiểm toán sâu chứng nhận về tính độc lập phương pháp, không chỉ sự hiện diện hồ sơ.
- Đánh giá ứng viên V141 so với danh mục phương pháp hiện có, chạy test V120 chậm và E2E Battle.
- Giữ nguyên dữ liệu SQLite trong ZIP. Thời gian mỗi lượt phụ thuộc giới hạn thực thi.
