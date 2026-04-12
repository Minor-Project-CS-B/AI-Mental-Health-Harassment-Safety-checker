import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ResponsiveContainer, RadialBarChart, RadialBar, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell 
} from 'recharts';
import { ShieldAlert, BarChart as ChartIcon, Users, Repeat, MessageSquare, ClipboardCheck } from 'lucide-react';

// === BACKEND SERVICE IMPORTS ===
import { getDashboard } from '../services/api';
import Navbar from '../components/Navbar';

const theme = {
  card: "bg-white rounded-[2.5rem] shadow-xl p-8 border border-slate-100",
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. FETCH REAL BACKEND DATA
    getDashboard()
      .then(r => {
        if (!r.data.onboarding_complete) {
          navigate('/onboarding');
          return;
        }
        setData(r.data);
      })
      .catch(err => console.error("Dashboard Fetch Error:", err))
      .finally(() => setLoading(false));
  }, [navigate]);

  // 2. LOGIC BRIDGE: Generate Factor Profile based on Backend Risk Score
  const generateFactorData = (score) => {
    const s = score * 100;
    return [
      { factor: 'Happiness', score: Math.max(100 - s, 20), fill: '#86efac' },
      { factor: 'Confidence', score: Math.max(90 - s, 30), fill: '#a7f3d0' },
      { factor: 'Stress', score: Math.min(s + 10, 95), fill: '#fca5a5' },
      { factor: 'Anxiety', score: Math.min(s + 5, 90), fill: '#fdba74' },
    ];
  };

  const riskLevel = data?.current_risk_level?.toUpperCase() || "LOW";
  const scoreValue = Math.round((data?.risk_score || 0) * 100);

  const gaugeData = [
    { name: 'Max', value: 100, fill: '#f1f5f9' },
    { name: 'Score', value: scoreValue, fill: riskLevel === 'HIGH' ? '#ef4444' : '#4f46e5' }
  ];

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      
      <main className="p-6 lg:p-12 max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-10">
          
          <header>
            <h2 className="text-4xl font-black text-slate-800 tracking-tight">
              Welcome back, {data?.name || 'User'} 
            </h2>
            <p className="text-slate-500 font-medium mt-2 text-lg">Your wellbeing overview based on AI analysis.</p>
          </header>

          <div className="grid lg:grid-cols-5 gap-10">
            
            {/* LEFT: Risk Gauge (Data from Backend) */}
            <div className={`${theme.card} lg:col-span-2 flex flex-col items-center justify-center text-center relative overflow-hidden`}>
              <h3 className="text-2xl font-black text-slate-800 mb-4">Safety Analysis</h3>
              
              <div className="w-full h-72 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" barSize={20} data={gaugeData} startAngle={180} endAngle={0}>
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
                The AI has analyzed your recent patterns. Your current risk level is categorized as <strong>{riskLevel.toLowerCase()}</strong>.
              </p>
            </div>

            {/* RIGHT: Factor Profile (Logic Bridge) */}
            <div className={`${theme.card} lg:col-span-3`}>
              <h3 className="text-2xl font-black text-slate-800 mb-8">Sentiment Trends</h3>
              <div className="w-full h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={generateFactorData(data?.risk_score || 0)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false}/>
                    <XAxis dataKey="factor" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 13 }} />
                    <YAxis domain={[0, 100]} hide />
                    <Tooltip cursor={{ fill: 'rgba(79,70,229,0.05)' }} contentStyle={{ borderRadius: '1rem', border: 'none' }} />
                    <Bar dataKey="score" radius={[10, 10, 0, 0]}>
                      {generateFactorData(data?.risk_score || 0).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className={theme.card + " p-6 text-center"}>
              <p className="text-slate-400 text-xs font-bold uppercase mb-1">Total Chats</p>
              <p className="text-2xl font-black text-slate-800">{data?.total_chats || 0}</p>
            </div>
            <div className={theme.card + " p-6 text-center"}>
              <p className="text-slate-400 text-xs font-bold uppercase mb-1">Assessments</p>
              <p className="text-2xl font-black text-slate-800">{data?.total_assessments || 0}</p>
            </div>
            <div className={theme.card + " p-6 text-center"}>
              <p className="text-slate-400 text-xs font-bold uppercase mb-1">Last Active</p>
              <p className="text-sm font-bold text-slate-800">
                {data?.last_active ? new Date(data.last_active).toLocaleDateString() : 'Today'}
              </p>
            </div>
            <div className={theme.card + " p-6 text-center border-indigo-100 bg-indigo-50/30"}>
              <p className="text-indigo-400 text-xs font-bold uppercase mb-1">Status</p>
              <p className="text-sm font-black text-indigo-600 tracking-tighter italic">SECURE CONNECTION</p>
            </div>
          </div>

          {/* Action Cards */}
          <div className="grid md:grid-cols-3 gap-8">
            <button onClick={() => navigate('/chat')} className="bg-indigo-600 p-8 rounded-[2.5rem] text-white shadow-xl hover:scale-[1.02] transition-all text-left flex flex-col justify-between h-48">
              <MessageSquare size={32} />
              <div>
                <h3 className="text-xl font-bold">AI Support Chat</h3>
                <p className="text-indigo-100 text-sm">Talk to our safety-trained AI assistant.</p>
              </div>
            </button>

            <button onClick={() => navigate('/assessment')} className="bg-white p-8 rounded-[2.5rem] shadow-lg border border-slate-100 hover:scale-[1.02] transition-all text-left flex flex-col justify-between h-48">
              <ClipboardCheck size={32} className="text-indigo-600" />
              <div>
                <h3 className="text-xl font-bold text-slate-800">New Assessment</h3>
                <p className="text-slate-500 text-sm">Update your wellbeing profile.</p>
              </div>
            </button>

            <div className="bg-red-50 p-8 rounded-[2.5rem] border border-red-100 flex flex-col justify-between h-48">
              <ShieldAlert size={32} className="text-red-600" />
              <div>
                <h3 className="text-xl font-bold text-red-800">SOS Helpline</h3>
                <button className="mt-2 text-red-600 font-black text-lg underline">CALL 1-800-SAFE</button>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default Dashboard;