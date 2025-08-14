@echo off
cd /d "%~dp0"
call .venv311\Scripts\activate
start cmd /k "python main.py"
start cmd /k "python dashboard\app.py"
