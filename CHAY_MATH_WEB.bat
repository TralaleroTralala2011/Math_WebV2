@echo off
setlocal
title MATH WEB - Launcher
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Khong tim thay Python. Hay cai Python va chon Add Python to PATH.
  pause
  exit /b 1
)
echo Dang khoi dong MATH WEB...
start "MATH WEB Backend" "%~dp0CHAY_BACKEND.bat"
start "MATH WEB Website" "%~dp0CHAY_WEBSITE.bat"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5500/"
echo.
echo Trang chu: http://127.0.0.1:5500/
echo API:      http://127.0.0.1:8000/docs
echo Giu ca hai cua so server mo trong luc su dung.
