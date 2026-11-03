@echo off
setlocal
cd /d "%~dp0backend"
echo Installing backend dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto :fail
echo Starting MATH WEB API at http://127.0.0.1:8000
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
goto :eof
:fail
echo Backend dependency installation failed. Check Python and the network.
pause
