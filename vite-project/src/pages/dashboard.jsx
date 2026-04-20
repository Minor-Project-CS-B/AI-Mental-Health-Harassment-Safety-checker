import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer, RadialBarChart, RadialBar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell
} from 'recharts';
import { ShieldAlert, MessageSquare, ClipboardCheck, Lightbulb, Phone } from 'lucide-react';
import { getDashboard, getAssessmentHistory, getLatestResponse } from '../services/api';
import Navbar from '../components/Navbar';

const theme = {
  card: "bg-white rounded-[2.5rem] shadow-xl p-8 border border-slate-100",
};

// ── Exact same data as backend response_generator.py ─────────────────────
const SUGGESTIONS = {
  low: {
    mental_health: [
      "Practice 5 minutes of deep breathing daily (inhale 4s, hold 4s, exhale 4s).",
      "Keep a short gratitude journal — write 3 positive things each evening.",
      "Stay physically active: even a 20-minute walk improves mood significantly.",
      "Maintain a consistent sleep schedule for better emotional balance.",
      "Reach out to a friend or family member you haven't spoken to in a while.",
    ],
    harassment: [
      "Be aware of your surroundings, especially in unfamiliar or isolated places.",
      "Save emergency contacts on your phone for quick access.",
      "Trust your instincts — if something feels wrong, move to a safer space.",
      "Talk to a trusted friend or family member about your experiences.",
    ],
  },
  medium: {
    mental_health: [
      "Try CBT journaling: write down a negative thought, then challenge it with evidence.",
      "Reach out to a counselor, mentor, or campus/workplace wellness program.",
      "Use grounding: name 5 things you see, 4 you can touch, 3 you hear.",
      "Limit social media if it's increasing your anxiety or feelings of inadequacy.",
      "Schedule one small enjoyable activity each day — even 10 minutes of a hobby helps.",
    ],
    harassment: [
      "Document every incident: date, time, location, what happened, any witnesses.",
      "Speak to a trusted authority figure (teacher, HR, campus coordinator).",
      "Avoid being alone with the person causing harm if possible.",
      "Block the person on all digital platforms if harassment is online.",
      "Seek support from a counselor or peer support group.",
    ],
  },
  high: {
    mental_health: [
      "Please contact a mental health helpline immediately — see the resources below.",
      "Tell a trusted person how you're feeling right now — do not be alone.",
      "If you are in immediate danger to yourself, go to the nearest hospital emergency.",
      "Avoid alcohol and substances, which can intensify distress.",
    ],
    harassment: [
      "If you are in immediate physical danger, call 112 (India emergency) now.",
      "Move to a safe location as soon as possible.",
      "Preserve all evidence: screenshots, messages — do not delete anything.",
      "File a complaint at the nearest police station or online at cybercrime.gov.in.",
    ],
  },
};

const MESSAGES = {
  low: {
    mental_health: "You're doing well for checking in with yourself. Small daily habits make a big difference.",
    harassment: "You seem safe right now. Stay aware of your surroundings and trust your instincts.",
  },
  medium: {
    mental_health: "It sounds like you're going through a tough time. You're not alone — support is available.",
    harassment: "What you're experiencing sounds difficult and unfair. You deserve to feel safe.",
  },
  high: {
    mental_health: "We're genuinely concerned about your wellbeing. Please reach out to a helpline immediately.",
    harassment: "Your safety is the top priority. If you are in immediate danger, contact emergency services (112).",
  },
};

