@echo off
title Smart Gate System - Virtual Environment Mode
cls

:: Green color for the header
color 0A
echo ======================================================
echo    SMART UNIVERSITY GATE SYSTEM - VIRTUAL MODE
echo ======================================================
echo.

if not exist venv (
    :: Red color for errors
    color 0C
    echo [ERROR] Folder 'venv' not found in this directory!
    echo [ACTION] Please create the virtual environment first.
    echo.
    pause
    exit
)

echo [STATUS] Activating Virtual Environment...
call venv\Scripts\activate

echo [STATUS] Starting main_app.py...
echo.
python main_app.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [CRASH] Application stopped unexpectedly.
)
pause