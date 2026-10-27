@echo off
setlocal
cd /d "%~dp0"
title MATH_WEB ADMIN - Control Center

echo ================================================
echo       MATH_WEB ADMIN CONTROL CENTER
echo ================================================
echo.

if not exist "admin.html" (
  echo [ERROR] Khong tim thay admin.html. Hay chay file nay tai thu muc goc MATH_WEB.
  pause
  exit /b 1
)
if not exist "backend\app\main.py" (
  echo [ERROR] Khong tim thay backend\app\main.py.
  pause
  exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Chua tim thay Python 3. Hay cai Python va chon Add Python to PATH.
    pause
    exit /b 1
  )
  set "PYTHON=python"
) else (
  set "PYTHON=py"
)

echo [1/3] Kiem tra thu vien backend...
%PYTHON% -m pip install -r "backend\requirements.txt"
if errorlevel 1 (
  echo [ERROR] Cai thu vien that bai. Kiem tra ket noi mang va Python.
  pause
  exit /b 1
)

echo.
echo [2/3] Khoi dong backend Admin + MathWeb tren cong 8000...
start "MATH_WEB Backend" cmd /k "cd /d ""%~dp0backend"" && %PYTHON% -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo.
echo [3/3] Khoi dong frontend tren cong 5500...
start "MATH_WEB Frontend" cmd /k "cd /d ""%~dp0"" && %PYTHON% -m http.server 5500"

echo Dang cho server khoi dong...
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:5500/admin.html"

echo.
echo ADMIN: http://127.0.0.1:5500/admin.html
echo API:   http://127.0.0.1:8000/docs
echo Hay giu hai cua so server mo trong luc su dung.
echo Admin co token rieng va khong dung chung phien dang nhap nguoi hoc.
echo.
pause
