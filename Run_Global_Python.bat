@echo off
title Smart Gate System - Global Mode
cls

:: Cyan color for the header
color 0B
echo ======================================================
echo    SMART UNIVERSITY GATE SYSTEM - GLOBAL MODE
echo ======================================================
echo.

echo [STATUS] Attempting to start the system...
python main_app.py

if %errorlevel% neq 0 (
    :: Yellow color for warnings/missing libraries
    color 0E
    echo.
    echo [WARNING] System could not start.
    echo [ACTION] Ensure libraries are installed using:
    echo          pip install -r requirements.txt
)
pause