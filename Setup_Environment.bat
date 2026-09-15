@echo off
title Smart Gate System - Automated Setup
cls

:: Blue color for setup
color 0B
echo ======================================================
echo    SYSTEM SETUP: IMAGE ANALYSIS AND PROCESSING 2
echo ======================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python 3.10+ and try again.
    pause
    exit
)

:: 2. Create Virtual Environment
echo [1/3] Creating Virtual Environment (venv)...
if exist venv (
    echo [INFO] venv already exists, skipping creation.
) else (
    python -m venv venv
)

:: 3. Activate and Install Requirements
echo [2/3] Activating environment and installing dependencies...
echo [INFO] This may take a few minutes (Downloading ~100MB)...
echo.

call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Installation failed! Check your internet connection.
    pause
    exit
)

:: 4. Success Message
color 0A
echo.
echo ======================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ======================================================
echo [STATUS] You can now run the project using:
echo          - Run_with_Venv.bat
echo ======================================================
echo.
pause