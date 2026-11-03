@echo off
setlocal
cd /d "%~dp0"
title MATH_WEB Launcher

 echo ========================================
 echo           MATH_WEB STARTER
 echo ========================================
 echo.

if not exist "index.html" (
  echo [ERROR] Khong tim thay index.html.
  echo Hay chay file nay trong thu muc goc MATH_WEB.
  pause
  exit /b 1
)
if not exist "backend\app\main.py" (
  echo [ERROR] Khong tim thay backend\app\main.py.
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Khong tim thay Python. Cai Python 3 va chon Add Python to PATH.
  pause
  exit /b 1
)

echo [1/3] Cai/kiem tra thu vien Backend...
python -m pip install -r "backend\requirements.txt"
if errorlevel 1 (
  echo [ERROR] Cai thu vien that bai. Kiem tra ket noi mang va Python.
  pause
  exit /b 1
)

echo.
echo [2/3] Khoi dong Backend tai cong 8000...
start "MATH_WEB Backend" cmd /k "cd /d ""%~dp0backend"" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [3/3] Khoi dong Website tai cong 5500...
start "MATH_WEB Website" cmd /k "cd /d ""%~dp0"" && python -m http.server 5500"

timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:5500/index.html"

echo.
echo Website: http://127.0.0.1:5500/index.html
echo API:     http://127.0.0.1:8000/docs
echo Giu hai cua so Backend va Website mo khi su dung.
echo Neu cong 5500 hoac 8000 dang duoc dung, dong server cu truoc.
echo.
pause
