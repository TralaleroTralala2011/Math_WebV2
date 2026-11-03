@echo off
setlocal
cd /d "%~dp0"
echo Open http://127.0.0.1:5500/ in your browser.
python -m http.server 5500
pause
