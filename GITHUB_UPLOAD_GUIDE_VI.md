# Hướng dẫn đưa MATH WEB lên GitHub (Windows)

## Trước khi tải lên

- Sao lưu thư mục dự án và cơ sở dữ liệu đang dùng.
- Không commit `backend/database/mathweb.db`, `.env`, API key, token, hoặc mật khẩu thật.
- Nếu repository là public, không để mật khẩu bootstrap Admin mặc định trong mã nguồn. Đặt `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` và `MATH_WEB_SECRET_KEY` ở môi trường backend; đổi mật khẩu Admin sau lần đăng nhập đầu tiên. Không đăng mã nguồn chứa thông tin xác thực lên public repository.
- GitHub Pages chỉ host frontend tĩnh. FastAPI, AI worker và SQLite cần backend đang chạy ở máy chủ riêng. `127.0.0.1` chỉ trỏ về máy của người truy cập, không phải máy chủ online.

## Cách A: Repository đã có sẵn

1. Tải ZIP mới, giải nén vào thư mục tạm.
2. Mở thư mục repository hiện tại, sao lưu nó trước.
3. Chép các file cập nhật từ ZIP vào repository, giữ lại `.git` của repository cũ. Không xóa `.git`.
4. Mở PowerShell trong thư mục repository và chạy:

```powershell
git status
git add -A
git diff --cached --stat
git commit -m "Upgrade MATH WEB admin and preview"
git push origin main
```

Nếu nhánh chính không tên `main`, kiểm tra bằng `git branch --show-current` và dùng đúng tên nhánh.

## Cách B: Tạo repository mới

1. Đăng nhập GitHub và tạo repository mới.
2. Chọn `Private` nếu chưa rà soát kỹ bảo mật. Không chọn thêm README nếu thư mục local đã có nội dung và README.
3. Giải nén ZIP vào thư mục dự án, mở PowerShell tại đó, chạy:

```powershell
git init
git branch -M main
git add -A
git status
git commit -m "Initial MATH WEB project"
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Thay `USERNAME/REPOSITORY` bằng đường dẫn repository thật của bạn.

## Nếu Git báo lỗi

- `git is not recognized`: cài Git for Windows rồi mở lại PowerShell.
- `remote origin already exists`: chạy `git remote -v` để kiểm tra, không thêm remote lần nữa.
- `failed to push`: kiểm tra đăng nhập GitHub, quyền repository và nhánh hiện tại.
- `nothing to commit`: không có thay đổi mới được Git nhận diện.

## Chạy sau khi cập nhật

Chạy `START_MATH_WEB.bat`, sau đó mở `http://127.0.0.1:5500/login.html`. Kiểm tra `http://127.0.0.1:8000/health`. Không chạy script push trước khi kiểm tra `git status` và chắc chắn không có file bí mật trong danh sách staged.
