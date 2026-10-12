# MATH WEB UNIFIED COMPLETE • Chạy bằng VS Code

## 1. Mở dự án
Giải nén `MATH_WEB_UNIFIED_COMPLETE_100P.zip`, sau đó mở đúng thư mục `MATH_WEB_UNIFIED_COMPLETE_100P` trong VS Code.

## 2. Chạy backend
Mở Terminal thứ nhất trong VS Code:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Giữ cửa sổ terminal này chạy. Có thể kiểm tra API tại `http://127.0.0.1:8000/health`.

## 3. Chạy frontend
Mở Terminal thứ hai tại thư mục gốc dự án, không phải trong `backend`:

```powershell
python -m http.server 5500
```

Mở `http://127.0.0.1:5500/` trong trình duyệt.

## Nếu gặp `ERR_CONNECTION_REFUSED`
Backend chưa chạy hoặc không nghe ở cổng 8000. Kiểm tra terminal backend, chạy lại lệnh Uvicorn ở bước 2 và không đóng terminal đó.

## Lưu thành tích
Thành tích trò chơi được lưu bằng `localStorage` của trình duyệt trên thiết bị hiện tại. Nếu đổi trình duyệt, xóa dữ liệu trang hoặc dùng thiết bị khác thì thành tích cục bộ có thể không xuất hiện ở đó.
