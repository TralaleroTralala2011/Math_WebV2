@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title MATH_WEB - Full local launcher
if not exist "index.html" (echo [ERROR] Missing index.html & pause & exit /b 1)
if not exist "backend\app\main.py" (echo [ERROR] Missing backend app & pause & exit /b 1)
rem By default services are reachable only on this computer.
rem Set MATHWEB_LAN=1 (or use START_MATH_WEB_LAN.bat) to enable Wi-Fi access.
set "BIND_HOST=127.0.0.1"
if /I "%MATHWEB_LAN%"=="1" set "BIND_HOST=0.0.0.0"
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=%CD%\.venv\Scripts\python.exe"
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (echo [ERROR] Python not available & pause & exit /b 1)
"%PYTHON%" -c "import fastapi,uvicorn,pydantic,sympy" >nul 2>&1
if errorlevel 1 (
 echo Installing backend dependencies...
 "%PYTHON%" -m pip install -r "backend\requirements.txt"
 if errorlevel 1 (echo [ERROR] Dependency install failed & pause & exit /b 1)
)
"%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/openapi.json',timeout=2)" >nul 2>&1
if errorlevel 1 (
 echo Starting backend and admin API on 127.0.0.1:8000...
 start "MATH_WEB Backend" cmd /k "cd /d ""%~dp0backend"" && ""%PYTHON%"" -m uvicorn app.main:app --host %BIND_HOST% --port 8000"
) else (echo Backend already available.)
"%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5500/index.html',timeout=2)" >nul 2>&1
if errorlevel 1 (
 echo Starting frontend on 127.0.0.1:5500...
 start "MATH_WEB Frontend" cmd /k "cd /d ""%~dp0"" && ""%PYTHON%"" ""scripts\serve_frontend.py"" 5500 --bind %BIND_HOST%"
) else (echo Frontend already available.)
if /I "%MATHWEB_LAN%"=="1" echo LAN mode: Allow Python through your Windows firewall on a TRUSTED Wi-Fi network only.
if /I "%MATHWEB_LAN%"=="1" echo If local-only servers are already running, close them and restart using LAN mode.
echo Waiting for backend and frontend...
"%PYTHON%" "scripts\wait_and_open.py"
if errorlevel 1 (echo [ERROR] Server startup failed. Check server windows. & pause & exit /b 1)
echo Website: http://127.0.0.1:5500/index.html
echo Admin:   http://127.0.0.1:5500/admin.html
echo API:     http://127.0.0.1:8000/docs
echo Close the server windows to stop the website.
pause
