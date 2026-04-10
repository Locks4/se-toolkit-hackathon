@echo off
echo ========================================
echo  System Diagnostics
echo ========================================
echo.

echo 1. Checking Python...
where python 2>nul
if %errorlevel% neq 0 (
    echo    Python: NOT FOUND in PATH
) else (
    echo    Python: Found
    python --version
)
echo.

echo 2. Checking Node.js...
where node 2>nul
if %errorlevel% neq 0 (
    echo    Node.js: NOT FOUND in PATH
) else (
    echo    Node.js: Found
    node --version
    npm --version
)
echo.

echo 3. Checking Dependencies...
if exist "backend\requirements.txt" (
    echo    Backend requirements: OK
) else (
    echo    Backend requirements: MISSING
)

if exist "frontend\package.json" (
    echo    Frontend package.json: OK
) else (
    echo    Frontend package.json: MISSING
)

if exist "frontend\node_modules" (
    echo    Frontend node_modules: INSTALLED
) else (
    echo    Frontend node_modules: NOT INSTALLED
)
echo.

echo 4. Testing Backend...
cd backend
python -c "import fastapi; print('   FastAPI:', fastapi.__version__)" 2>nul
python -c "import sqlalchemy; print('   SQLAlchemy:', sqlalchemy.__version__)" 2>nul
cd ..
echo.

echo 5. Testing Frontend...
cd frontend
if exist "node_modules\.package-lock.json" (
    echo    Frontend dependencies: OK
) else (
    echo    Frontend dependencies: Need to run 'npm install'
)
cd ..
echo.

echo ========================================
echo  Recommendation:
echo ========================================
echo.
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo RUN: setup.bat  (to install Python)
) else (
    where node >nul 2>&1
    if %errorlevel% neq 0 (
        echo RUN: setup.bat  (to install Node.js)
    ) else (
        echo RUN: start.bat  (to start the app)
    )
)
echo.
pause
