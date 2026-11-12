# MATH_WEB V114 – Báo cáo triển khai và kiểm chứng

**Dựa trên:** `MATH_WEB_GITHUB_READY_V113_CURATED_QUESTION_BANK.zip`.

## Mục tiêu người dùng

150 chủ đề × 2.000 dạng độc lập/chủ đề × 10 câu/dạng = **300.000 dạng độc lập, 3.000.000 câu hỏi**. Thay số hoặc đổi ID không tạo ra dạng độc lập mới.

## Kết quả thực tế

| Chỉ tiêu | Số thực tế | Cách hiểu |
|---|---:|---|
| Chủ đề trong danh mục | 150 | Có đủ tên/id |
| Chủ đề được ít nhất một blueprint V113/V114 phục vụ | 150 | Mỗi chủ đề tối thiểu một blueprint ứng viên |
| Blueprint ứng viên V113 | 60 | Không được tự coi là độc lập |
| Blueprint ứng viên mới V114 | 105 | 105 × 10 câu mẫu |
| Tổng blueprint V113 + V114 | 165 | Chưa được duyệt độc lập |
| Câu mẫu được tính lại đáp án | 1.650 | 600 V113 + 1.050 V114 |
| So trùng nguyên văn với ngân hàng cũ | 0 | Kiểm tra đối với 344.280 dòng nguồn |
| Nhóm khái niệm thô có nguy cơ chồng chéo | 16 | Báo cáo gắn cờ để con người duyệt |
| Dạng độc lập được chứng nhận | 0 | Chưa có bằng chứng duyệt đầy đủ |
| Dạng độc lập còn thiếu bằng chứng | 300.000 | Tính theo chuẩn chứng nhận nghiêm ngặt |
| Câu được công bố mới tự động | 0 | Chỉ ứng viên cách ly |

**Lưu ý:** Không tính 344.280 câu cũ là đã được kiểm định toàn diện. Bản gốc có nhiều dòng thiếu bằng chứng kiểm định hoặc lời giải ngắn, theo kiểm toán V113.

## Chất lượng và kiểm thử

- Kiểm tra tái sinh, đáp án toán học, phát hiện giả mạo đề và đáp án ở 105 bộ tạo mới.
- 12 seed bổ sung × 1.050 câu ứng viên = **12.600 lượt kiểm tra** tính hợp lệ và trùng nguyên văn trong từng lượt.
- 344.280 dòng ngân hàng cũ được duyệt bằng hàm băm câu chuẩn hóa; **0 trùng nguyên văn** với 1.650 câu mẫu V113/V114.
- Pytest chia theo ba nhóm độc lập: **31/31 + 60/60 + 61/61 = 152/152 ca đạt**. Việc chạy tất cả chung một lệnh đã gặp giới hạn thời gian, không được tính là một lần test tổng đạt.
- Một số cảnh báo FastAPI về `on_event` sắp bị loại bỏ; không làm test thất bại.
- Chưa có kiểm định thủ công từng câu, kiểm định ngữ nghĩa đầy đủ, chứng nhận phương pháp độc lập, kiểm thử production hay deployment online.

## Bảo toàn

- Giữ lại mọi file dự án V113.
- Các tệp gốc sửa có chủ đích: `backend/question_factory/engine.py`, `storage.py`, `cli.py`.
- Thêm engine, catalog, script kiểm toán, bài kiểm thử, hướng dẫn và dữ liệu mẫu V114.
- Ngân hàng `backend/app/ai/verified_seed/verified_seed_bank.jsonl` không bị thay đổi. Tài khoản, Battle, giao diện và toàn bộ mã game không bị sửa.
- `backend/database/mathweb.db` được khôi phục đúng byte từ V113 sau khi chạy kiểm thử, tránh lưu dữ liệu kiểm thử vào ZIP.

## Phần **chưa hoàn thành**

- 300.000 dạng độc lập được thẩm định và 3.000.000 câu chất lượng. Khối lượng, yêu cầu về chứng minh độc lập và kiểm định sư phạm không thể được suy ra từ 165 blueprint.
- Đánh giá chuyên gia và định dạng bài đa dạng (đúng/sai, trắc nghiệm nhiễu hợp lý, tự luận đa bước) trên toàn bộ danh mục.
- Dịch vụ tạo dạng toán sáng tạo tự động trên máy chủ có API mô hình, tài nguyên, ngân sách, hàng đợi đa máy và giám sát. V114 vẫn là thư viện generator hữu hạn, không tự sinh ra 300.000 phương pháp khác nhau.

## Đường dẫn tài liệu trong ZIP

- `QUESTION_FACTORY_V114_README.md`
- `V114_AUDIT/V114_REPORT.json`
- `V114_AUDIT/V114_150_TOPIC_COVERAGE.csv`
- `V114_AUDIT/V114_CANDIDATE_METHODS.jsonl`
- `V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl`

**Kết luận:** Phiên này đã triển khai thực tế 105 blueprint mới, kiểm tra 1.650 câu V113/V114 và tạo được ứng viên nội dung cho tất cả 150 chủ đề; tuyệt đối **chưa phải 100% mục tiêu**.
