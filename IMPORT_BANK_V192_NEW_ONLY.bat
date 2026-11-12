@echo off
setlocal
cd /d "%~dp0"
set "DB=%~1"
if "%DB%"=="" set "DB=backend\database\mathweb.db"
echo MATH_WEB V192: XEM TRUOC NHAP 1.500 CAU MOI (KHONG GHI).
python backend\scripts\import_bank_updates.py --db "%DB%" --input "bank_updates\V192_IMPORT_READY.jsonl"
if errorlevel 1 (
 echo Co loi kiem tra. KHONG NHAP.
 exit /b 1
)
echo.
echo Chi tiep tuc khi server dang dung DB nay da DUNG, du lieu da duoc sao luu can thiet.
set /p ANSWER=Nhap NHAP de sao luu moi va ghi, nhan Enter de huy: 
if /i not "%ANSWER%"=="NHAP" (
 echo Da huy. DB KHONG DOI.
 exit /b 0
)
set "BACKUP=backups\mathweb-before-v192-%RANDOM%-%RANDOM%.sqlite"
python backend\scripts\import_bank_updates.py --db "%DB%" --input "bank_updates\V192_IMPORT_READY.jsonl" --write --backup "%BACKUP%"
if errorlevel 1 (
 echo LOI NHAP. Hay kiem tra va giu nguyen du lieu sao luu.
 exit /b 1
)
echo Da hoan tat. Kiem tra ban ghi va mo website de thu truy xuat.
endlocal
