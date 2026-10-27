# MATH WEB: đăng nhập chung, quản trị độc lập và AI ngân hàng câu hỏi

## Những thay đổi trong bản này

- Admin dùng chung `login.html` với người học. Sau khi đăng nhập, tài khoản có vai trò `admin` được chuyển đến `admin.html`; người học vẫn được chuyển đến `account.html`.
- Danh tính Admin nằm trong bảng SQLite riêng `admin_accounts`, không phải một hồ sơ học sinh trong bảng `users`.
- API quản trị dùng token có loại `admin`; token này không được chấp nhận thay token người học ở các API dữ liệu học tập.
- Nếu cơ sở dữ liệu từ bản cũ có dòng `admin19022011` trong `users`, lần khởi động đầu tiên sẽ chuyển hash mật khẩu sang `admin_accounts` và đổi tên dòng cũ thành `legacy_admin_archived_<id>` để giữ an toàn các liên kết dữ liệu cũ. Dòng lưu trữ này bị ẩn khỏi danh sách tài khoản người học.
- Trang Admin xem dữ liệu tài khoản, lịch sử làm bài, kết quả theo chủ đề, ngân hàng câu hỏi, danh mục kiến thức thật mà AI luyện tập đang sử dụng, nhật ký quản trị.
- Có thể tự nhập câu hỏi, sửa, xóa, hoặc yêu cầu AI tạo câu hỏi rồi lưu vào `admin_question_bank`. Bộ máy luyện tập đọc ngân hàng này để ưu tiên dùng câu hỏi đã được quản lý khi chủ đề, dạng câu, mức độ và trò chơi khớp.
- AI nền kiểm tra độ phủ ngân hàng và bổ sung một lô nhỏ câu hỏi theo chu kỳ 6 giờ khi backend đang chạy. Admin có thể bật/tắt hoặc chạy thủ công trong trang **AI & tác vụ nền**.

## Cách chạy

### Dùng file khởi động

1. Giải nén dự án vào thư mục riêng.
2. Chạy `START_MATH_WEB.bat` ở thư mục gốc.
3. Mở `http://127.0.0.1:5500/login.html`.
4. Đăng nhập bằng tài khoản Admin đã được cấu hình. Trong cơ sở dữ liệu mới, mặc định là `admin19022011`; mật khẩu bootstrap mặc định là `adminsitinh`.
5. Admin sẽ được chuyển tự động đến `admin.html`. Người học vẫn vào trang tài khoản như trước.

Nếu cơ sở dữ liệu đã có Admin từ bản cũ, mật khẩu hash hiện tại được giữ lại khi chuyển đổi. Nếu mật khẩu đã từng đổi, hãy dùng mật khẩu hiện tại thay vì mặc định. Đổi mật khẩu sau khi đăng nhập và không đưa bản đang chạy công khai với mật khẩu mặc định.

### Chạy bằng VS Code

Terminal 1:

```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, tại thư mục gốc dự án:

```powershell
py -m http.server 5500
```

Mở `http://127.0.0.1:5500/login.html`.

## Giới hạn quan trọng về Internet và chạy nền

Worker trong bản này là worker nền thật trong tiến trình backend, nhưng phần tạo câu hỏi sử dụng bộ máy tạo câu hỏi nội bộ của MathWeb. Nó không phải một crawler Internet không giới hạn và chưa tự đọc/copy nội dung từ các website bên ngoài. Để nghiên cứu web tự động, cần cấu hình nhà cung cấp tìm kiếm/AI, API key riêng ở biến môi trường máy chủ và danh sách nguồn được phép sử dụng. Không nhúng API key vào HTML/JavaScript hoặc ZIP công khai.

Worker chạy khi backend còn hoạt động. Đóng trình duyệt vẫn không dừng backend, nhưng đóng cửa sổ backend, tắt máy hoặc dừng tiến trình Python sẽ dừng worker. Muốn chạy cả khi máy cá nhân tắt, cần triển khai backend lên máy chủ luôn bật.

Câu hỏi do AI tạo cần được rà soát trước khi phát hành cho người học, nhất là đáp án, lời giải và hình minh họa. Worker chỉ bổ sung số lượng nhỏ mỗi chu kỳ và tránh câu trùng chính xác; nó không bảo đảm mọi câu đều hoàn hảo.

## Kiểm thử đã chạy trong môi trường xây dựng

- Python compile cho backend thành công.
- JavaScript syntax check cho `js/auth.js` và script Admin thành công.
- `tests/test_api_integration.py`: 3 bài kiểm thử qua.
- Kiểm thử tích hợp: Admin login qua `/api/auth/login`, `/api/auth/me`, `/api/admin/me`, dashboard, thư viện, tạo/sửa câu hỏi đều thành công.
- Token người học bị từ chối ở API Admin; token Admin bị từ chối ở API người học.
- Worker thủ công đã tạo thành công 2 câu trên cơ sở dữ liệu thử nghiệm.

Các kiểm thử này chạy trên cơ sở dữ liệu thử nghiệm, không phải cơ sở dữ liệu của máy người dùng.
