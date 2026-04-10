# 🚀 Installation Guide

## Automatic Installation (Recommended)

**Just double-click `setup.bat`** - it will automatically:
1. ✅ Download and install Python if missing
2. ✅ Download and install Node.js if missing  
3. ✅ Install all project dependencies
4. ✅ Prepare everything for you

No manual installation needed!

## Manual Installation

If automatic installation doesn't work, follow these steps:

### Step 1: Install Python
1. Go to: https://www.python.org/downloads/
2. Download **Python 3.8 or higher** (latest stable recommended)
3. **IMPORTANT**: During installation, **CHECK** the box that says "Add Python to PATH"

### Step 2: Verify Installation
After installing, open a new terminal and run:
```bash
python --version
```
You should see something like: `Python 3.11.x`

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Start the App
Run the start script:
```bash
start.bat
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend (after backend is running)
cd frontend
npm start
```

## Full Prerequisites

You need BOTH of these installed:

### 1. Python 3.8+ (for backend)
- Download: https://www.python.org/downloads/
- Verify: `python --version`
- Must have pip: `pip --version`

### 2. Node.js 16+ (for frontend)
- Download: https://nodejs.org/
- Verify: `node --version`
- Must have npm: `npm --version`

## Troubleshooting

### "python is not recognized"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart your terminal after installation

### "pip is not recognized"
- Run: `python -m pip install -r requirements.txt`
- Or reinstall Python with pip option checked

### Backend starts but frontend shows errors
- Make sure you ran `npm install` in the frontend folder
- Delete `node_modules` folder and run `npm install` again

### Port 8000 already in use
- Change port in `backend/main.py` last line: `uvicorn.run(app, host="0.0.0.0", port=8001)`

## Quick Checklist

Before running the app, ensure:
- [ ] Python is installed: `python --version`
- [ ] pip is available: `pip --version`
- [ ] Node.js is installed: `node --version`
- [ ] npm is available: `npm --version`
- [ ] Backend dependencies installed: `pip install -r requirements.txt`
- [ ] Frontend dependencies installed: `npm install`
- [ ] Backend server is running (should see "Uvicorn running on...")
- [ ] Frontend server is running (should open browser automatically)

## Still Having Issues?

1. Close all terminal windows
2. Open a NEW terminal
3. Run: `start.bat`
4. Wait for both servers to start
5. Try registering again

The backend MUST be running before you can register or login!
