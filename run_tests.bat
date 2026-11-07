@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Create the environment first with run.bat, or run: python -m venv .venv
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pytest -q
if errorlevel 1 exit /b 1
where node >nul 2>nul
if not errorlevel 1 node --check app\static\app.js
