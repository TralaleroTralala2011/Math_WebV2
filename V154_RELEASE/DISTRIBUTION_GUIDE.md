# MATH_WEB V154 | Triển khai an toàn và lưu trữ riêng

**Có hai ZIP khác nhau:**

1. `MATH_WEB_GITHUB_READY_V154_PRIVATE_CHECKPOINT.zip`: bản tiếp nối đầy đủ, chứa **nguyên các cơ sở dữ liệu SQLite của bản V153**; chỉ giữ riêng tư. **Không upload lên GitHub, gửi công khai hoặc coi đây là DB sản xuất hiện tại.** ZIP cũ cũng có tài khoản thử, nên mọi thông tin xác thực cần được bảo vệ.
2. `MATH_WEB_GITHUB_READY_V154_GITHUB_SOURCE_ONLY.zip`: bản mã nguồn đã lọc **SQLite, dữ liệu WAL, thư mục .venv, cache và một số tệp bí mật thông dụng**. Đây chỉ là bước lọc sơ bộ; vẫn phải rà soát secrets, cấu hình, lịch sử Git và quyền chia sẻ trước khi public.

## Giữ tài khoản khi đổi phiên bản

- Không giải nén bản mã nguồn mới đè lên thư mục dữ liệu SQLite đang sử dụng.
- Dừng toàn bộ backend, Question Factory worker và các SQLite writers.
- Tạo một bản sao lưu nhất quán từ DB đang sử dụng, không dựa vào ZIP mã nguồn làm bản sao lưu sản xuất.
- Trước khi di chuyển, chạy `python backend/scripts/audit_legacy_databases.py --root .`. Mỗi cơ sở dữ liệu `mathweb.db` lịch sử có thể chứa tập tài khoản khác nhau. **Không trộn chúng bằng copy, SQL INSERT tự động, hoặc chọn bản có nhiều tài khoản nhất.**
- Nếu dữ liệu hiện dùng nằm trong `backend/database/` và bài học đang nằm riêng trong `database/study_suite.sqlite3`, có thể chạy **dry-run** trước:

```powershell
python backend/scripts/migrate_persistent_data.py --source-dir backend/database --include-file database/study_suite.sqlite3 --destination "$env:LOCALAPPDATA\MATHWEB\data" --backup-root "$env:LOCALAPPDATA\MATHWEB\backups"
```

- Sau khi kiểm tra đường dẫn, chọn bản DB sống thực sự và bảo đảm thư mục đích trống, thay lệnh cuối bằng `... --apply`. Lệnh chỉ cho phép thêm file khác tên. Nếu đã có `study_suite.sqlite3` ở nguồn chính thì phải rà soát thủ công, không được ghi đè.
- Đặt `MATHWEB_DATA_DIR` trỏ đến **cùng một đường dẫn cố định ngoài thư mục triển khai** ở tất cả lần cập nhật; `MATHWEB_DB_PATH`, `MATHWEB_AI_HISTORY_DB_PATH`, `QF_DB_PATH` nếu có sẽ ưu tiên hơn.
- Xác minh đăng nhập bằng tài khoản test và tiến độ XP học tập trên hệ thống staging (không sử dụng tài khoản thật để thử nếu chưa có bản sao lưu).
- SQLite có thể tạo tệp WAL/SHM khi đọc DB ở chế độ WAL; trình backup dùng API SQLite để lấy ảnh nhất quán và không sao chép trực tiếp file WAL sống.

## Kiểm thử

Chạy trong `backend/`:

```powershell
python scripts/run_tests_isolated.py -q tests question_factory/test_v124_quality_gate.py question_factory/test_v125_quality_gate.py question_factory/test_v127_independent_oracle.py question_factory/test_v128_method_audit.py question_factory/test_v129_integrity_gate.py
```

Công cụ sử dụng thư mục SQLite tạm để tránh ghi thử vào DB đi kèm nguồn. Không có bằng chứng E2E Battle/Admin, test tải lớn hay bảo toàn tài khoản **trên chính máy chủ sản xuất** trong V154.
