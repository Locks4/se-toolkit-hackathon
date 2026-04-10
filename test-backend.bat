@echo off
echo ========================================
echo  Testing Backend Registration
echo ========================================
echo.

:: Kill any existing backend
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

:: Start backend in background
echo Starting backend server...
start "Backend Test" /MIN cmd /k "cd backend && python main.py"

:: Wait for server to start
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Test registration
echo.
echo Testing registration endpoint...
echo.

curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"testuser@test.com\",\"password\":\"password123\",\"name\":\"Test User\"}"

echo.
echo.
echo Test complete!
echo.
echo If you saw a JSON response with user data, registration is working!
echo If you saw an error, check the Backend Test window for error details.
echo.
pause

:: Cleanup
taskkill /F /FI "WINDOWTITLE eq Backend Test" 2>nul
