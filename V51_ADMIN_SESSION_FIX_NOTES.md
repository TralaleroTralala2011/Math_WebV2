# MATH_WEB V51: Admin session fix

- Sửa getToken() để nhận token Admin đã lưu khi khởi động lại trình duyệt.
- getCurrentUser() cập nhật đúng các khóa profile của Admin.
- Đăng nhập Admin xóa phiên học sinh cũ; đăng nhập học sinh xóa phiên Admin cũ.
- Đăng xuất chung xóa cả hai nhóm khóa và gửi token đúng đến API logout.
- Nút đăng xuất trên admin.html cũng dọn cả hai nhóm khóa.
- Không xóa phiên chỉ vì lỗi mạng tạm thời.
- Không đổi database/backend, Battle, question bank hay giao diện.
- Kiểm tra cú pháp Node cho ba bản auth.js; kiểm tra ZIP.
- Cần thử đăng nhập thật trên Render, tắt/mở trình duyệt và logout để xác nhận end-to-end.
