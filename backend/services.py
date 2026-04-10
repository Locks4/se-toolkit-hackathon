from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
from models import User, Goal, GoalCompletion, StreakFreezeLog, SubGoal, SubGoalCompletion
from schemas import GoalCreate

FREEZE_COST = 5  # Gems needed to buy a streak freeze

def create_goal(db: Session, user_id: int, goal_data: GoalCreate):
    # Validate scheduled_date is not in the past
    if not goal_data.is_recurring and goal_data.scheduled_date:
        if goal_data.scheduled_date < date.today():
            raise ValueError("Cannot schedule a goal for a past date")
    
    goal = Goal(
        user_id=user_id,
        title=goal_data.title,
        description=goal_data.description,
        is_recurring=goal_data.is_recurring,
        scheduled_date=goal_data.scheduled_date if not goal_data.is_recurring else None
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    # Load subgoals (will be empty for new goal)
    goal.subgoals = []
    return goal

def get_user_goals(db: Session, user_id: int, target_date: date = None):
    """Get goals for a specific date or today's recurring goals"""
    if target_date is None:
        target_date = date.today()

    # Get all active recurring goals
    all_recurring = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.is_active == True,
        Goal.is_recurring == True
    ).all()
    
    # Filter recurring goals: only show on dates >= their creation date
    recurring_goals = []
    for goal in all_recurring:
        goal_creation_date = goal.created_at.date()
        if target_date >= goal_creation_date:
            recurring_goals.append(goal)

    # Get goals scheduled for specific date
    scheduled_goals = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.is_active == True,
        Goal.is_recurring == False,
        Goal.scheduled_date == target_date
    ).all()

    all_goals = recurring_goals + scheduled_goals

    return all_goals

def get_goals_for_date(db: Session, user_id: int, target_date: date):
    """Get all goals visible for a specific date"""
    return get_user_goals(db, user_id, target_date)

def delete_goal(db: Session, goal_id: int, user_id: int):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return False
    goal.is_active = False
    db.commit()
    return True

def complete_goal(db: Session, user_id: int, goal_id: int, completion_date: date = None):
    if completion_date is None:
        completion_date = date.today()
    
    # Prevent completing goals in the future
    if completion_date > date.today():
        raise ValueError("Cannot complete goals for a future date")
    
    # Get the goal
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise ValueError("Goal not found")
    
    # Check if already completed on this date
    existing = db.query(GoalCompletion).filter(
        GoalCompletion.user_id == user_id,
        GoalCompletion.goal_id == goal_id,
        GoalCompletion.completion_date == completion_date
    ).first()
    
    if existing:
        raise ValueError("Goal already completed on this date")
    
    # Create completion record
    completion = GoalCompletion(
        user_id=user_id,
        goal_id=goal_id,
        completed_at=datetime.utcnow(),
        completion_date=completion_date
    )
    
    # Award 1 gem only if completing today
    user = db.query(User).filter(User.id == user_id).first()
    if completion_date == date.today():
        user.gems += 1
    
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion

def get_goal_completions(db: Session, user_id: int, days: int = 90):
    since = date.today() - timedelta(days=days)
    return db.query(GoalCompletion).filter(
        GoalCompletion.user_id == user_id,
        GoalCompletion.completion_date >= since
    ).all()

def get_completions_for_date(db: Session, user_id: int, target_date: date):
    """Get all completions for a specific date"""
    return db.query(GoalCompletion).filter(
        GoalCompletion.user_id == user_id,
        GoalCompletion.completion_date == target_date
    ).all()

