# MATH_WEB V181 | Bắt đầu tại đây

**Đây là bản website đầy đủ đã được sửa mã nguồn, không chỉ là thư viện câu hỏi.** Mã nền là V167, bản website đầy đủ mới nhất truy cập được trong phiên này. Các checkpoint V179/V180 được giữ lại dưới dạng dữ liệu nhập V181, không ghi đè dữ liệu người dùng.

## Chạy trên Windows

1. Giải nén ZIP vào **thư mục mới**, không đè lên một bản MATH_WEB/GitHub có thể mới hơn V167.
2. Để tiếp tục sử dụng dữ liệu cũ, giữ nguyên SQLite `mathweb.db`, `question_factory.sqlite3`, lịch sử AI và `.env` trong vị trí lưu trữ hiện tại, hoặc cấu hình `MATHWEB_DATA_DIR` / `MATHWEB_DB_PATH` đúng đường dẫn. Bản ZIP không chứa cơ sở dữ liệu người dùng.
3. Chạy `START_MATH_WEB.bat` để khởi động frontend và backend. Kiểm tra `http://127.0.0.1:8000/health` và `http://127.0.0.1:5500/index.html`.
4. Dừng backend rồi chạy `IMPORT_BANK_V181.bat`. Công cụ xem trước, yêu cầu xác nhận, tạo bản sao lưu trước khi nhập. Có thể chạy lại mà không nhân đôi 3.695 câu.
5. Khởi động lại website và thử Luyện tập, bài tập được giao, Battle, Admin, tài khoản, bạn bè và tin nhắn trên máy của bạn.

**Lưu ý:** Nếu bản GitHub hiện tại của bạn đã có những thay đổi sau V167, hãy dùng `V181_CODE_DIFF.patch` và gói code-only để rà soát, gộp các sửa đổi thay vì thay toàn bộ mã bằng V167.

## Mức độ hoàn thiện

Đã chạy các nhóm kiểm thử backend (115 bài đạt), kiểm tra cú pháp JS, hình học, API và nhập SQLite cô lập. Chưa có bằng chứng đủ để công nhận **100% tất cả chức năng** trên máy thật hoặc production. Chưa có quyền truy cập database production hay xác minh commit GitHub mới nhất.

Chi tiết trong `V181_RELEASE_NOTES.md`, `V181_WEB_TEST_REPORT.json` và `bank_updates/README_V181.md`.