const RESOURCES = {
  low: [
    { title: "Vandrevala Foundation", desc: "24/7 mental health helpline.", contact: "1860-2662-345" },
    { title: "Mindfulness India", desc: "Free guided meditation.", url: "https://www.artofliving.org" },
  ],
  medium: [
    { title: "iCall – TISS", desc: "Psychosocial helpline for students.", contact: "9152987821", url: "https://icallhelpline.org" },
    { title: "Vandrevala Foundation", desc: "24/7 mental health helpline.", contact: "1860-2662-345" },
    { title: "NIMHANS", desc: "National Mental Health helpline.", contact: "080-46110007" },
    { title: "Women Helpline", desc: "National helpline for women.", contact: "181" },
  ],
  high: [
    { title: "Emergency Services", desc: "Call immediately if in danger.", contact: "112" },
    { title: "iCall – TISS", desc: "Psychosocial helpline.", contact: "9152987821", url: "https://icallhelpline.org" },
    { title: "Vandrevala Foundation", desc: "24/7 mental health helpline.", contact: "1860-2662-345" },
    { title: "Women Helpline", desc: "National helpline for women.", contact: "181" },
    { title: "Cyber Crime", desc: "Report online harassment.", url: "https://cybercrime.gov.in" },
  ],
};

const RISK_COLORS = {
  LOW:    { dot: "bg-emerald-400", badge: "bg-emerald-100 text-emerald-700", bar: "#10b981", tip: "bg-emerald-50 border-emerald-100" },
  MEDIUM: { dot: "bg-amber-400",   badge: "bg-amber-100 text-amber-700",     bar: "#f59e0b", tip: "bg-amber-50 border-amber-100"   },
  HIGH:   { dot: "bg-red-400",     badge: "bg-red-100 text-red-700",         bar: "#ef4444", tip: "bg-red-50 border-red-100"       },
};

