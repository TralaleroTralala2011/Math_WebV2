# MATH_WEB V45: Khôi phục quyền truy cập Admin an toàn

- Tên tài khoản Admin cố định: `admin19022011`.
- Mật khẩu **không** được ghi vào ZIP hoặc GitHub. Mật khẩu được đặt trực tiếp trên Render qua biến bí mật `MATHWEB_ADMIN_RESET_PASSWORD`.
- Trường hợp Admin chưa tồn tại: đặt `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` trên Render trước khi triển khai lần đầu.
- Trường hợp Admin **đã tồn tại** (đăng nhập báo sai mật khẩu): đặt `MATHWEB_ADMIN_RESET_PASSWORD` trên Render Environment bằng mật khẩu mới, lưu thay đổi, rồi mở Render Shell của **đúng service và ổ dữ liệu** và chạy:

```bash
PYTHONPATH=backend python backend/scripts/reset_admin_password.py
```

- Lệnh này đặt lại mật khẩu của Admin hiện tại, không xóa học sinh/ngân hàng, ghi audit và thu hồi token Admin cũ. Xóa biến `MATHWEB_ADMIN_RESET_PASSWORD` khỏi Render sau khi hoàn tất, tránh giữ bí mật không cần thiết.
- Đảm bảo Render sử dụng đúng `MATHWEB_DB_PATH`/ổ đĩa chứa tài khoản hiện tại. Nếu dùng SQLite tạm, cập nhật mã nguồn không thể sửa mật khẩu trong DB đã mất.
- Đăng nhập qua `login.html`, sau đó truy cập `admin.html`. Nếu chỉ cập nhật frontend GitHub Pages mà không chạy lệnh trên backend, mật khẩu trong Render không thay đổi.
- Render Shell có thể không khả dụng ở một số gói. Không chạy script trên máy tính cá nhân nếu cần thay đổi DB trên Render.
- Kiểm thử trên SQLite tạm: đổi mật khẩu thành công, mật khẩu cũ không còn hợp lệ, `auth_version` tăng.
