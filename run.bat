@echo off
set SCRIPT_DIR=%~dp0

:loop
python "%SCRIPT_DIR%bot.py"
goto loop
