# MATH_WEB V114: Ngân hàng 150 chủ đề, Question Factory

> **Không phải bản hoàn thành 3 triệu câu.** Phiên bản này giữ nguyên 344.280 câu trong ngân hàng gốc, bổ sung 105 bộ tạo dạng toán ứng viên với 1.050 câu mẫu, tổng V113 + V114: 165 ứng viên với 1.650 câu mẫu. Tất cả **chưa được chứng nhận độc lập về phương pháp** và đều chờ duyệt, không được tự đưa vào ngân hàng công khai.

## Đã có

- Danh mục 150 chủ đề Toán 10–12 trong `backend/question_factory/catalog_150.json`.
- Mỗi chủ đề có tối thiểu **một** bộ tạo dạng mới từ V113/V114. Điều này **không có nghĩa** đã có 2.000 dạng độc lập/chủ đề.
- V113: 60 blueprint và 600 câu mẫu.
- V114: 105 blueprint mới và 1.050 câu mẫu mới; mỗi blueprint tạo 10 câu khác nhau theo cấu hình mặc định.
- Tạo câu theo seed cố định, bộ xác minh biểu thức/toán học riêng từ tham số, kiểm tra nội dung tái sinh không bị sửa, và kiểm tra trùng nguyên văn.
- Dữ liệu mới cách ly trong `V114_AUDIT/`, không can thiệp 344.280 dòng gốc, không sửa giao diện, tài khoản, Battle hay các trang game.

## Xem dữ liệu

- `V114_AUDIT/V114_1650_MATH_VERIFIED_PENDING_REVIEW.jsonl`: đề bài, đáp án, lời giải, thông tin kiểm định và trạng thái chờ duyệt.
- `V114_AUDIT/V114_CANDIDATE_METHODS.jsonl`: 165 blueprint và nhóm khái niệm có thể trùng nhau.
- `V114_AUDIT/V114_150_TOPIC_COVERAGE.csv`: bảng đếm theo từng chủ đề.
- `V114_AUDIT/V114_REPORT.json`: số liệu đã kiểm tra.

## Đăng ký ứng viên với Question Factory

Mở PowerShell trong thư mục `MATH_WEB_GITHUB_READY/backend`:

```powershell
python -m pip install -r requirements-question-factory.txt
python -m question_factory.cli --db database/qf_v114.sqlite3 init
python -m question_factory.cli --db database/qf_v114.sqlite3 seed-curated
python -m question_factory.cli --db database/qf_v114.sqlite3 seed-v114
python -m question_factory.cli --db database/qf_v114.sqlite3 status
```

Các lệnh này sẽ đăng ký 165 blueprint trong trạng thái `pending`; **không sinh hay công bố câu hỏi trong game**. Muốn nhập từng blueprint vào ngân hàng hoạt động, phải đối chiếu phương pháp với ngân hàng cũ, kiểm chứng bài giải, làm rõ chương trình học và duyệt có danh tính; lệnh `approve-type` hiện có chỉ phù hợp quy trình thử nghiệm nội bộ, không phải giấy chứng nhận độc lập.

Nếu cần kiểm thử:

```powershell
python -m pytest -q tests/test_question_factory_v114.py
```

Để chạy lại kiểm toán trên dữ liệu gốc:

```powershell
$env:PYTHONPATH='.'
python -m question_factory.v114_audit --out-dir ../V114_AUDIT --legacy app/ai/verified_seed/verified_seed_bank.jsonl
```

## Giới hạn cần lưu ý

- Không có 300.000 phương pháp giải độc lập đã được chứng nhận.
- Không có 3.000.000 câu đã kiểm định; ngân hàng cũ có 344.280 bản ghi **chưa được chứng nhận hoàn toàn**.
- V114 kiểm tra đáp án số và biểu thức, chưa kiểm định hình vẽ/ngôn ngữ/sư phạm cho từng câu hay đảm bảo độc lập toán học giữa các blueprint.
- SQLite phù hợp kiểm thử/máy đơn. Để xử lý lớn đa máy cần PostgreSQL + hàng đợi tác vụ có lease + giám sát chi phí; cấu hình cloud luôn bật chưa được triển khai.
