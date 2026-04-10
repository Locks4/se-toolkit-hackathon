# 🔧 Troubleshooting Guide

## Issue: "Automatic download failed" or PowerShell errors

### Solution 1: Run as Administrator
1. Right-click on `setup.bat`
2. Select "Run as administrator"
3. Click "Yes" when prompted

### Solution 2: Manual Installation (If automatic fails)

**Install Python:**
1. Go to: https://www.python.org/downloads/
2. Download Python 3.12 or later
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH"
5. Click "Install Now"

**Install Node.js:**
1. Go to: https://nodejs.org/
2. Download the LTS version (left button)
3. Run the installer
4. Click "Next" through the installation

**Then run setup.bat again!**

### Solution 3: Check PowerShell Execution

If you see PowerShell errors, try this:

1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type `Y` and press Enter
4. Run `setup.bat` again

---

## Issue: "Registration failed" when using the app

**Cause:** Backend server is not running

**Solution:**
1. Make sure you ran `setup.bat` first
2. Run `start.bat` 
3. Wait until you see "Uvicorn running on..." in the backend window
4. Then try registering again

---

## Issue: Frontend won't start

**Try these:**
1. Delete the `frontend\node_modules` folder
2. Run `setup.bat` again
3. Or manually: `cd frontend` then `npm install` then `npm start`

---

## Quick Status Check

To verify everything is installed:

```bash
python --version    # Should show Python 3.x
node --version      # Should show v20.x or similar
npm --version       # Should show 9.x or similar
```

If any of these fail, that software needs to be installed.

---

## Still Having Problems?

1. Close all terminal windows
2. Restart your computer (to refresh PATH)
3. Try `setup.bat` again (run as administrator)
4. If it still fails, follow the manual installation steps above
