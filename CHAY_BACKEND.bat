@echo off
setlocal
title MATH WEB - Backend
cd /d "%~dp0backend"
echo ==============================================
echo  MATH WEB BACKEND
echo ==============================================
echo Dang cai dat cac thu vien can thiet...
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
  echo.
  echo LOI: Khong cai dat duoc thu vien. Hay kiem tra Python va Internet.
  pause
  exit /b 1
)
echo.
echo Backend se chay tai http://127.0.0.1:8000
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
echo.
echo Backend da dung hoac gap loi.
pause
