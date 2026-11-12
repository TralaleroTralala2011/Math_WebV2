@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
title MATH_WEB - AI Worker (local)
cd /d "%~dp0"

rem ===== SETTINGS =====
rem Maximum AI turns per launch. Set to 0 for unlimited (may incur API charges).
set "MAX_RUNS=10"
rem Seconds between turns.
set "WAIT_SECONDS=30"
rem Branch for AI edits, never auto-push to remote.
set "WORK_BRANCH=ai-mathweb-worker"
rem ====================

if not exist ".git" (
  echo [ERROR] Place this BAT in the root of the MATH_WEB Git repository.
  pause
  exit /b 1
)
where git >nul 2>&1 || (echo [ERROR] Git is not installed or not in PATH. & pause & exit /b 1)
where codex >nul 2>&1 || (echo [ERROR] Codex CLI is not installed or not in PATH. & echo Install and sign in to Codex CLI first. & pause & exit /b 1)

rem Do not start if there are local edits; this protects user work.
for /f "delims=" %%G in ('git status --porcelain 2^>nul') do set "DIRTY=1"
if defined DIRTY (
  echo [STOP] Uncommitted changes detected. Commit or stash them first.
  git status --short
  pause
  exit /b 1
)

rem Never silently switch an existing user's branch.
for /f "delims=" %%G in ('git branch --show-current') do set "CURRENT_BRANCH=%%G"
if /I not "!CURRENT_BRANCH!"=="%WORK_BRANCH%" (
  git show-ref --verify --quiet "refs/heads/%WORK_BRANCH%"
  if not errorlevel 1 (
    echo [STOP] Worker branch already exists. Switch manually after checking it:
    echo git switch %WORK_BRANCH%
    pause
    exit /b 1
  )
  git switch -c "%WORK_BRANCH%" || (echo [ERROR] Could not create branch. & pause & exit /b 1)
)

if not exist "worker_logs" mkdir "worker_logs"
if not exist "MATHWEB_WORKER_GOAL.md" (
  > "MATHWEB_WORKER_GOAL.md" echo # MATH_WEB autonomous development goal
  >> "MATHWEB_WORKER_GOAL.md" echo Work on this repository only. Preserve existing features and user data.
  >> "MATHWEB_WORKER_GOAL.md" echo Target: 150 topics, 2000 genuinely distinct math problem types per topic, 10 distinct questions with validated answers and explanations per type.
  >> "MATHWEB_WORKER_GOAL.md" echo Do not count renumbered or parameter-only variants as new types. Never claim completion without independent validation.
  >> "MATHWEB_WORKER_GOAL.md" echo Prioritize reproducible tests, deduplication, mathematical correctness, and fixing broken battle/admin/auth features.
  >> "MATHWEB_WORKER_GOAL.md" echo Keep a checkpoint in MATHWEB_WORKER_STATUS.md after each turn. Do not access secrets, deploy, push, delete user data, or modify files outside the repository.
)

set /a RUN=0
:LOOP
set /a RUN+=1
if not "%MAX_RUNS%"=="0" if !RUN! GTR %MAX_RUNS% goto DONE

echo.
echo ===== AI TURN !RUN! / %MAX_RUNS% =====
rem Store logs outside tracked changes (add worker_logs/ to .gitignore yourself).
set "LOGFILE=worker_logs\turn_!RUN!.log"
set "PROMPT=Read MATHWEB_WORKER_GOAL.md and MATHWEB_WORKER_STATUS.md if present. Inspect the repository, implement one useful verified increment, run available relevant tests, and update MATHWEB_WORKER_STATUS.md with real results, blockers, and the next step. Do not invent results. Work only in this repository. Do not push, deploy, or access secrets."

rem Codex CLI must already be authenticated. This command may consume paid usage.
codex exec --full-auto "%PROMPT%" > "!LOGFILE!" 2>&1
set "RC=!errorlevel!"
type "!LOGFILE!"
if not "!RC!"=="0" (
  echo [STOP] Codex failed with exit code !RC!. Check !LOGFILE!
  goto DONE
)

rem Stop on explicit completion marker, only if the agent's validation supports it.
if exist "MATHWEB_WORKER_STATUS.md" (
  findstr /C:"VERIFIED_COMPLETE: YES" "MATHWEB_WORKER_STATUS.md" >nul 2>&1
  if not errorlevel 1 (
    echo [NOTICE] Agent reported verified completion. Manually review evidence before trusting it.
    goto DONE
  )
)

rem Commit only the worker's changes, excluding logs. No remote push.
git add -A -- . ":(exclude)worker_logs" ":(exclude)worker_logs/**" ":(exclude)*.env" ":(exclude)*.env.*" >nul 2>&1
if errorlevel 1 (
  echo [STOP] Git staging failed.
  goto DONE
)
git diff --cached --quiet
if errorlevel 1 (
  git -c user.name="MATH_WEB Local Worker" -c user.email="mathweb-worker@localhost" commit -m "AI worker checkpoint !RUN!" || goto DONE
)
echo [INFO] Sleeping %WAIT_SECONDS% seconds. Ctrl+C to stop.
timeout /t %WAIT_SECONDS% /nobreak >nul
goto LOOP

:DONE
echo.
echo Worker stopped. Review MATHWEB_WORKER_STATUS.md, logs, and git history.
echo No changes were pushed to GitHub automatically.
pause
endlocal
