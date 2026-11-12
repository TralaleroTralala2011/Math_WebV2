@echo off
setlocal
rem Optional LAN mode. Do not run on public or untrusted networks.
set "MATHWEB_LAN=1"
call "%~dp0START_MATH_WEB.bat"
endlocal
