from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional

from database import engine, get_db, Base
from models import User, Goal
from schemas import UserRegister, UserLogin, UserResponse, Token, GoalCreate, GoalUpdate, GoalResponse, GoalCompletionResponse, StreakFreezePurchase, CalendarDay, DayView, SubGoalCreate, SubGoalResponse
from auth import authenticate_user, create_access_token, get_current_user, hash_password
from services import (
    create_goal, get_user_goals, complete_goal, delete_goal,
    get_user_streak, get_user_gems, purchase_streak_freeze,
    get_calendar_data, get_goal_completions, use_streak_freeze,
    create_subgoal, complete_subgoal, uncomplete_subgoal, delete_subgoal,
    get_subgoals, get_day_view
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Goal Tracker API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoints
@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_pwd = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_pwd,
            name=user_data.name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Goal endpoints
@app.post("/api/goals", response_model=GoalResponse)
def create_new_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_goal(db, current_user.id, goal)

@app.get("/api/goals", response_model=List[GoalResponse])
def get_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Return all active goals (both recurring and scheduled)
    # Frontend will filter them by date
    return db.query(Goal).filter(
        Goal.user_id == current_user.id, 
        Goal.is_active == True
    ).all()

@app.put("/api/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal

@app.delete("/api/goals/{goal_id}")
def delete_goal_endpoint(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = delete_goal(db, goal_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}

# Goal completion endpoints
from pydantic import BaseModel
from fastapi import Body

class CompleteGoalRequest(BaseModel):
    completion_date: Optional[str] = None

@app.post("/api/goals/{goal_id}/complete", response_model=GoalCompletionResponse)
def complete_goal_endpoint(goal_id: int, request: Optional[CompleteGoalRequest] = Body(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    completion_date = None
    if request and request.completion_date:
        completion_date = date.fromisoformat(request.completion_date)
    return complete_goal(db, current_user.id, goal_id, completion_date)

@app.get("/api/goals/completions", response_model=List[GoalCompletionResponse])
def get_completions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_goal_completions(db, current_user.id)

# Streak and gems endpoints
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    streak = get_user_streak(db, current_user.id)
    gems = get_user_gems(db, current_user.id)
    return {
        "streak": streak,
        "gems": gems,
        "freezes_available": current_user.streak_freezes
    }

@app.post("/api/freeze/purchase")
def purchase_freeze(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        purchase_streak_freeze(db, current_user.id)
        return {"message": "Freeze purchased successfully", "gems": get_user_gems(db, current_user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/freeze/use")
def use_freeze(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        use_streak_freeze(db, current_user.id)
        return {"message": "Freeze used successfully", "freezes_remaining": current_user.streak_freezes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Calendar endpoint
@app.get("/api/calendar/{year}/{month}")
def get_calendar_month(year: int, month: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_calendar_data(db, current_user.id, year, month)

# Day view endpoint
@app.get("/api/day/{date_str}")
def get_day_view_endpoint(date_str: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        target_date = date.fromisoformat(date_str)
        return get_day_view(db, current_user.id, target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

# SubGoal endpoints
@app.post("/api/subgoals", response_model=SubGoalResponse)
def create_new_subgoal(subgoal_data: SubGoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify the goal belongs to the user
    goal = db.query(Goal).filter(Goal.id == subgoal_data.goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    subgoal = create_subgoal(db, current_user.id, subgoal_data.goal_id, subgoal_data.title)
    
    # Return dict matching SubGoalResponse schema
    return {
        "id": subgoal.id,
        "goal_id": subgoal.goal_id,
        "title": subgoal.title,
        "is_completed": False,
        "completion_date": None,
        "created_at": subgoal.created_at
    }

@app.put("/api/subgoals/{subgoal_id}/complete")
def complete_subgoal_endpoint(subgoal_id: int, request: Optional[CompleteGoalRequest] = Body(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    completion_date = None
    if request and request.completion_date:
        completion_date = date.fromisoformat(request.completion_date)
    try:
        return complete_subgoal(db, subgoal_id, current_user.id, completion_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/api/subgoals/{subgoal_id}/uncomplete")
def uncomplete_subgoal_endpoint(subgoal_id: int, request: Optional[CompleteGoalRequest] = Body(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    completion_date = None
    if request and request.completion_date:
        completion_date = date.fromisoformat(request.completion_date)
    try:
        uncomplete_subgoal(db, subgoal_id, current_user.id, completion_date)
        return {"message": "Subgoal uncompleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/subgoals/{subgoal_id}")
def delete_subgoal_endpoint(subgoal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = delete_subgoal(db, subgoal_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Subgoal not found")
    return {"message": "Subgoal deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
