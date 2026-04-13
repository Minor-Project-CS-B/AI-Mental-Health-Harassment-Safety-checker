import React, { useEffect, useRef } from "react";
import logo from '../assets/logo minor.jpg'; 

const stats = [
  { val: "10K+", label: "Users Helped" },
  { val: "95%",  label: "Accuracy Rate" },
  { val: "24/7", label: "AI Available" },
  { val: "100%", label: "Anonymous" },
];

const features = [
  { icon: "🧠", title: "Mental Health Check",     desc: "Detect stress, anxiety & depression through AI-powered assessment." },
  { icon: "🛡️", title: "Harassment Safety",       desc: "Identify unsafe situations and get immediate safety guidance." },
  { icon: "💬", title: "AI Chat Support",           desc: "Talk to our empathetic AI anytime — text or voice." },
  { icon: "📊", title: "Risk Classification",     desc: "Intelligent Low / Medium / High risk scoring engine." },
  { icon: "🔒", title: "100% Private",            desc: "Anonymous usage, no permanent data storage." },
  { icon: "📞", title: "Helpline Access",           desc: "Instant access to verified emergency contacts." },
];

export default function Landing({ setPage }) {
  // Removed useTheme logic to prevent "undefined" error

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-teal-50/20 text-slate-900 font-sans">

      {/* NAV */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl border-b bg-white/80 border-slate-200/60 transition-colors duration-300">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">


      <div className="flex-shrink-0 flex items-center">
            <a href="/" className="flex items-center">
              <img 
                src={logo} 
                alt="AIMHHC logo" 
                className="h-10 w-auto mr-3 rounded-lg" 
              />
              <span className="font-bold text-xl text-gray-800 tracking-tight">
                AI<span className="text-blue-600">MH</span>HC
              </span>
            </a>
          </div>
          </div>


            {/* <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-lg shadow-lg shadow-cyan-500/25">🧠</div>
            <span className="font-extrabold text-lg tracking-tight text-slate-800">
              AI<span className="text-cyan-500">MH</span>HC
            </span>
          </div> */}
          <div className="flex items-center gap-3">
           
            <button  className="px-5 py-2 rounded-xl text-sm font-bold bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-500/25 hover:-translate-y-0.5 transition-all">
              <a href="/login" >Get Started</a>
            </button>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20 text-center relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase mb-8 border bg-cyan-50 border-cyan-200 text-cyan-600">
          ✦ AI-Powered · Anonymous · Confidential
        </div>

        <h1 className="text-6xl md:text-7xl font-extrabold leading-[1.08] mb-6 tracking-tight">
          Your Mind Deserves<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-400 to-cyan-500">
            Care & Safety
          </span>
        </h1>

        <p className="text-xl leading-relaxed max-w-2xl mx-auto mb-12 text-slate-500">
          An intelligent, compassionate AI tool that helps you assess your emotional well-being and personal safety — non-diagnostic, always private.
        </p>

        <div className="flex items-center justify-center gap-4 flex-wrap mb-16">
          <button onClick={() => setPage("register")} className="px-10 py-4 rounded-2xl font-bold text-base bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-xl shadow-cyan-500/30 hover:-translate-y-1 hover:shadow-cyan-500/50 transition-all duration-200">
            Start Free Assessment →
          </button>
          <button  className="px-10 py-4 rounded-2xl font-semibold text-base border-2 border-slate-200 text-slate-600 hover:bg-white transition-all hover:-translate-y-0.5">
            <a href="/login" > Already a member? Login</a>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
          {stats.map((s, i) => (
            <div key={i} className="rounded-2xl p-5 border bg-white border-slate-200/70 shadow-sm transition-colors">
              <div className="text-2xl font-extrabold text-cyan-500 mb-1">{s.val}</div>
              <div className="text-xs font-medium text-slate-400">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section className="border-t py-20 border-slate-100">
        <div className="max-w-6xl mx-auto px-6">
          <p className="text-xs font-bold uppercase tracking-widest text-center mb-3 text-slate-400">Everything you need</p>
          <h2 className="text-3xl font-extrabold text-center mb-12 text-slate-800">Powerful Features</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <div key={i} className="rounded-2xl p-6 border bg-white border-slate-200/70 hover:border-cyan-300 shadow-sm hover:shadow-md transition-all hover:-translate-y-1 cursor-default">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4 bg-cyan-50">{f.icon}</div>
                <div className="font-bold mb-2 text-sm text-slate-800">{f.title}</div>
                <div className="text-xs leading-relaxed text-slate-400">{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-t py-20 border-slate-100">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-3xl font-extrabold text-center mb-12 text-slate-800">How It Works</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
            {[
              { n: "01", t: "Register",      d: "Create a free anonymous account in seconds." },
              { n: "02", t: "Onboarding",     d: "Tell us a bit about yourself — age, gender, concerns." },
              { n: "03", t: "Assessment",     d: "Answer 10 simple AI-guided questions." },
              { n: "04", t: "Get Support",    d: "Receive personalized suggestions & helplines." },
            ].map((s) => (
              <div key={s.n} className="rounded-2xl p-6 border bg-white border-slate-200/70 shadow-sm transition-all">
                <div className="text-4xl font-extrabold text-cyan-500/25 mb-3">{s.n}</div>
                <div className="font-bold text-sm mb-2 text-slate-800">{s.t}</div>
                <div className="text-xs leading-relaxed text-slate-400">{s.d}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t py-20 border-slate-100">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <div className="rounded-3xl p-10 border bg-gradient-to-br from-cyan-50 to-teal-50 border-cyan-200">
            <h2 className="text-3xl font-extrabold mb-4 text-slate-800">Ready to Check In?</h2>
            <p className="mb-8 text-slate-500">Free. Anonymous. Takes less than 5 minutes.</p>
            <button onClick={() => setPage("register")} className="px-10 py-4 rounded-2xl font-bold bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-500/25 hover:-translate-y-1 transition-all">
              Get Started Free →
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t py-8 text-center border-slate-100">
        <p className="text-xs text-slate-400">MindSafe AI · Minor Project · Not a medical tool</p>
      </footer>
    </div>
  );
}