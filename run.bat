@echo off
title OmniDL Pro Launcher
cd /d "%~dp0"
echo Starting OmniDL Pro...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)
