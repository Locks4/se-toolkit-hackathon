# 🎯 How to Start the Goal Tracker App

## Quick Start (2 Steps)

### Step 1: First Time Only
Double-click: **`setup.bat`**
- Installs Python (if missing)
- Installs Node.js (if missing)
- Installs dependencies

### Step 2: Every Time You Want to Use the App
Double-click: **`start.bat`**

Three windows will open:
1. **Start Window** (shows progress, press any key when done)
2. **Backend Window** (blue - keep this open!)
3. **Frontend Window** (green - keep this open!)

Your browser will automatically open to: **http://localhost:3000**

---

## What You'll See

### Window 1: Start Progress
```
========================================
  Goal Tracker App - Starting
========================================

Step 1/4: Checking Python...
[OK] Python found!

Step 2/4: Checking Node.js...
[OK] Node.js found!

Step 3/4: Starting Backend...
[OK] Backend is running!

Step 4/4: Starting Frontend...
[OK] Frontend starting!

Press any key to continue...
```

### Window 2: Backend (Blue)
```
============================================
  BACKEND SERVER - Keep this window open!
============================================

INFO: Uvicorn running on http://0.0.0.0:8000
```

### Window 3: Frontend (Green)
```
============================================
  FRONTEND SERVER - Keep this window open!
============================================

Compiled successfully!
You can now view the app in the browser.
Local: http://localhost:3000
```

---

## If Something Goes Wrong

### "Python is not found"
→ Run `setup.bat` first

### "Node.js is not found"
→ Run `setup.bat` first

### Backend window shows errors
→ Check the error message, it will tell you what's wrong

### Frontend window shows errors
→ Run `setup.bat` to reinstall dependencies

### Browser doesn't open
→ Manually go to: http://localhost:3000

---

## To Stop the App
Just close the Backend and Frontend windows when you're done.

---

## Troubleshooting

**Q: I double-clicked start.bat and nothing happened**
A: Look for 3 windows opening - they may be behind other windows!

**Q: It says "Backend may not be responding"**
A: Check the Backend window - there will be an error message shown

**Q: I get "port already in use" errors**
A: Close any existing Backend/Frontend windows and try again

---

**Need more help?** See `TROUBLESHOOTING.md`
