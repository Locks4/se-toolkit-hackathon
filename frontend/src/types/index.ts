export interface User {
  id: number;
  email: string;
  name: string;
  gems: number;
  streak_freezes: number;
}

export interface SubGoal {
  id: number;
  goal_id: number;
  title: string;
  is_completed: boolean;
  completion_date: string | null;
  created_at: string;
}

export interface Goal {
  id: number;
  title: string;
  description: string | null;
  is_active: boolean;
  is_recurring: boolean;
  scheduled_date: string | null;
  created_at: string;
  subgoals?: SubGoal[];
}

export interface GoalCompletion {
  id: number;
  goal_id: number;
  completed_at: string;
  completion_date: string;
}

export interface Stats {
  streak: number;
  gems: number;
  freezes_available: number;
}

export interface CalendarDay {
  date: string;
  goals_total: number;
  goals_completed: number;
  is_frozen: boolean;
  completion_percentage: number;
}

export interface DayView {
  date: string;
  goals: Goal[];
  completions: GoalCompletion[];
  total_goals: number;
  completed_goals: number;
  completion_percentage: number;
}

export interface CalendarData {
  year: number;
  month: number;
  days: CalendarDay[];
}
