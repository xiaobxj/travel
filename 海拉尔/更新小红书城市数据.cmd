@echo off
setlocal
cd /d "%~dp0"
python -X utf8 "%~dp0collect_city_xhs.py" --rebuild
pause
endlocal
