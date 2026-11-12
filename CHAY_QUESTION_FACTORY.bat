@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%\backend"
if not exist "backend\question_factory\cli.py" (
  echo Khong tim thay backend\question_factory\cli.py
  pause
  exit /b 1
)
echo [MATH_WEB] Cai thu vien Question Factory...
python -m pip install -r backend\requirements-question-factory.txt || goto error
echo [MATH_WEB] Khoi dong factory worker song song (dung Ctrl+C de ket thuc)...
python -m question_factory.cli daemon --workers 4 --poll 5
exit /b %errorlevel%
:error
echo [LOI] Khong cai duoc thu vien. Kiem tra Python va mang.
pause
exit /b 1
