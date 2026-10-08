# MATH WEB

Nền tảng luyện Toán bằng HTML/CSS/JavaScript + FastAPI.

## Chạy local

### Backend

```powershell
cd "C:\duong-dan-den-MATH_WEB\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

Mở PowerShell thứ hai:

```powershell
cd "C:\duong-dan-den-MATH_WEB"
python -m http.server 5500
```

Mở `http://127.0.0.1:5500/`.

## Cấu trúc

- `index.html`: trang chủ ở root, phù hợp GitHub Pages/repository.
- `practice.html`: luyện tập.
- `battle.html`: PvP.
- `account.html`: tài khoản.
- `chat.html`: chat.
- `css/`: giao diện.
- `js/`: JavaScript.
- `games/`: 45 game luyện tập.
- `backend/`: FastAPI và API AI/matchmaking.

> GitHub Pages chỉ phục vụ frontend tĩnh. Các chức năng cần FastAPI như đăng nhập, AI, matchmaking và PvP cần backend được deploy riêng, sau đó đặt `window.MATHWEB_API_BASE` về URL backend.
