import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth APIs
export const authAPI = {
  register: (data: { email: string; password: string; name: string }) => 
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) => 
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Goals APIs
export const goalsAPI = {
  getAll: () => api.get('/goals'),
  create: (data: { title: string; description?: string; is_recurring?: boolean; scheduled_date?: string }) => 
    api.post('/goals', data),
  update: (id: number, data: { title?: string; description?: string; is_active?: boolean }) => 
    api.put(`/goals/${id}`, data),
  delete: (id: number) => api.delete(`/goals/${id}`),
  complete: (id: number, completion_date?: string) => {
    const body: any = {};
    if (completion_date) {
      body.completion_date = completion_date;
    }
    return api.post(`/goals/${id}/complete`, body);
  },
  getCompletions: () => api.get('/goals/completions'),
};

// SubGoals APIs
export const subgoalsAPI = {
  create: (data: { title: string; goal_id: number }) => 
    api.post('/subgoals', data),
  complete: (id: number, completion_date?: string) => {
    const body: any = {};
    if (completion_date) {
      body.completion_date = completion_date;
    }
    return api.put(`/subgoals/${id}/complete`, body);
  },
  uncomplete: (id: number, completion_date?: string) => {
    const body: any = {};
    if (completion_date) {
      body.completion_date = completion_date;
    }
    return api.put(`/subgoals/${id}/uncomplete`, body);
  },
  delete: (id: number) => api.delete(`/subgoals/${id}`),
};

// Stats APIs
export const statsAPI = {
  getStats: () => api.get('/stats'),
  purchaseFreeze: () => api.post('/freeze/purchase'),
  useFreeze: () => api.post('/freeze/use'),
};

// Calendar APIs
export const calendarAPI = {
  getMonth: (year: number, month: number) => 
    api.get(`/calendar/${year}/${month}`),
  getDay: (dateStr: string) => 
    api.get(`/day/${dateStr}`),
};

export default api;
