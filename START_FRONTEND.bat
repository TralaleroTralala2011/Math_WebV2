@echo off
setlocal
cd /d "%~dp0"
echo Open http://127.0.0.1:5500/ in your browser.
python "scripts\serve_frontend.py" 5500 --bind 127.0.0.1
pause
