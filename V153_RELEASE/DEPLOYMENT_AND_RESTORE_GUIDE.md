# MATH_WEB V153 | Giữ tài khoản khi nâng cấp mã nguồn

**Quy tắc quan trọng:** Dừng backend, Question Factory worker và mọi tiến trình đang ghi SQLite trước khi chuyển môi trường. Không ghi đè thư mục dữ liệu đang sử dụng. Không gửi ZIP chứa cơ sở dữ liệu người dùng lên GitHub công khai.

## Windows PowerShell

Đứng tại thư mục `MATH_WEB_GITHUB_READY` đã giải nén:

```powershell
# 1) Xem trước. Không sao chép hay sửa dữ liệu.
python backend/scripts/migrate_persistent_data.py --source-dir backend/database --destination "$env:LOCALAPPDATA\MATHWEB\data" --backup-root "$env:LOCALAPPDATA\MATHWEB\backups"

# 2) Sau khi ĐÃ dừng các server/worker, kiểm tra thư mục đích rỗng
#    rồi mới thực hiện. Bản gốc vẫn còn trong backend/database.
python backend/scripts/migrate_persistent_data.py --source-dir backend/database --destination "$env:LOCALAPPDATA\MATHWEB\data" --backup-root "$env:LOCALAPPDATA\MATHWEB\backups" --apply

# 3) Các lần khởi động sau phải đặt biến môi trường này.
$env:MATHWEB_DATA_DIR="$env:LOCALAPPDATA\MATHWEB\data"
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Biến `MATHWEB_DB_PATH`, `MATHWEB_AI_HISTORY_DB_PATH` và `QF_DB_PATH` nếu có giá trị riêng sẽ được ưu tiên hơn `MATHWEB_DATA_DIR`; kiểm tra và gỡ giá trị cũ khi cần. Đường dẫn ngoài cần duy trì **giống nhau qua mọi phiên bản**; đừng đặt thư mục dữ liệu trong thư mục ZIP giải nén mới.

## Khôi phục vào thư mục mới (backend đã dừng)

```powershell
python backend/scripts/restore_sqlite.py --snapshot "C:\path\backups\<stamp>" --destination "C:\path\empty-new-data"
```

Tuyệt đối không khôi phục đè vào thư mục đang có tài khoản. Muốn phục hồi phiên bản cũ, đổi sang thư mục dữ liệu mới đã được khôi phục và khởi động backend từ đó. Trên Windows, công cụ xóa **chỉ** một thư mục đích đã kiểm tra rỗng ngay trước thao tác thay thế; không xóa cơ sở dữ liệu đang tồn tại.

## Phạm vi đã kiểm tra

- Các DB trong `backend/database/`: `mathweb.db`, `mathweb_ai_history.sqlite3`, `question_factory.sqlite3` và các `.db/.sqlite/.sqlite3` khác cùng thư mục.
- Các module `question_factory.bootstrap`, `question_factory.api`, `app.ai.engine.question_history` đã dùng đường dẫn chung khi không có override rõ ràng. Các DB học tập, chẩn đoán và tính năng cuối cũng lấy `database_path` của backend.
- Một số **bản sao lịch sử** của dự án ở các thư mục khác vẫn có SQLite. Công cụ migration **không** tự động trộn hoặc ghi đè chúng, vì không thể xác minh bản nào là dữ liệu đang hoạt động. Phải đối chiếu riêng trước khi di chuyển.
- Không có .git history trong ZIP nguồn; không thể xác minh mã commit hoặc tình trạng file đã được Git theo dõi. `.gitignore` chỉ chặn DB mới chưa được theo dõi. Trước khi push chạy `git ls-files "*.db" "*.sqlite" "*.sqlite3"`; nếu xuất hiện database nhạy cảm đã được theo dõi, phải rà soát và ngừng push để xử lý an toàn.
- Tập test API nên được chạy bằng `python backend/scripts/run_tests_isolated.py ...` để tránh tạo tài khoản thử trong DB thực của dự án.

**Chưa xác minh:** server đang chạy trên máy thật, migration giữa các máy, khôi phục trên toàn bộ DB lịch sử, giao diện mobile, Battle/Admin end-to-end, benchmark với hàng triệu câu hỏi. Trước khi deploy thật, sao lưu ngoài máy và chạy thử trên bản sao đầy đủ của dữ liệu.
