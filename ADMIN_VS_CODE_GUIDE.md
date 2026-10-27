# MATH_WEB Admin độc lập

## Chạy nhanh trên Windows
1. Giải nén toàn bộ ZIP vào một thư mục.
2. Nhấn đúp `CHAY_ADMIN_MATH_WEB.bat`.
3. Chờ hai cửa sổ server mở, sau đó trang quản trị tự mở tại `http://127.0.0.1:5500/admin.html`.
4. Đăng nhập bằng tài khoản quản trị đã được cấu hình trong backend. Mật khẩu khởi tạo mặc định hiện tại là `adminsitinh` nếu chưa đổi qua biến môi trường hoặc trong trang Admin.
5. Giữ hai cửa sổ server mở khi dùng hệ thống.

Không mở `admin.html` bằng cách nhấn đúp trực tiếp (địa chỉ `file://`). Trang phải được phục vụ qua HTTP để trình duyệt gọi API backend.

## Chạy bằng VS Code, không dùng BAT
Mở thư mục gốc dự án trong VS Code, chọn Terminal > New Terminal.

Terminal 1:
```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, tại thư mục gốc của dự án:
```powershell
py -m http.server 5500
```

Mở `http://127.0.0.1:5500/admin.html`.

## Nguyên tắc phân quyền
- Admin là trang quản trị độc lập tại `admin.html`, không phải màn hình tài khoản người học.
- API quản trị nằm dưới `/api/admin`; backend xác minh role ở mỗi request.
- Phiên Admin dùng `localStorage` key `mathweb_admin_token`, tách biệt với `mathweb_token` của người học. Đăng xuất Admin không đăng xuất tài khoản học tập.
- Chỉ tài khoản `admin19022011` có role `admin`; backend không cho API công khai cấp thêm quyền admin.
- Các chức năng quản trị chỉ thao tác được khi API backend chạy và tài khoản có quyền Admin.

## Bảo mật
Mật khẩu khởi tạo mặc định chỉ dùng cho môi trường local. Đổi mật khẩu ngay sau lần đăng nhập đầu tiên. Không đưa mật khẩu mặc định lên máy chủ công khai; cấu hình `MATHWEB_SECRET_KEY` mạnh và bật HTTPS nếu triển khai production.
