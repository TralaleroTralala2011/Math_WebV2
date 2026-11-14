# MATH_WEB V53 · Thao tác cập nhật (Admin)

## Đã triển khai

- Mục **Thao tác cập nhật** trong `admin.html`, giữ nguyên các tab Admin trước đó.
- Admin nhấn nút xuất dữ liệu; trình duyệt khởi tạo tải tệp `MATH_WEB_FULL_BACKUP_....mwbackup` về máy.
- Tệp được mã hóa AES-256-GCM bằng mật khẩu sao lưu do Admin đặt, không trùng với mật khẩu đăng nhập.
- Sao lưu SQLite nhất quán bằng API `sqlite3.Connection.backup`, kể cả dữ liệu WAL.
- Toàn bộ bảng trong các cơ sở dữ liệu phía máy chủ được giữ nguyên: tài khoản, mật khẩu băm, trò chuyện, bạn bè, thông báo, Battle, điểm, lịch sử và dữ liệu học.
- Những kho được phát hiện và sao lưu: `accounts`, `study_suite`, `learning_progress`, `final_features`, `question_history`.
- Sau khi trình duyệt khởi tạo tải tệp, backend ghi thông báo `system_update` cho mọi tài khoản trong bảng người dùng và thêm nhật ký Audit.
- Khôi phục sau cập nhật: upload `.mwbackup` + mật khẩu + xác nhận gõ chữ; backend kiểm tra AES-GCM, SHA-256 từng SQLite, PRAGMA quick_check và cấu trúc bảng trước khi ghi dữ liệu; có bản sao rollback khi lỗi.
- Sau khôi phục tạo thông báo thành công, yêu cầu khởi động lại backend và đăng nhập lại.
- Không có hành động tự động xóa database cũ khi Admin chưa upload bản sao lưu.

## Thao tác

1. Đăng nhập Admin như trước, vào **Thao tác cập nhật**.
2. Đặt mật khẩu sao lưu dài ít nhất 12 ký tự. Nhấn **Tải toàn bộ dữ liệu và gửi thông báo**.
3. Kiểm tra file đã xuất hiện trong thư mục Downloads **trước** khi cập nhật GitHub/Render. Giữ mật khẩu và tệp ở nơi an toàn.
4. Sau khi cập nhật backend và frontend, vào mục đó, chọn `.mwbackup`, nhập lại mật khẩu và chấp nhận xác nhận khôi phục.
5. Khởi động lại backend và đăng nhập lại. Kiểm tra hai tài khoản, XP, bạn bè, tin nhắn, trận đấu và tiến độ học.

## Giới hạn quan trọng

- Chỉ sao lưu dữ liệu người dùng **đang được lưu trên server**. Dữ liệu khách chỉ lưu ở localStorage từng máy không nằm trong máy chủ, do đó không thể xuất toàn bộ từ Admin.
- Ngân hàng câu hỏi B56 nằm trong gói nguồn dự án, không phải dữ liệu người dùng; vẫn được bảo toàn nguyên vẹn, không bị tính vào phần sao lưu hồ sơ cá nhân.
- Nếu Render không có ổ lưu bền vững và không khôi phục lại tệp sau deploy, cơ sở dữ liệu trên máy chủ mới có thể khởi tạo lại. Không tự xóa dữ liệu trên server đang hoạt động.
- Khôi phục cần thực hiện trong giờ bảo trì với **một backend worker**, tránh các yêu cầu ghi khác chạy cùng lúc. Khởi động lại backend sau khôi phục.
- Browser có thể chặn tải tệp tự động hoặc chọn vị trí lưu; vì thế phải xác nhận tệp đã có trên máy.
- Mật khẩu bảo vệ file sao lưu KHÔNG được lưu trên máy chủ. Nếu quên mật khẩu, file không thể giải mã.
- Không được xem bảo vệ bằng tệp nén là thay thế cho sao lưu định kỳ hoặc lưu trữ database lâu dài.

## Kiểm thử

- `pytest -q backend/tests/test_admin_update_backup.py backend/tests/test_v53_b56_topic_selection.py`: **4/4 đạt**.
- Bao gồm thử API không đăng nhập bị từ chối, file bị thay đổi bị từ chối, mật khẩu sai bị từ chối, khôi phục nhiều kho DB, thông báo cho tài khoản và hai người chọn 1–3 chủ đề Battle.
- Kiểm tra cú pháp JS của Admin mới, script Battle và backend: đạt.
- Các kiểm thử cũ `test_v50*`, `test_v51*` có kỳ vọng luồng Battle đi thẳng vào PLAYING, trái với yêu cầu mới của V53 phải chờ hai người chọn chủ đề. Không sửa các bài kiểm thử lịch sử khi cập nhật Admin.
- Chưa thử bản mới thực tế trên Render/GitHub Pages của người dùng.
