@echo off
echo ========================================
echo  Goal Tracker App - Setup Script
echo ========================================
echo.

echo [Step 1/2] Installing prerequisites (if needed)...
echo This may take a few minutes on first run...
echo.

:: Run PowerShell installer script
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Prerequisites installation failed.
    echo Please check the errors above and try again.
    pause
    exit /b 1
)

echo.
echo [Step 2/2] Installing project dependencies...
echo.

:: Refresh PATH
setlocal enabledelayedexpansion
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=!PATH!;%%b"
endlocal

echo.
echo Installing Python dependencies...
cd backend

:: Add Python Scripts to PATH temporarily
for /f "delims=" %%i in ('python -c "import site; print(site.USER_BASE)" 2^>nul') do set USER_SCRIPTS=%%i\Scripts
for /f "delims=" %%i in ('python -c "import site; print(site.getsitepackages()[0])" 2^>nul') do set SITE_PACKAGES=%%i

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install backend dependencies.
    echo Trying alternative method...
    python -m pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install backend dependencies.
        pause
        exit /b 1
    )
)

cd ..

echo.
echo Installing frontend dependencies...
cd frontend

if not exist "node_modules" (
    echo This may take a while...
    call npm install
    
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install frontend dependencies.
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed.
)

cd ..

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo   Double-click: start.bat
echo.
echo Or run manually:
echo   Terminal 1: cd backend ^&^& python main.py
echo   Terminal 2: cd frontend ^&^& npm start
echo.
echo Then open: http://localhost:3000
echo ========================================
pause
