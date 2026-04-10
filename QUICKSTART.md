# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- npm or yarn package manager

## Installation & Running

### Option 1: Using Setup Script (Recommended for Windows)

Double-click `setup.bat` to install all dependencies automatically.

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Starting the App

### Using Start Script (Windows):
Double-click `start.bat` - this will open two terminals automatically.

### Manual Start:

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Backend runs on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend opens at: http://localhost:3000

## Using the App

1. **Register**: Create a new account with email and password
2. **Add Goals**: Click "+ Add Goal" to create your daily goals
3. **Complete Goals**: Mark each goal as complete (earns 1 gem per completion)
4. **Build Streaks**: Complete ALL goals every day to maintain your streak
5. **Buy Freezes**: Spend 10 gems to buy a streak freeze
6. **Use Freezes**: Protect your streak when you miss a day
7. **View Calendar**: See your progress heatmap (Duolingo-style)

## API Documentation

Once backend is running, visit: http://localhost:8000/docs

This shows all available API endpoints with test functionality.

## Troubleshooting

**Backend won't start:**
- Make sure Python is installed: `python --version`
- Make sure pip is available: `pip --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Make sure Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Clear cache: `npm start` usually works

**Port already in use:**
- Backend: Change port in `backend/main.py` (last line)
- Frontend: React will prompt to use a different port

## Features Checklist

✅ User registration and login
✅ Add/edit/delete goals
✅ Mark goals as complete
✅ Earn 1 gem per completed goal
✅ Track daily streak (consecutive days with all goals completed)
✅ Purchase streak freeze for 10 gems
✅ Use freeze to skip 1 day without breaking streak
✅ Calendar heatmap showing goal completion
✅ Color-coded calendar (gray → yellow → orange → green)
✅ Modern, responsive UI
✅ Protected routes (login required)

## Default Test Credentials

Create any account you want - there's no predefined test user.

## Next Steps

1. Run the app
2. Create an account
3. Add some goals
4. Test completing them
5. Check the calendar view
6. Try buying a freeze

Enjoy your Goal Tracker! 🎯💎🔥
