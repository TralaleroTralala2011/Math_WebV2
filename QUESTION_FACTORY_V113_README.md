# MATH_WEB V113: ngân hàng câu hỏi, kiểm định và chống đếm trùng dạng

## Trạng thái kỹ thuật ngày 08/11/2026

- Mục tiêu **150 chủ đề × 2.000 dạng độc lập × 10 câu = 3.000.000 câu**: **CHƯA ĐẠT**. Không có cách đúng đắn để tuyên bố hoàn tất bằng cách đổi số, ID, hoặc diễn đạt.
- Bản V112 có danh mục 150 chủ đề; ngân hàng legacy 344.280 câu. V113 không sửa, ghi đè, xóa nội dung ngân hàng legacy, tài khoản hay giao diện cũ.
- V113 thêm **60 blueprint toán học được lập trình tường minh**, với 600 câu mẫu đã được SymPy kiểm lại đáp án. 60 blueprint liên quan **55 chủ đề**; 54 nhóm khái niệm sau khi gộp những nhóm gần nhau theo bộ cảnh báo, **không phải** 54 dạng độc lập được chứng nhận.
- Dữ liệu mới mặc định **pending-expert-review**, không tự nhập vào trò chơi đang hoạt động và không tự đánh dấu đã hoàn thành mục tiêu 300.000 phương pháp.
- Kiểm kê 344.280 dòng nguồn: 11.464 chữ ký nguyên bản nhưng chỉ **1.691 nhóm chữ ký** sau khi chuẩn hóa số trong tên; vẫn chưa thể coi 1.691 là phương pháp độc lập. 39.140 dòng nằm trong các chữ ký tự mô tả là biến thể hoặc dùng lại cách giải.
- 11.464 candidate cards được xuất để thẩm định tại `V113_AUDIT/V113_SOURCE_FORM_CANDIDATES.jsonl`, kèm priority. Đây **không phải** 11.464 dạng được cấp chứng nhận.

## Tệp mới

| Đường dẫn | Nội dung |
|---|---|
| `backend/question_factory/expanded_catalog.py` | 60 blueprint, 54 nhóm cảnh báo khái niệm |
| `backend/question_factory/expanded_engine.py` | 600 phép sinh câu cùng phép tính lại đáp án bằng SymPy |
| `backend/question_factory/export_curated.py` | Xuất 600 câu mẫu, chứng cứ kiểm định và fingerprint |
| `backend/question_factory/audit_corpus.py` | Kiểm toán streaming toàn bộ ngân hàng cũ, nhóm biến thể |
| `backend/question_factory/grading.py` | Chấm phân số, π, căn thức bằng AST an toàn; không eval/sympify dữ liệu người dùng |
| `V113_AUDIT/V113_CORPUS_AUDIT.json` | Kiểm toán đầy đủ + danh sách 150 chủ đề |
| `V113_AUDIT/V113_COVERAGE_150.json` | Khoảng trống mục tiêu 2000/20.000 của từng chủ đề (chỉ số chứng nhận) |
| `V113_AUDIT/V113_SOURCE_FORM_CANDIDATES.jsonl` | 11.464 nhóm chữ ký gốc chưa duyệt, mẫu, score, cảnh báo |
| `V113_AUDIT/V113_CURATED_600.jsonl` | 600 câu mới có đáp án, giải thích, params và kết quả kiểm định |
| `V113_AUDIT/V113_CURATED_SUMMARY.json` | Phân nhóm blueprint và số liệu trạng thái |
| `backend/tests/test_question_factory_v113.py` | Các kiểm thử giới hạn, tương đương toán, tránh phát hành khi chưa duyệt |

## Hướng dẫn chạy trên Windows, không cần GitHub

Giải nén, mở Command Prompt hoặc PowerShell trong `MATH_WEB_GITHUB_READY/backend`, cài Python 3.11+ và phụ thuộc:

```powershell
python -m pip install -r requirements-question-factory.txt
python -m question_factory.cli --db database/qf_v113.sqlite3 init
python -m question_factory.cli --db database/qf_v113.sqlite3 seed-curated
python -m question_factory.cli --db database/qf_v113.sqlite3 status
```

Câu hỏi ở trạng thái chờ duyệt, nên `verified_questions = 0` nếu chưa có những dạng được duyệt. Để kiểm tra một dạng, xem 10 câu trong `V113_AUDIT/V113_CURATED_600.jsonl` tương ứng với `family`, xác nhận phương pháp giải thật sự đúng chủ đề và khác các dạng đã có. Sau khi có người duyệt:

```powershell
python -m question_factory.cli --db database/qf_v113.sqlite3 approve-type v113-circle_area --reviewer "reviewer-name"
python -m question_factory.cli --db database/qf_v113.sqlite3 enqueue --per-type 10
python -m question_factory.cli --db database/qf_v113.sqlite3 run --workers 4
python -m question_factory.cli --db database/qf_v113.sqlite3 status
```

Thao tác trên dùng **cơ sở dữ liệu thử nghiệm mới** và không thay SQLite tài khoản MATH_WEB. Để vận hành worker liên tục trên **máy chủ đã triển khai** mới sử dụng lệnh `daemon`; một phiên trò chuyện ChatGPT không thể thay máy chủ chạy 24/7. Trước khi dùng production cần backup, secrets, giám sát và kiểm thử tải.

## Quy tắc chống thổi phồng số dạng

1. Mỗi dạng cần mô tả **mục tiêu giải, phép biến đổi quyết định, miền dữ liệu, các bước giải và ngoại lệ**.
2. Nếu chỉ đổi hệ số, đổi tên biến, đổi tên bài, đổi ID hoặc đổi cách diễn đạt, **không cấp mã dạng độc lập**.
3. Mọi chữ ký số như `V41 / family 5 / variant 25` phải qua bước gom nhóm, sau đó đánh giá ngữ nghĩa bởi người có chuyên môn.
4. Câu hỏi phải có kiểm định toán học độc lập; kiểm định đáp án số không thay thế kiểm định lời giải, hình vẽ, distractor hoặc hướng dẫn sư phạm.
5. Chỉ dữ liệu từ những dạng đã xét duyệt và vượt kiểm định mới được công bố qua API; lỗi, dữ liệu cũ chưa đủ chứng cứ và ứng viên mới ở vùng cách ly.

## Giới hạn còn lại

Chưa có 300.000 dạng độc lập; chưa có 3.000.000 câu mới đã kiểm định; chưa có generator cho mọi chủ đề; chưa có thẩm định sư phạm toàn bộ legacy. Không tuyên bố deployment 24/7, kiểm thử production, hay chuyên gia đã duyệt 60 blueprint. Hệ thống chỉ có thể tiến đến mục tiêu khi mở rộng theo chương trình kiến thức và kiểm định thật, không sinh ID giả.
