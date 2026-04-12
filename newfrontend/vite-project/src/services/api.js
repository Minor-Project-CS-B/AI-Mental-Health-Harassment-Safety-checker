import axios from 'axios';

// Create axios instance with your Backend URL
const api = axios.create({ 
  baseURL: 'http://127.0.0.1:8000' 
});

// Request Interceptor: Attach Token to every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// Response Interceptor: Handle Token Expiration
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

/* --- Authentication Endpoints --- */
// Supports Full Name, Username, Email, and Password
export const register = (data) => api.post('/auth/register', data);

// OAuth2 Password Grant (matches your Swagger login requirement)
export const login = (username, password) => {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  return api.post('/auth/login', form, { 
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' } 
  });
};

export const getMe = () => api.get('/auth/me');

/* --- Onboarding Endpoints --- */
export const getOnboardingQuestions = () => api.get('/onboarding/questions');
export const submitOnboarding = (data) => api.post('/onboarding/submit', data);

/* --- Assessment Endpoints (Mental Health vs Safety) --- */
// track: 'mental' or 'safety'
// Change 'generate' to 'questions' to match your Swagger docs
export const generateAssessment = (track) => api.get(`/assessment/questions/${track}`);
export const submitAssessment = (data) => api.post('/assessment/submit', data);
export const getAssessmentHistory = () => api.get('/assessment/history');

/* --- AI Chat & Evidence Endpoints --- */
export const startChat = () => api.get('/chat/start');
export const sendMessage = (data) => api.post('/chat/message', data);

// Media Uploads
export const uploadImageEvidence = (formData) => api.post('/chat/upload-evidence/image', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

export const voiceToText = (formData) => api.post('/chat/voice-to-text', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

/* --- Dashboard & Resources --- */
export const getDashboard = () => api.get('/dashboard/');
export const getHelp = () => api.get('/help/');
export const getEmergency = () => api.get('/help/emergency');

export default api;