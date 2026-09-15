@echo off
chcp 65001 >nul
title Launching VoxMux Pro...
echo ====================================================
echo [*] Launching Application via Virtual Environment...
echo ====================================================

if not exist venv (
    echo [ERROR] Virtual environment (venv) not found!
    echo Please run 'Setup_Environment.bat' first to initialize the system.
    echo.
    pause
    exit /b
)

echo [*] Activating environment and starting the engine...
call venv\Scripts\activate

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application crashed or exited with an error code.
    pause
)