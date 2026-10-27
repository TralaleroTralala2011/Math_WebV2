# MATH_WEB Knowledge Library 1.0.0
## Báo cáo để người dùng rà soát
Ngày tạo: 24/10/2026

### Mục tiêu
Bổ sung một gói thư viện kiến thức có cấu trúc cho MATH_WEB, bao phủ khung Toán phổ thông lớp 10–12 và bản đồ Toán chuyên/HSG/Olympiad. Gói này mở rộng theo dữ liệu, không khóa ở 147 chủ đề.

### Đã đóng gói trong thư viện này
- `topic_coverage_catalog.json`: danh mục 139 chủ đề có sẵn trong ZIP đầu vào: lớp 10 = 45, lớp 11 = 47, lớp 12 = 47. Các mục giữ nguyên tên/ID/subtopic từ `backend/app/ai/knowledge/index.json`.
- `olympiad_advanced_map.json`: 46 nhánh/đầu mục Toán chuyên và HSG: số học, đại số, bất đẳng thức, đa thức, phương trình hàm, dãy số, tổ hợp, hình học, giải tích, xác suất và phương pháp chứng minh.
- `formula_theorem_bank.json`: 74 mục công thức/định lý/phương pháp tham khảo, có điều kiện và ghi chú khi cần.
- `question_archetypes.json`: 28 khuôn tư duy/dạng hỏi khác nhau để thiết kế đề đa dạng, không chỉ thay số.
- `SOURCE_REGISTER.md`: nguồn chính thức/nguồn tham khảo và quy tắc ghi nhận nguồn.
- `DATA_SCHEMA.json`: lược đồ gợi ý cho các bản ghi kiến thức, câu hỏi, lời giải và nguồn.
- `COVERAGE_AND_LIMITATIONS.md`: cách hiểu đúng về độ bao phủ và những việc còn cần làm.

### Đếm chính xác từ dữ liệu hiện tại
- Chủ đề phổ thông có sẵn: 139, không phải 147.
- Đầu mục bản đồ Toán chuyên/HSG: 46.
- Công thức/định lý/phương pháp tham khảo: 74.
- Dạng tư duy/dạng hỏi: 28.
- Các con số này thuộc các bảng khác nhau, không được cộng thành “tổng chủ đề duy nhất” vì phạm vi có thể giao nhau.

### Quan trọng: giới hạn hiện tại
Đây là **bản thư viện nền có cấu trúc và bộ khung kiến thức ban đầu**, chưa phải bằng chứng rằng mọi sách giáo khoa, sách bài tập, mọi đề thi tỉnh/quốc gia và mọi lời giải trên Internet đã được thu thập hết. Danh mục chủ đề không đồng nghĩa đã có bài giảng đầy đủ cho từng chủ đề; ngân hàng công thức cần được giáo viên/chuyên gia rà soát trước khi dùng làm đáp án tự động.

Muốn đạt độ bao phủ cao có thể kiểm toán, mỗi mục phải được bổ sung theo quy trình:
1. Đối chiếu chương trình phổ thông và chương trình nâng cao chính thức.
2. Lập ma trận yêu cầu cần đạt theo khối, chủ đề, kiến thức tiên quyết.
3. Gắn định lý/công thức với điều kiện áp dụng và chứng minh/diễn giải.
4. Viết bài tập gốc đa dạng ở các dạng trắc nghiệm, đúng/sai, trả lời ngắn và tự luận.
5. Kiểm chứng lời giải độc lập; kiểm tra dữ kiện, đáp án và hình vẽ.
6. Gắn nguồn, giấy phép, năm/kỳ thi và trạng thái rà soát.
7. Chạy phát hiện trùng lặp theo cấu trúc toán học và kiểm thử nhiều lần.

### Tích hợp vào website
Gói thư viện đã được thêm vào ZIP dự án dưới thư mục `MATHWEB_KNOWLEDGE_LIBRARY/` để xem xét và phát triển tiếp. Việc thêm các tệp dữ liệu này **không tự động chứng minh** rằng bộ sinh câu hỏi đang nạp toàn bộ dữ liệu mới; bước tích hợp runtime và kiểm thử API là công việc riêng, phải thực hiện rồi xác minh trước khi tuyên bố hoàn thành.
