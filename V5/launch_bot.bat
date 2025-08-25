@echo off
echo =================================================
echo    Pump.fun Trading Bot Launcher
echo =================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo ✅ pip is available
echo.

:: Install required packages
echo 📦 Installing required packages...
pip install streamlit pandas requests

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo ✅ All packages installed successfully
echo.

:: Check if pump_bot.py exists
if not exist "pump_bot.py" (
    echo ERROR: pump_bot.py file not found in current directory
    echo Please make sure pump_bot.py is in the same folder as this launcher
    pause
    exit /b 1
)

echo ✅ pump_bot.py found
echo.

:: Launch the bot
echo 🚀 Launching Pump.fun Trading Bot...
echo.
echo The bot will open in your default web browser
echo Close this window to stop the bot
echo.

streamlit run pump_bot.py --server.headless false --server.port 8501

pause