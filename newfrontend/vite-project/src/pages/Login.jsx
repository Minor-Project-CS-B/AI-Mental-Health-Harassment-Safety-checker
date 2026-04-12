import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
// === CONNECTION LINE: Import the login service ===

import { login } from '../services/api'; 

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 1. HIGHLIGHT: Call backend with form data
      const res = await login(form.username, form.password);
      
      // 2. HIGHLIGHT: Store the JWT token for future requests
      localStorage.setItem('token', res.data.access_token);
      
      // 3. HIGHLIGHT: Redirect to Onboarding upon success
      navigate('/onboarding');
    } catch (err) {
      // Extract specific error message to avoid React "Objects are not valid" crash
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : "Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="bg-white p-10 rounded-[2.5rem] shadow-xl border border-slate-100 w-full max-w-md">
        
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-slate-800">Welcome Back</h2>
          <p className="text-slate-500 mt-2">Login to continue your assessment</p>
        </div>

        {/* ERROR DISPLAY: Safely render as a string */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-2xl text-sm border border-red-100">
            ⚠️ {String(error)}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2 ml-1">Username</label>
            <input
              type="text"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-100 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              placeholder="Your username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2 ml-1">Password</label>
            <input
              type="password"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-100 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold text-lg shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all mt-4"
          >
            {loading ? "Authenticating..." : "Sign In →"}
          </button>
        </form>
   <div className="mt-6 text-center">
  <p className="text-gray-600 text-sm">
    Don't have an account?{' '}
    
      <a href="/register" className="text-indigo-600 font-bold hover:underline">Register</a>
      {/* <Link 
      to="/register" 
      className="text-blue-600 font-bold hover:underline transition-all"
    >
      Sign Up
    </Link> */}
  </p>
    </div>
         
      </div>
    </div>
  );
};

export default Login;