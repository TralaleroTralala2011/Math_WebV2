# V39: Lưu trạng thái đăng nhập sau khi tắt máy
- Frontend đã dùng localStorage cho token và hồ sơ: đóng trình duyệt, khởi động lại máy không tự xóa đăng nhập.
- Tăng thời hạn phiên được ký từ 7 lên 30 ngày để hạn chế đăng nhập lại.
- Đăng xuất vẫn xóa thông tin trong trình duyệt và gửi yêu cầu thu hồi phiên đến backend.
- Bảo mật: token vẫn hết hạn sau 30 ngày, có thể bị thu hồi khi đăng xuất, thay đổi bảo mật hoặc mất khóa ký.
- Cần triển khai backend Render V39 để thay đổi thời hạn có hiệu lực. Các token cũ vẫn giữ hạn 7 ngày.
- Không bảo đảm lưu đăng nhập nếu người dùng xóa dữ liệu trình duyệt, dùng ẩn danh, hoặc chuyển thiết bị.