def get_user_streak(db: Session, user_id: int) -> int:
    """Calculate current streak in days"""
    user = db.query(User).filter(User.id == user_id).first()
    
    # Check if user has any freezes that might protect the streak
    recent_freeze = db.query(StreakFreezeLog).filter(
        StreakFreezeLog.user_id == user_id,
        StreakFreezeLog.freeze_date >= date.today() - timedelta(days=1)
    ).first()
    
    # Get all completions
    completions = db.query(GoalCompletion).filter(
        GoalCompletion.user_id == user_id
    ).order_by(GoalCompletion.completion_date.desc()).all()
    
    if not completions:
        return 0
    
    # Get active recurring goals
    active_goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.is_active == True, Goal.is_recurring == True).all()
    
    if not active_goals:
        return 0
    
    # Calculate streak
    streak = 0
    current_date = date.today()
    
    # Check if today is completed
    today_completions = [c for c in completions if c.completion_date == current_date]
    
    # If today is not completed and no freeze protection, streak is broken
    if not today_completions and not recent_freeze:
        # Check if yesterday was completed
        yesterday = current_date - timedelta(days=1)
        yesterday_completions = [c for c in completions if c.completion_date == yesterday]
        
        if not yesterday_completions:
            return 0
        # Start from yesterday
        current_date = yesterday
    
    # Count consecutive days
    while True:
        day_completions = [c for c in completions if c.completion_date == current_date]
        
        # Check if all active recurring goals were completed on this day
        completed_goal_ids = set(c.goal_id for c in day_completions)
        active_goal_ids = set(g.id for g in active_goals)
        
        if active_goal_ids.issubset(completed_goal_ids):
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Check if there's a freeze for this date
            freeze = db.query(StreakFreezeLog).filter(
                StreakFreezeLog.user_id == user_id,
                StreakFreezeLog.freeze_date == current_date
            ).first()
            
            if freeze:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
    
    return streak

