@echo off
setlocal
title MATH WEB - Website
cd /d "%~dp0"
echo Website se chay tai http://127.0.0.1:5500
python "scripts\serve_frontend.py" 5500
echo.
echo Website server da dung.
pause
