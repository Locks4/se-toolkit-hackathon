@echo off
setlocal enabledelayedexpansion

title Goal Tracker - Starting...
color 0A

echo.
echo ========================================
echo   Goal Tracker App - Starting
echo ========================================
echo.
echo This window will stay open and show you what's happening.
echo.
echo Step 1/4: Checking Python...
timeout /t 1 /nobreak >nul

python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [FAIL] Python is not found!
    echo.
    echo Please run: setup.bat
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Python found!
python --version
echo.

echo Step 2/4: Checking Node.js...
timeout /t 1 /nobreak >nul

node --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [FAIL] Node.js is not found!
    echo.
    echo Please run: setup.bat
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Node.js found!
node --version
echo.

echo Step 3/4: Starting Backend...
timeout /t 1 /nobreak >nul

:: Kill old backend if running
taskkill /F /IM python.exe 2>nul >nul
timeout /t 1 /nobreak >nul

echo Starting backend in a new window...
start "Goal Tracker Backend (Port 8000)" cmd /k "cd /d %~dp0backend && color 0B && echo. && echo ============================================ && echo   BACKEND SERVER - Keep this window open! && echo ============================================ && echo. && python main.py"

echo Waiting 8 seconds for backend to start...
for /L %%i in (8,-1,1) do (
    <nul set /p "=%%i... "
    timeout /t 1 /nobreak >nul
)
echo.
echo.

:: Test backend
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running on http://localhost:8000
) else (
    color 0E
    echo [WARN] Backend may not be responding. Check the Backend window for errors.
)
echo.

echo Step 4/4: Starting Frontend...
timeout /t 1 /nobreak >nul

:: Kill old frontend if running
taskkill /F /IM node.exe 2>nul >nul

echo Starting frontend in a new window...
start "Goal Tracker Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend && color 0A && echo. && echo ============================================ && echo   FRONTEND SERVER - Keep this window open! && echo ============================================ && echo. && npm start"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Two new windows should have opened:
echo   1. Backend Server (blue window)
echo   2. Frontend Server (green window)
echo.
echo The browser will open automatically to:
echo   http://localhost:3000
echo.
echo If the browser doesn't open, wait a moment
echo then visit: http://localhost:3000
echo.
echo ========================================
echo.
echo You can close this window. Keep the other two open!
echo.
pause
