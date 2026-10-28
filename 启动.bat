@echo off
cd /d "%~dp0"
if not exist "data\wiki.db" goto nodb
start "" /b pythonw "src\desktop.py"
exit /b 0
:nodb
echo data\wiki.db not found. Run src\p0_extract.py, p0b_texttable.py, p1_parse.py, p2_build_db.py first.
pause
