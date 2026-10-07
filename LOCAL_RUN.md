# MATH WEB - Chạy local

## 1. Backend
Mở PowerShell:

```powershell
cd "C:\Users\Duc Nhan\Downloads\MATH_WEB_COMPLETE\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 2. Frontend
Mở PowerShell thứ hai:

```powershell
cd "C:\Users\Duc Nhan\Downloads\MATH_WEB_COMPLETE"
python -m http.server 5500
```

Mở: http://127.0.0.1:5500/

Không cần tạo thư mục MATH_GAME.
