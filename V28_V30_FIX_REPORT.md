# MATH_WEB V28 Classic V30: Sửa đăng nhập, chấm bài, bố cục

**Nền:** V29 NAV & BATTLE FIX (đã tích hợp ngân hàng V254 B54).

## Sửa đổi

- Sửa lỗi trắc nghiệm: truyền chỉ số đáp án có kiểu dữ liệu rõ ràng tới backend, không dùng chuỗi `"0"`, `"1"` dễ bị hiểu thành văn bản đáp án.
- Không tự chuyển hướng đăng nhập chỉ vì thấy token cũ chưa được máy chủ xác minh. Phần xác minh và thu hồi token hợp lệ vẫn do auth.js đảm nhiệm.
- Ẩn banner dùng thử trên trang chủ khi có phiên đăng nhập.
- Sửa khoảng trắng Chat và cải thiện trình bày kiến thức ở Học bài theo chủ đề, không đổi nội dung và palette.
- Giữ nguyên giao diện Battle V29, backend Battle/Chat, B54 SQLite và ma trận khảo sát 900 câu.

## Kiểm thử

- 14/14 ca test gồm chấm đáp án, chống đáp án tương đương, API được chọn: đạt.
- 8/8 ca test gồm đăng nhập lại cùng tài khoản và an ninh Battle: đạt.
- JavaScript node --check: đạt.
- SQLite B54 SHA-256 bằng bản nền, JSON khảo sát không đổi.
- Lưu ý: chưa kiểm thử hình ảnh desktop/mobile do Chromium ERR_BLOCKED_BY_ADMINISTRATOR; chưa kiểm định độc lập toàn bộ câu hỏi.

**Trường hợp không thể giải quyết bằng mã đơn thuần:** nếu dữ liệu đăng nhập thực tế biến mất giữa các bản ZIP, kiểm tra đường dẫn `%LOCALAPPDATA%\MATH_WEB\mathweb.db` trên máy Windows và đừng xóa thư mục đó khi cập nhật.
