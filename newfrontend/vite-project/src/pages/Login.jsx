import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function Login({ setPage }) {
  const { login }    = useAuth();
  const { dark, toggle } = useTheme();
  const [form, setForm]       = useState({ email: "", password: "" });
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleSubmit = () => {
    if (!form.email || !form.password) { setError("Please fill in all fields."); return; }
    setLoading(true);
    setTimeout(() => {
      login({ name: form.email.split("@")[0], email: form.email });
      setPage("dashboard");
    }, 900);
  };

  const base = dark
    ? "bg-[#080c14] text-white"
    : "bg-gradient-to-br from-slate-50 via-cyan-50/20 to-white text-slate-900";

  const card = dark
    ? "bg-[#0d1322] border-white/[0.08]"
    : "bg-white border-slate-200/70 shadow-xl shadow-slate-200/50";

  const input = dark
    ? "bg-[#080c14] border-white/[0.08] text-slate-200 placeholder-slate-600 focus:border-cyan-500/50"
    : "bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:border-cyan-400";

  return (
    <div className={`min-h-screen flex items-center justify-center px-6 py-12 transition-colors duration-300 ${base}`}>
      {/* Theme toggle top right */}
      <button onClick={toggle} className={`fixed top-4 right-4 w-10 h-10 rounded-xl flex items-center justify-center text-lg z-50 transition-all ${dark ? "bg-white/[0.07]" : "bg-white border border-slate-200 shadow-sm"}`}>
        {dark ? "☀️" : "🌙"}
      </button>

      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <button onClick={() => setPage("landing")} className="inline-flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-3xl shadow-xl shadow-cyan-500/25">🧠</div>
            <span className={`font-extrabold text-xl ${dark ? "text-white" : "text-slate-800"}`}>
              Mind<span className="text-cyan-500">Safe</span> AI
            </span>
          </button>
          <h1 className={`text-2xl font-extrabold mt-4 mb-1 ${dark ? "text-white" : "text-slate-800"}`}>Welcome back</h1>
          <p className={`text-sm ${dark ? "text-slate-500" : "text-slate-400"}`}>Login to your account</p>
        </div>

        <div className={`rounded-3xl border p-8 transition-colors ${card}`}>
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className={`block text-sm font-semibold mb-2 ${dark ? "text-slate-300" : "text-slate-600"}`}>Email Address</label>
              <input type="email" placeholder="you@example.com" value={form.email}
                onChange={e => { setForm({...form, email: e.target.value}); setError(""); }}
                className={`w-full rounded-xl border px-4 py-3 text-sm outline-none transition-colors ${input}`} />
            </div>
            <div>
              <label className={`block text-sm font-semibold mb-2 ${dark ? "text-slate-300" : "text-slate-600"}`}>Password</label>
              <div className="relative">
                <input type={showPass ? "text" : "password"} placeholder="Enter your password" value={form.password}
                  onChange={e => { setForm({...form, password: e.target.value}); setError(""); }}
                  className={`w-full rounded-xl border px-4 py-3 text-sm outline-none transition-colors pr-12 ${input}`} />
                <button onClick={() => setShowPass(!showPass)} className={`absolute right-3 top-1/2 -translate-y-1/2 text-base ${dark ? "text-slate-500" : "text-slate-400"}`}>
                  {showPass ? "🙈" : "👁️"}
                </button>
              </div>
            </div>
          </div>

          <button onClick={handleSubmit} disabled={loading}
            className="w-full mt-6 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-500/25 hover:-translate-y-0.5 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none">
            {loading ? "Logging in..." : "Login →"}
          </button>

          <div className={`flex items-center gap-3 my-5 ${dark ? "text-slate-600" : "text-slate-300"}`}>
            <div className="flex-1 h-px bg-current" />
            <span className="text-xs">OR</span>
            <div className="flex-1 h-px bg-current" />
          </div>

          <p className={`text-center text-sm ${dark ? "text-slate-500" : "text-slate-400"}`}>
            Don't have an account?{" "}
            <button onClick={() => setPage("register")} className="text-cyan-500 font-bold hover:text-cyan-400 transition-colors">
              Register here
            </button>
          </p>
        </div>

        <button onClick={() => setPage("landing")} className={`w-full mt-4 text-center text-xs transition-colors ${dark ? "text-slate-600 hover:text-slate-400" : "text-slate-400 hover:text-slate-600"}`}>
          ← Back to Home
        </button>
      </div>
    </div>
  );
}
