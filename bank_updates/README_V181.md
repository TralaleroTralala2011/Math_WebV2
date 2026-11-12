# MATH_WEB V181 | Ngân hàng câu hỏi tích hợp vào website

Nguồn: V179 (1.900 câu), V180 QA (1.470 câu) và V180 bổ sung (360 câu).

- Tổng đầu vào: 3.730 câu.
- Vượt kiểm tra cấu trúc, kiểm tra đáp án qua bộ chấm đang dùng và điều kiện một đáp án trắc nghiệm: **3.695 câu**.
- Cách ly: **35 câu** do có phương án trắc nghiệm tương đương nhau về giá trị toán học.
- Chủ đề trong danh mục chính thức được bổ sung dữ liệu: **67/150**.
- Dạng toán độc lập mới được chứng nhận: **0**.
- Các phép tính/đáp án được kế thừa từ kiểm chứng của V179/V180; chưa có kiểm toán toàn diện mọi lời giải và tính độc lập ngữ nghĩa.

## Nhập vào ngân hàng đang hoạt động

Bản phát hành này chứa mã nguồn website hoàn chỉnh, nhưng **không ghi đè cơ sở dữ liệu cá nhân của bạn**. Các câu mới nằm trong `V181_IMPORT_READY.jsonl`. Hãy dừng backend, sao lưu dữ liệu, sau đó chạy `IMPORT_BANK_V181.bat` (Windows), hoặc:

```bash
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db
python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db --write --backup backups/mathweb-before-v181.sqlite
```

Nếu bạn dùng `MATHWEB_DB_PATH` hoặc `MATHWEB_DATA_DIR`, hãy thay `--db` bằng đường dẫn thực tế. File đích phải là SQLite MATH_WEB hiện có với bảng `admin_question_bank`. Lệnh mặc định chỉ xem trước; `--write` bắt buộc có đường dẫn backup mới. Import chạy trong transaction, có ledger nguồn và chạy lại không tạo bản ghi trùng.

Đã thử nghiệm trên **bản sao SQLite cô lập**: 0 → 3.695 câu; nhập lần hai 0 câu; toàn vẹn SQLite OK; các câu có thể lấy qua `/api/ai/questions`, chấm qua `/api/ai/questions/{id}/answer` và sử dụng trong bài tập được giao. Chưa triển khai lên production của bạn.

## Không được tính thành 3.695 dạng toán mới

Các câu trên thuộc những nhóm phương pháp đã có/ứng viên. Cả 8 tiêu chí chứng nhận dạng độc lập vẫn phải được thẩm định trước khi cộng vào mục tiêu 300.000 dạng và 3.000.000 câu.
