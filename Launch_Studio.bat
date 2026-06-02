@echo off
title NFL Data Studio Launcher
echo ===================================================
echo           🏈 NFL DATA STUDIO LAUNCHER
echo ===================================================
echo.

:: Detect virtual environments
if exist "%~dp0venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment in .\venv...
    call "%~dp0venv\Scripts\activate.bat"
) else if exist "%~dp0.venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment in .\.venv...
    call "%~dp0.venv\Scripts\activate.bat"
) else (
    echo [WARNING] No local virtual environment found (.venv or venv).
    echo [WARNING] Proceeding with system default Python...
)

echo.
echo [INFO] Running Streamlit interface (app.py)...
streamlit run "%~dp0app.py" --server.fileWatcherType=none

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Streamlit failed to start or crashed.
    pause
)
