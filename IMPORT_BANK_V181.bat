@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=%CD%\.venv\Scripts\python.exe"
set "PYTHONPATH=%CD%\backend"
if not exist "bank_updates\V181_IMPORT_READY.jsonl" (
 echo [ERROR] Missing V181 bank data.
 pause
 exit /b 1
)
set "TARGET=backend\database\mathweb.db"
if defined MATHWEB_DATA_DIR set "TARGET=%MATHWEB_DATA_DIR%\mathweb.db"
if defined MATHWEB_DB_PATH set "TARGET=%MATHWEB_DB_PATH%"
if not exist "%TARGET%" (
 echo [ERROR] Cannot find existing MATH_WEB database: %TARGET%
 echo Start the backend once or set MATHWEB_DB_PATH to the actual SQLite file.
 pause
 exit /b 1
)
echo Bank target: %TARGET%
echo.
echo Preview only (no changes):
"%PYTHON%" backend\scripts\import_bank_updates.py --db "%TARGET%"
if errorlevel 1 (pause & exit /b 1)
echo.
echo Close the running backend before applying this update.
choice /c YN /m "Import QA-gated questions into this database with an automatic backup"
if errorlevel 2 exit /b 0
if not exist backups mkdir backups
set "BACKUP=backups\mathweb-before-v181-%RANDOM%-%RANDOM%.sqlite"
"%PYTHON%" backend\scripts\import_bank_updates.py --db "%TARGET%" --write --backup "%BACKUP%"
if errorlevel 1 (
 echo [ERROR] Import failed. Check the log. Original database was not intentionally overwritten.
 pause
 exit /b 1
)
echo Import complete. Backup: %BACKUP%
pause