def get_user_gems(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    return user.gems

def purchase_streak_freeze(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.gems < FREEZE_COST:
        raise ValueError(f"Not enough gems. Need {FREEZE_COST}, have {user.gems}")
    
    user.gems -= FREEZE_COST
    user.streak_freezes += 1
    db.commit()
    return user

def use_streak_freeze(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.streak_freezes <= 0:
        raise ValueError("No streak freezes available")
    
    user.streak_freezes -= 1
    
    # Log the freeze usage
    freeze_log = StreakFreezeLog(
        user_id=user_id,
        freeze_date=date.today()
    )
    db.add(freeze_log)
    db.commit()
    return user

def get_calendar_data(db: Session, user_id: int, year: int, month: int):
    """Get calendar data for a specific month"""
    from datetime import date as date_type
    
    # Get first and last day of the month
    first_day = date_type(year, month, 1)
    if month == 12:
        last_day = date_type(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date_type(year, month + 1, 1) - timedelta(days=1)
    
    # Get all completions in this month
    completions = db.query(GoalCompletion).filter(
        GoalCompletion.user_id == user_id,
        GoalCompletion.completion_date >= first_day,
        GoalCompletion.completion_date <= last_day
    ).all()
    
    # Get all freezes in this month
    freezes = db.query(StreakFreezeLog).filter(
        StreakFreezeLog.user_id == user_id,
        StreakFreezeLog.freeze_date >= first_day,
        StreakFreezeLog.freeze_date <= last_day
    ).all()
    
    freeze_dates = set(f.freeze_date for f in freezes)
    
    # Group completions by date
    completion_counts = {}
    for completion in completions:
        completion_counts[completion.completion_date] = completion_counts.get(completion.completion_date, 0) + 1
    
    # Get active recurring goals count
    active_goals = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.is_active == True,
        Goal.is_recurring == True
    ).count()
    
    # Build calendar days
    calendar_days = []
    current = first_day
    while current <= last_day:
        goals_completed = completion_counts.get(current, 0)
        calendar_days.append({
            "date": current.isoformat(),
            "goals_total": active_goals,
            "goals_completed": goals_completed,
            "is_frozen": current in freeze_dates,
            "completion_percentage": (goals_completed / active_goals * 100) if active_goals > 0 else 0
        })
        current += timedelta(days=1)
    
    return {
        "year": year,
        "month": month,
        "days": calendar_days
    }

# SubGoal functions
def create_subgoal(db: Session, user_id: int, goal_id: int, title: str):
    subgoal = SubGoal(
        user_id=user_id,
        goal_id=goal_id,
        title=title
    )
    db.add(subgoal)
    db.commit()
    db.refresh(subgoal)
    return subgoal

def get_subgoals(db: Session, goal_id: int, target_date: date = None):
    """Get subgoals for a goal, with completion status for a specific date"""
    subgoals = db.query(SubGoal).filter(SubGoal.goal_id == goal_id).all()
    
    if target_date is None:
        target_date = date.today()
    
    # Get completions for this date
    completions = db.query(SubGoalCompletion).filter(
        SubGoalCompletion.subgoal_id.in_([sg.id for sg in subgoals]),
        SubGoalCompletion.completion_date == target_date
    ).all()
    
    completed_subgoal_ids = set(c.subgoal_id for c in completions)
    
    # Build response with completion status
    result = []
    for sg in subgoals:
        sg_dict = {
            'id': sg.id,
            'goal_id': sg.goal_id,
            'title': sg.title,
            'is_completed': sg.id in completed_subgoal_ids,
            'completion_date': target_date.isoformat() if sg.id in completed_subgoal_ids else None,
            'created_at': sg.created_at
        }
        result.append(sg_dict)
    
    return result

def complete_subgoal(db: Session, subgoal_id: int, user_id: int, completion_date: date = None):
    if completion_date is None:
        completion_date = date.today()
    
    subgoal = db.query(SubGoal).filter(SubGoal.id == subgoal_id, SubGoal.user_id == user_id).first()
    if not subgoal:
        raise ValueError("SubGoal not found")
    
    # Check if already completed on this date
    existing = db.query(SubGoalCompletion).filter(
        SubGoalCompletion.subgoal_id == subgoal_id,
        SubGoalCompletion.completion_date == completion_date
    ).first()
    
    if existing:
        raise ValueError("Subgoal already completed on this date")
    
    # Create completion record
    completion = SubGoalCompletion(
        user_id=user_id,
        subgoal_id=subgoal_id,
        completion_date=completion_date
    )
    db.add(completion)
    db.commit()
    return completion

def uncomplete_subgoal(db: Session, subgoal_id: int, user_id: int, completion_date: date = None):
    if completion_date is None:
        completion_date = date.today()
    
    # Delete completion record for this date
    completion = db.query(SubGoalCompletion).filter(
        SubGoalCompletion.subgoal_id == subgoal_id,
        SubGoalCompletion.completion_date == completion_date
    ).first()
    
    if not completion:
        raise ValueError("Subgoal completion not found for this date")
    
    db.delete(completion)
    db.commit()
    return True

def delete_subgoal(db: Session, subgoal_id: int, user_id: int):
    subgoal = db.query(SubGoal).filter(SubGoal.id == subgoal_id, SubGoal.user_id == user_id).first()
    if not subgoal:
        return False
    db.delete(subgoal)
    db.commit()
    return True

def get_day_view(db: Session, user_id: int, target_date: date):
    """Get complete view for a specific date"""
    goals = get_goals_for_date(db, user_id, target_date)
    completions = get_completions_for_date(db, user_id, target_date)

    # Build goals with subgoals as dicts
    goals_with_subgoals = []
    for goal in goals:
        subgoals = get_subgoals(db, goal.id, target_date)
        goal_dict = {
            "id": goal.id,
            "title": goal.title,
            "description": goal.description,
            "is_active": goal.is_active,
            "is_recurring": goal.is_recurring,
            "scheduled_date": goal.scheduled_date,
            "created_at": goal.created_at,
            "subgoals": subgoals
        }
        goals_with_subgoals.append(goal_dict)

    total_goals = len(goals_with_subgoals)
    completed_goals = len(completions)

    return {
        "date": target_date.isoformat(),
        "goals": goals_with_subgoals,
        "completions": completions,
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "completion_percentage": (completed_goals / total_goals * 100) if total_goals > 0 else 0
    }
