import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
// 1. Import the register function from your api service
import { register } from '../services/api';

const Register = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ 
    fullName: '',
    username: '', 
    email: '', 
    password: '' 
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // const handleRegister = async (e) => {
  //   e.preventDefault();
  //   setLoading(true);
  //   setError("");
    
  //   try {
  //     // 2. Map frontend state to Backend Schema keys
  //     await register({
  //       full_name: form.fullName, // Backend expects full_name
  //       username: form.username,
  //       email: form.email,
  //       password: form.password
  //     });
      
  //     // If successful, send them to login
  //     navigate('/login');
  //   } catch (err) {
  //     // Show specific error from backend (e.g., "Email already registered")
  //     setError(err.response?.data?.detail || "Registration failed. Please try again.");
  //   } finally {
  //     setLoading(false);
  //   }
  // };


  const handleRegister = async (e) => {
  e.preventDefault();
  setLoading(true);
  setError("");
  
  try {
    // MATCHING SWAGGER SCHEMA
    await register({
      name: form.fullName,     // Backend expects "name", not "full_name"
      username: form.username, // Matches
      email: form.email,       // Matches
      password: form.password  // Matches
    });
    navigate('/login');
  } catch (err) {
    // FIX FOR REACT CRASH: Extract only the message string
    // FastAPI sends errors in an array: err.response.data.detail[0].msg
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) {
      setError(detail[0].msg); 
    } else {
      setError(detail || "Registration failed.");
    }
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-sans">
      <div className="bg-white p-10 rounded-[2.5rem] shadow-xl border border-slate-100 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mx-auto flex items-center justify-center text-3xl mb-4 shadow-lg shadow-indigo-200">
            ✨
          </div>
          <h2 className="text-3xl font-extrabold text-slate-800">Create Account</h2>
          <p className="text-slate-500 font-medium mt-2">Start your safe AI journey</p>
        </div>

        {error && (
  <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-2xl text-sm border border-red-100">
    {/* By extracting detail[0].msg above, 'error' is now a string! */}
    ⚠️ {String(error)} 
  </div>
)}

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Full Name</label>
            <input 
              type="text" 
              placeholder="John Doe"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              value={form.fullName}
              onChange={(e) => setForm({...form, fullName: e.target.value})}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Username</label>
            <input 
              type="text" 
              placeholder="johndoe123"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              value={form.username}
              onChange={(e) => setForm({...form, username: e.target.value})}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Email Address</label>
            <input 
              type="email" 
              placeholder="name@example.com"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              value={form.email}
              onChange={(e) => setForm({...form, email: e.target.value})}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1.5 ml-1">Password</label>
            <input 
              type="password" 
              placeholder="••••••••"
              className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 outline-none focus:border-indigo-500 focus:bg-white transition-all"
              value={form.password}
              onChange={(e) => setForm({...form, password: e.target.value})}
              required
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            className={`w-full py-4 rounded-2xl font-bold text-lg text-white transition-all mt-4 ${loading ? 'bg-slate-400' : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200'}`}
          >
            {loading ? "Creating Account..." : "Sign Up →"}
          </button>
        </form>

        <p className="text-center mt-8 text-slate-500 font-medium">
          Already have an account? <Link to="/login" className="text-indigo-600 font-bold hover:underline">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;