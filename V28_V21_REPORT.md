# MATH_WEB V28 Classic V21 – Security & Assessment QA

## Đã chỉnh
- Loại khóa ký xác thực `.mathweb_hmac_secret` và SQLite `mathweb.db` khỏi ZIP phát hành, không xóa dữ liệu người dùng đang lưu ở máy họ.
- Giữ nguyên giao diện; ổn định thứ tự đáp án sau khi câu hỏi được vẽ lại trong cùng lượt khảo sát.
- Kiểm thử HTTP: `/backend/*` và `/scripts/*` bị chặn, trang chủ truy cập bình thường.

## Nâng cấp từ bản cũ
- **Windows:** ứng dụng lưu DB và khóa trong `%LOCALAPPDATA%\MATH_WEB` theo cơ chế hiện có, do đó không ghi đè chúng bằng ZIP.
- **Linux/macOS:** nếu đang sử dụng DB trong thư mục `backend/database/`, cần sao lưu `mathweb.db` và `.mathweb_hmac_secret` rồi khôi phục vào bản mới hoặc cấu hình `MATHWEB_DB_PATH` và `MATH_WEB_SECRET_FILE`. Không chia sẻ hai tệp này.
- Nếu đăng nhập bị hết hiệu lực khi thay khóa, người dùng cần đăng nhập lại; không xuất mật khẩu dưới dạng văn bản thô.

## Chưa xác nhận
- Nội dung 900 câu chưa qua thẩm định độc lập; Battle hai tài khoản chưa được kiểm thử bằng hai trình duyệt thật.
- Chưa kiểm thử đồ họa 20 trang trên desktop/mobile.

## Kiểm thử mở rộng
- 21/21 bài test đầu đạt; bộ mở rộng 25/26 đạt.
- Bài chưa đạt chỉ kiểm tra việc nhúng stylesheet NEON V27; không bổ sung CSS V27 vì người dùng yêu cầu **giữ giao diện V28 Classic**.
- Kiểm thử Battle WebSocket ở mức test; **chưa phải** thử hai tài khoản qua hai trình duyệt thật.
