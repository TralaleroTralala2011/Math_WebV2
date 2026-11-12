@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "BANK_DB=%~1"
if not defined BANK_DB set "BANK_DB=backend\database\mathweb.db"
if not exist "%BANK_DB%" (
  echo [KHONG TIM THAY DB] %BANK_DB%
  echo Goi lai: IMPORT_BANK_V191.bat "C:\duong-dan\mathweb.db"
  exit /b 1
)
echo === MATH_WEB V191: CHI KIEM TRA TRUOC, CHUA GHI ===
python backend\scripts\import_bank_updates.py --db "%BANK_DB%" --input bank_updates\V191_CUMULATIVE_QA_IMPORT.jsonl
if errorlevel 1 exit /b 1
set /p "ANSWER=De sao luu va nhap cac cau hop le, go NHAP roi Enter (khac thi huy): "
if /i not "%ANSWER%"=="NHAP" (
  echo Da huy. Khong thay doi DB.
  exit /b 0
)
if not exist backups mkdir backups
set "BACKUP=backups\mathweb-before-v191-%RANDOM%-%RANDOM%.sqlite"
python backend\scripts\import_bank_updates.py --db "%BANK_DB%" --input bank_updates\V191_CUMULATIVE_QA_IMPORT.jsonl --write --backup "%BACKUP%"
if errorlevel 1 (
  echo NHAP THAT BAI. Kiem tra log va ban backup.
  exit /b 1
)
echo HOAN TAT. Backup: %BACKUP%
exit /b 0
