

import axios from 'axios';

const api = axios.create({ 
  baseURL: 'http://127.0.0.1:8000' 
});

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

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

/* --- Authentication --- */
export const register        = (data)  => api.post('/auth/register', data);
export const verifyMagicLink = (token) => api.post('/auth/verify-magic-link', { token });
export const getMe           = ()      => api.get('/auth/me');
export const requestLink     = (email) => api.post(`/auth/request-link?email=${email}`);

export const login = (username, password) => {
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);
  return api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
};

/* --- Onboarding --- */
export const getOnboardingQuestions = ()     => api.get('/onboarding/questions');
export const submitOnboarding       = (data) => api.post('/onboarding/submit', data);

/* --- Assessment --- */
export const getAssessmentQuestions = (track) => api.get(`/assessment/generate/${track}`);
export const submitAssessment        = (data)  => api.post('/assessment/submit', data);
export const getAssessmentHistory    = ()      => api.get('/assessment/history');

/* --- Chat --- */
export const startChat      = ()     => api.get('/chat/start');
export const sendMessage    = (data) => api.post('/chat/message', data);
export const getChatHistory = ()     => api.get('/chat/history');
export const getEvidence    = ()     => api.get('/chat/evidence');

export const uploadImageEvidence = (formData) =>
  api.post('/chat/upload-evidence/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

export const uploadVideoEvidence = (formData) =>
  api.post('/chat/upload-evidence/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

export const voiceToText = (formData) =>
  api.post('/chat/voice-to-text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

/* --- Dashboard & Help --- */
export const getDashboard = () => api.get('/dashboard/');
export const getHelp      = () => api.get('/help/');
export const getEmergency = () => api.get('/help/emergency');

/* --- Dynamic Response Generator --- */
export const generateResponse   = (data) => api.post('/response/generate', data);
export const getLatestResponse  = ()     => api.get('/response/latest');
export const getResponseHistory = ()     => api.get('/response/history');

export default api;