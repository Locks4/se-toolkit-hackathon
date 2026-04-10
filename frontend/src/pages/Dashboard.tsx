import React, { useState, useEffect } from 'react';
import { goalsAPI, statsAPI, calendarAPI, subgoalsAPI } from '../api';
import { Goal, Stats, CalendarData, SubGoal } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

// Helper function to get local date string in YYYY-MM-DD format
const getLocalDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const Dashboard: React.FC = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [stats, setStats] = useState<Stats>({ streak: 0, gems: 0, freezes_available: 0 });
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [newGoalDescription, setNewGoalDescription] = useState('');
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [isDaily, setIsDaily] = useState(false);
  const [newSubgoalTitle, setNewSubgoalTitle] = useState('');
  const [addingSubgoalToGoal, setAddingSubgoalToGoal] = useState<number | null>(null);
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [completedGoals, setCompletedGoals] = useState<Map<string, Set<number>>>(new Map());
  const [viewingDate, setViewingDate] = useState(new Date());
  const [showDayView, setShowDayView] = useState(false);
  const [dayViewData, setDayViewData] = useState<any>(null);
  const [expandedGoals, setExpandedGoals] = useState<Set<number>>(new Set());
  const [selectedCalendarDate, setSelectedCalendarDate] = useState<Date | null>(null);
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);
  const [confirmModal, setConfirmModal] = useState<{message: string; onConfirm: () => void} | null>(null);
  
  // Ref to track current viewing date synchronously
  const viewingDateRef = React.useRef<Date>(new Date());

  // Toast notification helper
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Confirmation modal helper
  const showConfirm = (message: string, onConfirm: () => void) => {
    setConfirmModal({ message, onConfirm });
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    loadGoals();
    loadStats();
    loadCalendar();
  }, [currentMonth, currentYear]);

  // Keep ref in sync with viewingDate state
  useEffect(() => {
    viewingDateRef.current = viewingDate;
  }, [viewingDate]);

  useEffect(() => {
    checkCompletedGoalsForDate(viewingDate);
  }, [goals, viewingDate]);

  const loadGoals = async () => {
    try {
      const response = await goalsAPI.getAll();
      setGoals(response.data);
    } catch (error) {
      console.error('Failed to load goals:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await statsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadCalendar = async () => {
    try {
      const response = await calendarAPI.getMonth(currentYear, currentMonth);
      setCalendarData(response.data);
    } catch (error) {
      console.error('Failed to load calendar:', error);
    }
  };

  const checkCompletedGoalsForDate = async (date: Date) => {
    try {
      const dateStr = getLocalDateString(date);
      const cacheKey = dateStr;
      if (completedGoals.has(cacheKey)) {
        return;
      }

      const response = await goalsAPI.getCompletions();
      const completed = new Set<number>();
      response.data.forEach((completion: any) => {
        if (completion.completion_date === dateStr) {
          completed.add(completion.goal_id);
        }
      });
      
      const newMap = new Map(completedGoals);
      newMap.set(cacheKey, completed);
      setCompletedGoals(newMap);
    } catch (error) {
      console.error('Failed to load completions:', error);
    }
  };

  const getCompletedForDate = (date: Date): Set<number> => {
    const dateStr = getLocalDateString(date);
    return completedGoals.get(dateStr) || new Set();
  };

  const loadDayView = async (date: Date) => {
    // Update viewing date immediately so UI reflects selection instantly
    setViewingDate(date);
    setSelectedCalendarDate(date);
    
    // Force immediate re-render with the new date
    await new Promise(resolve => setTimeout(resolve, 0));
    
    try {
      const dateStr = getLocalDateString(date);
      const response = await calendarAPI.getDay(dateStr);
      setDayViewData(response.data);
      setShowDayView(true);
      await checkCompletedGoalsForDate(date);
    } catch (error: any) {
      console.error('Failed to load day view:', error);
    }
  };

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGoalTitle.trim()) return;

    try {
      await goalsAPI.create({
        title: newGoalTitle,
        description: newGoalDescription || undefined,
        is_recurring: isDaily,
        scheduled_date: isDaily ? undefined : getLocalDateString(viewingDate),
      });
      setNewGoalTitle('');
      setNewGoalDescription('');
      setIsDaily(false);
      setShowAddGoal(false);
      loadGoals();
      if (showDayView) {
        loadDayView(viewingDate);
      }
      showToast('Goal added successfully!', 'success');
    } catch (error: any) {
      console.error('Failed to create goal:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to add goal';
      showToast(errorMsg, 'error');
    }
  };

  const handleCompleteGoal = async (goalId: number, date: Date = viewingDate) => {
    try {
      const dateStr = getLocalDateString(date);
      await goalsAPI.complete(goalId, dateStr);
      
      const dateKey = dateStr;
      const newMap = new Map(completedGoals);
      const completedSet = newMap.get(dateKey) || new Set();
      completedSet.add(goalId);
      newMap.set(dateKey, completedSet);
      setCompletedGoals(newMap);
      
      if (showDayView) {
        loadDayView(date);
      }
      
      loadStats();
      showToast('Goal completed! +1 💎', 'success');
    } catch (error: any) {
      console.error('Failed to complete goal:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to complete goal';
      showToast(errorMsg, 'error');
    }
  };

  const handleDeleteGoal = async (goalId: number) => {
    showConfirm('Are you sure you want to delete this goal?', async () => {
      try {
        await goalsAPI.delete(goalId);
        loadGoals();
        showToast('Goal deleted', 'success');
      } catch (error) {
        console.error('Failed to delete goal:', error);
        showToast('Failed to delete goal', 'error');
      }
    });
  };

  const handleAddSubgoal = async (goalId: number) => {
    if (!newSubgoalTitle.trim()) return;

    try {
      await subgoalsAPI.create({
        title: newSubgoalTitle,
        goal_id: goalId,
      });
      setNewSubgoalTitle('');
      setAddingSubgoalToGoal(null);
      loadGoals();
      if (showDayView) {
        loadDayView(viewingDate);
      }
    } catch (error) {
      console.error('Failed to add subgoal:', error);
    }
  };

  const handleToggleSubgoal = async (subgoal: SubGoal) => {
    try {
      const dateStr = getLocalDateString(viewingDate);
      if (subgoal.is_completed) {
        await subgoalsAPI.uncomplete(subgoal.id, dateStr);
      } else {
        await subgoalsAPI.complete(subgoal.id, dateStr);
      }
      loadGoals();
      if (showDayView) {
        loadDayView(viewingDate);
      }
    } catch (error) {
      console.error('Failed to toggle subgoal:', error);
    }
  };

  const handleDeleteSubgoal = async (subgoalId: number) => {
    showConfirm('Delete this subgoal?', async () => {
      try {
        await subgoalsAPI.delete(subgoalId);
        loadGoals();
        if (showDayView) {
          loadDayView(viewingDate);
        }
        showToast('Subgoal deleted', 'success');
      } catch (error) {
        console.error('Failed to delete subgoal:', error);
        showToast('Failed to delete subgoal', 'error');
      }
    });
  };

  const handlePurchaseFreeze = async () => {
    showConfirm('Purchase a streak freeze for 5 gems?', async () => {
      try {
        await statsAPI.purchaseFreeze();
        loadStats();
        showToast('Freeze purchased successfully! ❄️', 'success');
      } catch (error: any) {
        showToast(error.response?.data?.detail || 'Failed to purchase freeze', 'error');
      }
    });
  };

  const handleUseFreeze = async () => {
    showConfirm('Use a streak freeze to protect your streak today?', async () => {
      try {
        await statsAPI.useFreeze();
        loadStats();
        showToast('Freeze used successfully! ❄️', 'success');
      } catch (error: any) {
        showToast(error.response?.data?.detail || 'Failed to use freeze', 'error');
      }
    });
  };

  const getCompletionColor = (completed: number, total: number): string => {
    if (total === 0) return '#e0e0e0';
    const percentage = completed / total;
    if (percentage === 0) return '#e0e0e0';
    if (percentage < 0.5) return '#ffd700';
    if (percentage < 1) return '#ffa500';
    return '#4caf50';
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const goToPreviousMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const goToNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const goToPreviousDay = () => {
    const newDate = new Date(viewingDate);
    newDate.setDate(newDate.getDate() - 1);
    loadDayView(newDate);
  };

  const goToNextDay = () => {
    const newDate = new Date(viewingDate);
    newDate.setDate(newDate.getDate() + 1);
    loadDayView(newDate);
  };

  const goToToday = () => {
    const today = new Date();
    setViewingDate(today);
    setShowDayView(false);
    setSelectedCalendarDate(null);
  };

  const toggleGoalExpansion = (goalId: number) => {
    const newExpanded = new Set(expandedGoals);
    if (newExpanded.has(goalId)) {
      newExpanded.delete(goalId);
    } else {
      newExpanded.add(goalId);
    }
    setExpandedGoals(newExpanded);
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
    if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
    
    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  };

  const completedForCurrentView = getCompletedForDate(viewingDate);
  const allGoalsCompletedForToday = goals.length > 0 && goals.every(g => getCompletedForDate(new Date()).has(g.id));
  
  // Use ref for synchronous date comparison
  const viewingDateRefCurrent = viewingDateRef.current;
  
  // Check if viewing date is today, future, or past
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const viewingDateObj = new Date(viewingDateRefCurrent);
  viewingDateObj.setHours(0, 0, 0, 0);
  
  const isViewingFuture = viewingDateObj > today;
  const isViewingPast = viewingDateObj < today;
  const isViewingToday = viewingDateObj.getTime() === today.getTime();
  const canCompleteGoals = !isViewingFuture && !isViewingPast; // Only today
  
  // Filter goals based on the selected calendar date using ref
  const goalsForViewingDate = goals.filter(goal => {
    if (goal.is_recurring) {
      // Daily goals: show on creation date and all future dates
      const createdStr = goal.created_at.split('T')[0];
      const createdDate = new Date(createdStr + 'T00:00:00');
      return viewingDateObj >= createdDate;
    } else {
      // One-time goals: show only on their scheduled date
      if (!goal.scheduled_date) return false;
      const scheduledDate = new Date(goal.scheduled_date + 'T00:00:00');
      return scheduledDate.getTime() === viewingDateObj.getTime();
    }
  });

  return (
    <div className="dashboard">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          <span className="toast-icon">{toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}</span>
          <span className="toast-message">{toast.message}</span>
          <button className="toast-close" onClick={() => setToast(null)}>×</button>
        </div>
      )}

      {/* Confirmation Modal */}
      {confirmModal && (
        <div className="modal-overlay" onClick={() => setConfirmModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">❓</div>
            <p className="modal-message">{confirmModal.message}</p>
            <div className="modal-actions">
              <button 
                className="btn-modal-cancel"
                onClick={() => setConfirmModal(null)}
              >
                Cancel
              </button>
              <button 
                className="btn-modal-confirm"
                onClick={() => {
                  setConfirmModal(null);
                  confirmModal.onConfirm();
                }}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="dashboard-header">
        <div className="header-top">
          <h1>🎯 Goal Tracker</h1>
          <div className="header-actions">
            <button onClick={goToToday} className="btn-today">📍 Today</button>
            {user && <span className="user-name">👤 {user.name}</span>}
            <button onClick={handleLogout} className="btn-logout">🚪 Sign Out</button>
          </div>
        </div>
        <div className="stats-bar">
          <div className="stat-item">
            <span className="stat-icon">🔥</span>
            <span className="stat-value">{stats.streak}</span>
            <span className="stat-label">Day Streak</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">💎</span>
            <span className="stat-value">{stats.gems}</span>
            <span className="stat-label">Gems</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">❄️</span>
            <span className="stat-value">{stats.freezes_available}</span>
            <span className="stat-label">Freezes</span>
          </div>
        </div>
      </header>

      <div className="freeze-actions">
        <button onClick={handlePurchaseFreeze} className="btn-secondary" disabled={stats.gems < 5}>
          Buy Freeze (5 💎)
        </button>
        <button onClick={handleUseFreeze} className="btn-secondary" disabled={stats.freezes_available === 0}>
          Use Freeze
        </button>
      </div>

      {showDayView && dayViewData && (
        <div className="day-view">
          <div className="day-header">
            <button onClick={goToPreviousDay} className="btn-nav">←</button>
            <h2>{formatDate(viewingDate)}</h2>
            <button onClick={goToNextDay} className="btn-nav">→</button>
          </div>
          {isViewingFuture && (
            <div className="day-warning">
              ⚠️ You're viewing a future date. You can add goals but cannot complete them yet.
            </div>
          )}
          {isViewingPast && (
            <div className="day-warning">
              ⚠️ You're viewing a past date. Goals cannot be completed for past dates.
            </div>
          )}
          <div className="day-stats">
            <div className="day-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${dayViewData.completion_percentage}%` }}
                />
              </div>
              <span className="progress-text">
                {dayViewData.completed_goals}/{dayViewData.total_goals} completed
              </span>
            </div>
          </div>

          <div className="day-goals">
            {dayViewData.goals.map((goal: Goal) => {
              const isCompleted = dayViewData.completions.some((c: any) => c.goal_id === goal.id);
              const goalSubgoals = goal.subgoals || [];
              const isExpanded = expandedGoals.has(goal.id);
              
              return (
                <div key={goal.id} className={`day-goal-card ${isCompleted ? 'completed' : ''}`}>
                  <div className="goal-header" onClick={() => toggleGoalExpansion(goal.id)}>
                    <div className="goal-info">
                      <h3>{goal.title}</h3>
                      {goal.description && <p>{goal.description}</p>}
                      {goalSubgoals.length > 0 && (
                        <span className="subgoal-count">
                          {goalSubgoals.filter((s: SubGoal) => s.is_completed).length}/{goalSubgoals.length} subgoals
                        </span>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCompleteGoal(goal.id, viewingDate);
                      }}
                      disabled={isCompleted || !canCompleteGoals}
                      className={isCompleted ? 'btn-completed' : !canCompleteGoals ? 'btn-disabled' : 'btn-complete'}
                    >
                      {isCompleted ? '✓ Done' : !canCompleteGoals ? (isViewingFuture ? '🔒 Future' : '📁 Past') : 'Complete'}
                    </button>
                  </div>

                  {isExpanded && (
                    <div className="goal-details">
                      {goalSubgoals.length > 0 && (
                        <div className="subgoals-list">
                          {goalSubgoals.map((subgoal: SubGoal) => (
                            <div key={subgoal.id} className={`subgoal-item ${subgoal.is_completed ? 'completed' : ''}`}>
                              <input
                                type="checkbox"
                                checked={subgoal.is_completed}
                                onChange={() => handleToggleSubgoal(subgoal)}
                              />
                              <span className="subgoal-title">{subgoal.title}</span>
                              <button onClick={() => handleDeleteSubgoal(subgoal.id)} className="btn-delete-small">
                                🗑️
                              </button>
                            </div>
                          ))}
                        </div>
                      )}

                      {addingSubgoalToGoal === goal.id ? (
                        <div className="add-subgoal-form">
                          <input
                            type="text"
                            placeholder="Subgoal title"
                            value={newSubgoalTitle}
                            onChange={(e) => setNewSubgoalTitle(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleAddSubgoal(goal.id)}
                          />
                          <div className="subgoal-actions">
                            <button onClick={() => handleAddSubgoal(goal.id)} className="btn-small btn-success">Add</button>
                            <button onClick={() => setAddingSubgoalToGoal(null)} className="btn-small btn-secondary">Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <button 
                          onClick={() => setAddingSubgoalToGoal(goal.id)}
                          className="btn-add-subgoal"
                        >
                          + Add Subgoal
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            {dayViewData.goals.length === 0 && (
              <div className="empty-state">
                <p>No goals for this day</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="dashboard-content">
        <div className="goals-section">
          <div className="goals-header">
            <h2>Your Goals {isViewingToday ? '' : `(${formatDate(viewingDate)})`}</h2>
            <button 
              onClick={() => setShowAddGoal(!showAddGoal)} 
              className="btn-primary"
              disabled={isViewingPast}
              title={isViewingPast ? "Cannot add goals for past dates" : ""}
            >
              + Add Goal
            </button>
          </div>

          {showAddGoal && (
            <form onSubmit={handleAddGoal} className="add-goal-form">
              <input
                type="text"
                placeholder="Goal title (e.g., Exercise, Read, Meditate)"
                value={newGoalTitle}
                onChange={(e) => setNewGoalTitle(e.target.value)}
                required
              />
              <textarea
                placeholder="Description (optional)"
                value={newGoalDescription}
                onChange={(e) => setNewGoalDescription(e.target.value)}
                rows={2}
              />
              <div className="goal-option">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={isDaily}
                    onChange={(e) => setIsDaily(e.target.checked)}
                  />
                  <span>📅 Make this a daily recurring goal</span>
                </label>
                {!isDaily && (
                  <p className="goal-hint">
                    This goal will be added for <strong>{formatDate(viewingDate)}</strong> only
                    {isViewingPast && (
                      <span className="hint-error"> ⚠️ Cannot add goals for past dates</span>
                    )}
                  </p>
                )}
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-success">
                  {isDaily ? 'Add Daily Goal' : 'Add One-Time Goal'}
                </button>
                <button type="button" onClick={() => setShowAddGoal(false)} className="btn-secondary">Cancel</button>
              </div>
            </form>
          )}

          {allGoalsCompletedForToday && !showDayView && (
            <div className="success-banner">
              🎉 All goals completed today! Great job!
            </div>
          )}

          <div className="goals-list" key={viewingDate.toDateString()}>
            {goalsForViewingDate.map(goal => (
              <div key={goal.id} className={`goal-card ${getCompletedForDate(viewingDate).has(goal.id) ? 'completed' : ''}`}>
                <div className="goal-content">
                  <h3>{goal.title}</h3>
                  {goal.description && <p>{goal.description}</p>}
                </div>
                <div className="goal-actions">
                  <button
                    onClick={() => handleCompleteGoal(goal.id, viewingDate)}
                    disabled={getCompletedForDate(viewingDate).has(goal.id) || !canCompleteGoals}
                    className={getCompletedForDate(viewingDate).has(goal.id) ? 'btn-completed' : !canCompleteGoals ? 'btn-disabled' : 'btn-complete'}
                  >
                    {getCompletedForDate(viewingDate).has(goal.id) ? '✓ Done' : !canCompleteGoals ? (isViewingFuture ? '🔒 Future' : '📁 Past') : 'Complete'}
                  </button>
                  <button onClick={() => handleDeleteGoal(goal.id)} className="btn-delete">
                    🗑️
                  </button>
                </div>
              </div>
            ))}
            {goalsForViewingDate.length === 0 && (
              <div className="empty-state">
                <p>No goals for {isViewingToday ? 'today' : formatDate(viewingDate)}. Add your first goal to get started!</p>
              </div>
            )}
          </div>
        </div>

        <div className="calendar-section">
          <h2>Calendar</h2>
          <div className="calendar-nav">
            <button onClick={goToPreviousMonth}>←</button>
            <h3>{monthNames[currentMonth - 1]} {currentYear}</h3>
            <button onClick={goToNextMonth}>→</button>
          </div>

          {calendarData && (
            <div className="calendar-grid">
              <div className="calendar-day-header">Sun</div>
              <div className="calendar-day-header">Mon</div>
              <div className="calendar-day-header">Tue</div>
              <div className="calendar-day-header">Wed</div>
              <div className="calendar-day-header">Thu</div>
              <div className="calendar-day-header">Fri</div>
              <div className="calendar-day-header">Sat</div>

              {(() => {
                const firstDay = new Date(currentYear, currentMonth - 1, 1);
                const startingDay = firstDay.getDay();
                const days = [];

                for (let i = 0; i < startingDay; i++) {
                  days.push(<div key={`empty-${i}`} className="calendar-day empty" />);
                }

                calendarData.days.forEach((day, index) => {
                  const date = new Date(day.date + 'T00:00:00');
                  const isViewingToday = date.toDateString() === new Date().toDateString();
                  const isSelected = selectedCalendarDate && date.toDateString() === selectedCalendarDate.toDateString();
                  days.push(
                    <div
                      key={index}
                      className={`calendar-day ${isViewingToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
                      style={{
                        backgroundColor: getCompletionColor(day.goals_completed, day.goals_total),
                      }}
                      onClick={() => loadDayView(date)}
                      title={`${day.goals_completed}/${day.goals_total} goals completed${day.is_frozen ? ' (Frozen)' : ''}`}
                    >
                      <span className="day-number">{date.getDate()}</span>
                      {day.goals_completed > 0 && (
                        <span className="day-count">{day.goals_completed}/{day.goals_total}</span>
                      )}
                      {day.is_frozen && <span className="freeze-icon">❄️</span>}
                    </div>
                  );
                });

                return days;
              })()}
            </div>
          )}

          <div className="calendar-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e0e0e0' }}></div>
              <span>No goals</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#ffd700' }}></div>
              <span>Some goals</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#ffa500' }}></div>
              <span>Most goals</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#4caf50' }}></div>
              <span>All goals</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
