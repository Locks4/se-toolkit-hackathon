from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gems = Column(Integer, default=0)
    streak_freezes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    goals = relationship("Goal", back_populates="user")
    completions = relationship("GoalCompletion", back_populates="user")
    streak_freeze_logs = relationship("StreakFreezeLog", back_populates="user")
    subgoals = relationship("SubGoal", back_populates="user")
    subgoal_completions = relationship("SubGoalCompletion", back_populates="user")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=True)  # True = daily recurring goal, False = scheduled for specific date
    scheduled_date = Column(Date, nullable=True)  # For non-recurring goals
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")
    completions = relationship("GoalCompletion", back_populates="goal")
    subgoals = relationship("SubGoal", back_populates="goal", cascade="all, delete-orphan")

class SubGoal(Base):
    __tablename__ = "subgoals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subgoals")
    goal = relationship("Goal", back_populates="subgoals")
    completions = relationship("SubGoalCompletion", back_populates="subgoal", cascade="all, delete-orphan")

class SubGoalCompletion(Base):
    __tablename__ = "subgoal_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subgoal_id = Column(Integer, ForeignKey("subgoals.id"), nullable=False)
    completion_date = Column(Date, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subgoal_completions")
    subgoal = relationship("SubGoal", back_populates="completions")

class GoalCompletion(Base):
    __tablename__ = "goal_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="completions")
    goal = relationship("Goal", back_populates="completions")

class StreakFreezeLog(Base):
    __tablename__ = "streak_freeze_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)
    freeze_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="streak_freeze_logs")
