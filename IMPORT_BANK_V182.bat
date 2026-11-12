@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "DB=%MATHWEB_DB_PATH%"
if not defined DB set "DB=backend\database\mathweb.db"
if not exist "%DB%" (
  echo [ERROR] Khong tim thay SQLite hien co: %DB%
  echo Hay dat MATHWEB_DB_PATH toi dung mathweb.db cua ban. Khong tu tao DB moi.
  pause
  exit /b 1
)
echo.
echo === MATH_WEB V182 - XEM TRUOC, KHONG GHI DU LIEU ===
python backend\scripts\import_bank_updates.py --db "%DB%" --input bank_updates\V181_IMPORT_READY.jsonl
if errorlevel 1 goto error
python backend\scripts\import_bank_updates.py --db "%DB%" --input bank_updates\V182_IMPORT_READY.jsonl
if errorlevel 1 goto error
python backend\scripts\bank_coverage_v182.py --db "%DB%"
if errorlevel 1 goto error
echo.
echo DUNG BACKEND truoc khi nhap. Ban sao luu se duoc tao rieng cho moi dot.
choice /C YN /M "Xac nhan da dung backend va muon NHAP V181 + V182 vao DB nay"
if errorlevel 2 exit /b 0
if not exist "backups" mkdir "backups"
set "B1=backups\before_v181_%RANDOM%_%RANDOM%.sqlite"
set "B2=backups\before_v182_%RANDOM%_%RANDOM%.sqlite"
python backend\scripts\import_bank_updates.py --db "%DB%" --input bank_updates\V181_IMPORT_READY.jsonl --write --backup "%B1%"
if errorlevel 1 goto error
python backend\scripts\import_bank_updates.py --db "%DB%" --input bank_updates\V182_IMPORT_READY.jsonl --write --backup "%B2%"
if errorlevel 1 goto error
python backend\scripts\bank_coverage_v182.py --db "%DB%" --output "backups\V182_COVERAGE_AFTER_IMPORT.json"
if errorlevel 1 goto error
echo.
echo Hoan tat. Kiem tra ket qua o backups\V182_COVERAGE_AFTER_IMPORT.json
pause
exit /b 0
:error
echo [ERROR] Nhap khong thanh cong. Kiem tra log va cac ban sao luu.
pause
exit /b 1
