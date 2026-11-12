@echo off
setlocal
cd /d "%~dp0backend"
python -m pip install -r requirements-question-factory.txt || goto :failed
python -m question_factory.cli --db database/qf_v114.sqlite3 init || goto :failed
python -m question_factory.cli --db database/qf_v114.sqlite3 seed-curated || goto :failed
python -m question_factory.cli --db database/qf_v114.sqlite3 seed-v114 || goto :failed
python -m question_factory.cli --db database/qf_v114.sqlite3 status || goto :failed
echo.
echo [OK] Da dang ky 165 bo tao o trang thai CHO DUYET, khong tu dong dua vao game.
echo Xem QUESTION_FACTORY_V114_README.md va V114_AUDIT.
pause
exit /b 0
:failed
echo [LOI] Kiem tra Python va dependencies truoc khi thu lai.
pause
exit /b 1
