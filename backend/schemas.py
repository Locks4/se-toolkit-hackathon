from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# Auth schemas
class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    name: str
    gems: int
    streak_freezes: int

class Token(BaseModel):
    access_token: str
    token_type: str

# SubGoal schemas
class SubGoalCreate(BaseModel):
    title: str
    goal_id: int

class SubGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    goal_id: int
    title: str
    is_completed: bool
    completion_date: Optional[date] = None
    created_at: datetime

# Goal schemas
class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_recurring: bool = True
    scheduled_date: Optional[date] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    is_active: bool
    is_recurring: bool
    scheduled_date: Optional[date] = None
    created_at: datetime

# Goal completion schemas
class GoalCompletionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    goal_id: int
    completed_at: datetime
    completion_date: date

# Streak freeze schemas
class StreakFreezePurchase(BaseModel):
    cost: int = 10  # Default cost in gems

class CalendarDay(BaseModel):
    date: date
    goals_total: int
    goals_completed: int
    is_frozen: bool = False

class DayView(BaseModel):
    date: date
    goals: List[GoalResponse]
    completions: List[GoalCompletionResponse]
    total_goals: int
    completed_goals: int
    completion_percentage: float
