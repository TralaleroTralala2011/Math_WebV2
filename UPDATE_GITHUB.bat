@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo MATH WEB FINAL 100P - GITHUB UPDATE
echo ========================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0CHECK_PROJECT.ps1"
if errorlevel 1 (
  echo.
  echo PREFLIGHT FAILED. Nothing was pushed.
  pause
  exit /b 1
)

where git >nul 2>nul
if errorlevel 1 (
  echo Git was not found in PATH.
  pause
  exit /b 1
)

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo This folder is not inside a Git working tree.
  echo Extract the package into your existing Math_WebV2 Git repository first.
  pause
  exit /b 1
)

git add -A
if errorlevel 1 goto :fail

git diff --cached --quiet
if not errorlevel 1 (
  echo No changes to commit.
  git status --short
  exit /b 0
)

git commit -m "Upgrade MATH WEB AI problem generator"
if errorlevel 1 goto :fail

git push origin main
if errorlevel 1 goto :fail

echo.
echo ========================================
echo GITHUB UPDATE SUCCESSFUL
echo ========================================
pause
exit /b 0

:fail
echo.
echo GITHUB UPDATE FAILED. No further action was taken automatically.
pause
exit /b 1