// ── Tips Section Component ────────────────────────────────────────────────
function TipsSection({ riskLevel, track }) {
  const level  = riskLevel?.toLowerCase() || "low";
  const trk    = track?.includes("harassment") ? "harassment" : "mental_health";
  const tips   = SUGGESTIONS[level]?.[trk] || SUGGESTIONS.low.mental_health;
  const msg    = MESSAGES[level]?.[trk]    || MESSAGES.low.mental_health;
  const res    = RESOURCES[level]          || RESOURCES.low;
  const colors = RISK_COLORS[riskLevel]    || RISK_COLORS.LOW;

  const [activeIdx, setActiveIdx] = useState(0);

  return (
    <div className={`${theme.card} p-6`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Lightbulb size={20} className="text-indigo-500" />
          <h3 className="text-xl font-black text-slate-800">
            AI Tips For You
          </h3>
        </div>
        <span className={`text-xs font-black px-3 py-1.5 rounded-full ${colors.badge}`}>
          {riskLevel} RISK
        </span>
      </div>

      {/* Support message */}
      <p className="text-slate-500 text-sm leading-relaxed mb-5 border-l-4 pl-3"
        style={{ borderColor: colors.bar }}>
        {msg}
      </p>

      {/* Tips grid — 2 columns, compact */}
      <div className="grid md:grid-cols-2 gap-2 mb-5">
        {tips.map((tip, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.07 }}
            className={`flex items-start gap-2.5 rounded-2xl px-4 py-3 border text-sm text-slate-700 leading-snug cursor-pointer transition-all ${
              activeIdx === i
                ? `${colors.tip} border-opacity-100 shadow-sm`
                : "bg-slate-50 border-slate-100 hover:bg-slate-100"
            }`}
            onClick={() => setActiveIdx(i)}
          >
            <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${colors.dot}`} />
            {tip}
          </motion.div>
        ))}
      </div>

      {/* Resources — horizontal scrollable pills */}
      <div>
        <div className="flex items-center gap-1.5 mb-2">
          <Phone size={13} className="text-slate-400" />
          <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Quick Resources</span>
        </div>
        <div className="flex gap-2 flex-wrap">
          {res.map((r, i) => (
            <a
              key={i}
              href={r.contact ? `tel:${r.contact}` : r.url}
              target={r.url ? "_blank" : undefined}
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white transition-opacity hover:opacity-80"
              style={{ background: "linear-gradient(135deg,#06b6d4,#0d9488)" }}
            >
              {r.contact ? "📞" : "🌐"} {r.title}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────
const Dashboard = () => {
  const navigate = useNavigate();
  const [data,         setData]         = useState(null);
  const [assessHist,   setAssessHist]   = useState([]);
  const [latestResp,   setLatestResp]   = useState(null);
  const [loading,      setLoading]      = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboard(),
      getAssessmentHistory().catch(() => ({ data: { history: [] } })),
      getLatestResponse().catch(() => ({ data: { response: null } })),
    ]).then(([dashRes, histRes, respRes]) => {
      if (!dashRes.data.onboarding_complete) { navigate('/onboarding'); return; }
      setData(dashRes.data);
      setAssessHist(histRes.data.history || []);
      setLatestResp(respRes.data.response || null);
    })
    .catch(err => console.error('Dashboard error:', err))
    .finally(() => setLoading(false));
  }, [navigate]);

  // Build chart data from REAL backend sentiment_history.
  // sentiment_history is an array of { mood: 0-100, label, time } from chat messages.
  // Falls back to risk-score-derived estimates if no chat data exists yet.
  const buildChartData = () => {
    const sh = data?.sentiment_history || [];
    const rh = data?.risk_history      || [];

    if (sh.length === 0 && rh.length === 0) {
      // No data at all — return placeholder that explains what will appear
      return [
        { factor: 'Complete a chat', score: 0, fill: '#e2e8f0' },
      ];
    }

    // Average mood from real chat sentiment (0-100 scale)
    const avgMood = sh.length > 0
      ? sh.reduce((sum, m) => sum + m.mood, 0) / sh.length
      : 50;

    // Average risk from assessment history (already 0-100)
    const avgRisk = rh.length > 0
      ? rh.reduce((sum, r) => sum + r.score, 0) / rh.length
      : (data?.risk_score || 0) * 100;

    return [
      { factor: 'Mood',       score: Math.round(avgMood),                      fill: '#86efac' },
      { factor: 'Wellbeing',  score: Math.round(Math.max(100 - avgRisk, 10)),   fill: '#a7f3d0' },
      { factor: 'Stress',     score: Math.round(Math.min(avgRisk + 5,  95)),    fill: '#fca5a5' },
      { factor: 'Risk',       score: Math.round(Math.min(avgRisk, 95)),         fill: '#fdba74' },
    ];
  };

  const riskLevel  = data?.current_risk_level?.toUpperCase() || "LOW";
  const scoreValue = Math.round((data?.risk_score || 0) * 100);
  const gaugeData  = [
    { name: 'Max',   value: 100,        fill: '#f1f5f9' },
    { name: 'Score', value: scoreValue, fill: riskLevel === 'HIGH' ? '#ef4444' : '#4f46e5' },
  ];

  // Detect track from recent assessments
  const latestTrack = data?.recent_assessments?.[0]?.track || "mental_health";

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <main className="p-6 lg:p-10 max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">

          {/* ── HEADER ── */}
          <header>
            <h2 className="text-4xl font-black text-slate-800 tracking-tight">
              Welcome back, {data?.name || 'User'} 👋
            </h2>
            <p className="text-slate-500 font-medium mt-1 text-lg">
              Your wellbeing overview based on AI analysis.
            </p>
          </header>

          {/* ── ROW 1: Gauge + Bar Chart (same as before) ── */}
          <div className="grid lg:grid-cols-5 gap-8">

            {/* LEFT: Risk Gauge */}
            <div className={`${theme.card} lg:col-span-2 flex flex-col items-center justify-center text-center relative overflow-hidden`}>
              <h3 className="text-2xl font-black text-slate-800 mb-4">Safety Analysis</h3>
              <div className="w-full h-64 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%"
                    barSize={20} data={gaugeData} startAngle={180} endAngle={0}>
                    <RadialBar dataKey="value" cornerRadius={10} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center top-8">
                  <span className="text-xs text-slate-400 font-bold uppercase tracking-widest">Risk Level</span>
                  <span className={`text-5xl font-black mt-2 ${riskLevel === 'HIGH' ? 'text-red-600' : 'text-indigo-700'}`}>
                    {riskLevel}
                  </span>
                  <span className="text-lg font-bold text-slate-500 mt-1">{scoreValue}%</span>
                </div>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed px-4">
                AI has analyzed your recent patterns. Risk level is <strong>{riskLevel.toLowerCase()}</strong>.
              </p>
            </div>

            {/* RIGHT: Sentiment Bar Chart */}
            <div className={`${theme.card} lg:col-span-3`}>
              <h3 className="text-2xl font-black text-slate-800 mb-6">Sentiment Trends</h3>
              <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={buildChartData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="factor" axisLine={false} tickLine={false}
                      tick={{ fill: '#64748b', fontSize: 13 }} />
                    <YAxis domain={[0, 100]} hide />
                    <Tooltip
                      cursor={{ fill: 'rgba(79,70,229,0.05)' }}
                      contentStyle={{ borderRadius: '1rem', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}
                    />
                    <Bar dataKey="score" radius={[10, 10, 0, 0]}>
                      {buildChartData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* ── ROW 2: Stats + Tips side by side ── */}
          <div className="grid lg:grid-cols-5 gap-8">

            {/* LEFT: Quick Stats (2x2 grid) + Action cards */}
            <div className="lg:col-span-2 flex flex-col gap-4">

              {/* Stats 2x2 */}
              <div className="grid grid-cols-2 gap-4">
                <div className={`${theme.card} p-5 text-center`}>
                  <p className="text-slate-400 text-xs font-bold uppercase mb-1">Total Chats</p>
                  <p className="text-2xl font-black text-slate-800">{data?.total_chats || 0}</p>
                </div>
                <div className={`${theme.card} p-5 text-center`}>
                  <p className="text-slate-400 text-xs font-bold uppercase mb-1">Assessments</p>
                  <p className="text-2xl font-black text-slate-800">{data?.total_assessments || 0}</p>
                </div>
                <div className={`${theme.card} p-5 text-center`}>
                  <p className="text-slate-400 text-xs font-bold uppercase mb-1">Last Active</p>
                  <p className="text-sm font-bold text-slate-800">
                    {data?.last_active ? new Date(data.last_active).toLocaleDateString() : 'Today'}
                  </p>
                </div>
                <div className={`${theme.card} p-5 text-center border-indigo-100 bg-indigo-50/30`}>
                  <p className="text-indigo-400 text-xs font-bold uppercase mb-1">Status</p>
                  <p className="text-xs font-black text-indigo-600 tracking-tight italic">SECURE ✓</p>
                </div>
              </div>

              {/* Action buttons */}
              <button
                onClick={() => navigate('/chat')}
                className="bg-indigo-600 p-6 rounded-[2rem] text-white shadow-xl hover:scale-[1.02] transition-all text-left flex items-center gap-4"
              >
                <MessageSquare size={28} />
                <div>
                  <h3 className="text-lg font-bold">AI Support Chat</h3>
                  <p className="text-indigo-100 text-sm">Talk to our safety-trained AI.</p>
                </div>
              </button>

              <button
                onClick={() => navigate('/assessment')}
                className="bg-white p-6 rounded-[2rem] shadow-lg border border-slate-100 hover:scale-[1.02] transition-all text-left flex items-center gap-4"
              >
                <ClipboardCheck size={28} className="text-indigo-600" />
                <div>
                  <h3 className="text-lg font-bold text-slate-800">New Assessment</h3>
                  <p className="text-slate-500 text-sm">Update your wellbeing profile.</p>
                </div>
              </button>

              <div className="bg-red-50 p-6 rounded-[2rem] border border-red-100 flex items-center gap-4">
                <ShieldAlert size={28} className="text-red-600 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-bold text-red-800">SOS Helpline</h3>
                  <a href="tel:9152987821" className="text-red-600 font-black text-base underline">
                    iCall: 9152987821
                  </a>
                </div>
              </div>
            </div>

            {/* RIGHT: Tips Section — takes remaining 3 cols */}
            <div className="lg:col-span-3">
              <TipsSection
                riskLevel={riskLevel}
                track={latestTrack}
              />
            </div>
          </div>

        </motion.div>
      </main>
    </div>
  );
};

export default Dashboard;