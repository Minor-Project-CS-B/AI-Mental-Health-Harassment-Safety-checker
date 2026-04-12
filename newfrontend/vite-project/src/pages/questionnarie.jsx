import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, CheckCircle, Brain, ShieldAlert, ArrowLeft, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { generateAssessment , submitAssessment } from '../services/api';
import Navbar from '../components/Navbar';

const Assessment = () => {
  const navigate = useNavigate();
  
  // Logic States
  const [track, setTrack] = useState(null);
  const [questions, setQs] = useState([]);
  const [answers, setAns] = useState({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  // 1. SELECT TRACK LOGIC (Backend Fetch)
  const selectTrack = async (t) => {
    setLoading(true);
    setErr(null);
    try {
      const r = await generateAssessment(t);
      setQs(r.data.questions);
      setTrack(t);
    } catch {
      setErr('Failed to load deep-dive questions.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = (option, score, emoji) => {
    const q = questions[currentIdx];
    setAns(prev => ({
      ...prev,
      [q.id]: { question_id: q.id, question_text: q.text, answer: option, score }
    }));
  };

  // 2. SUBMIT LOGIC (To Dashboard)
  const handleNext = async () => {
    const q = questions[currentIdx];
    if (!answers[q.id]) return;

    if (currentIdx < questions.length - 1) {
      setCurrentIdx(prev => prev + 1);
    } else {
      setLoading(true);
      try {
        await submitAssessment({ track, answers: Object.values(answers) });
        // Redirect to dashboard where the new logic-bridge charts will update
        navigate('/dashboard');
      } catch {
        setErr('Submission failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const reset = () => {
    setTrack(null);
    setQs([]);
    setAns({});
    setCurrentIdx(0);
  };

  // --- UI PART 1: TRACK SELECTION (Attractive Modern Cards) ---
  if (!track) return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-6 py-20">
        <header className="text-center mb-16">
          <motion.h2 
            initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
            className="text-5xl font-black text-slate-800 tracking-tight mb-4"
          >
            Choose Your <span className="text-indigo-600">Focus</span>
          </motion.h2>
          <p className="text-slate-500 text-lg font-medium">Select a specialized track for a deeper AI analysis.</p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {[
            { 
              id: 'mental_health', 
              label: 'Mental Wellbeing', 
              icon: <Brain size={40}/>, 
              color: 'bg-blue-600', 
              desc: 'Deep dive into stress patterns, mood fluctuations, and emotional resilience.',
              bg: 'bg-blue-50'
            },
            { 
              id: 'harassment', 
              label: 'Safety & Harassment', 
              icon: <ShieldAlert size={40}/>, 
              color: 'bg-rose-600', 
              desc: 'Secure assessment for workplace safety and social harassment concerns.',
              bg: 'bg-rose-50'
            }
          ].map((item) => (
            <motion.button
              whileHover={{ y: -20 }}
              whileTap={{ scale: 0.98 }}
              key={item.id}
              onClick={() => selectTrack(item.id)}
              className="relative group overflow-hidden bg-white p-10 rounded-[3rem] shadow-xl border border-slate-100 text-left transition-all"
            >
              <div className={`${item.bg} ${item.color.replace('bg-', 'text-')} w-20 h-20 rounded-[2rem] flex items-center justify-center mb-8 transition-transform group-hover:rotate-12`}>
                {item.icon}
              </div>
              <h3 className="text-3xl font-bold text-slate-800 mb-4">{item.label}</h3>
              <p className="text-slate-500 leading-relaxed mb-8">{item.desc}</p>
              <div className="flex items-center gap-2 font-bold text-indigo-600">
                Start Track <ChevronRight size={20} />
              </div>
              {/* Decorative background element */}
              <div className={`absolute -right-4 -bottom-4 w-24 h-24 ${item.color} opacity-5 rounded-full`} />
            </motion.button>
          ))}
        </div>
        {err && <p className="text-center mt-8 text-red-500 font-bold">⚠️ {err}</p>}
      </div>
    </div>
  );

  // --- UI PART 2: QUESTION FLOW (Clean, Minimalist, Animated) ---
  const q = questions[currentIdx];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-[3rem] shadow-2xl p-12 border border-slate-100 w-full max-w-4xl relative"
        >
          {/* Back Button */}
          <button onClick={reset} className="absolute top-10 left-10 flex items-center gap-1 text-slate-400 font-bold hover:text-indigo-600 transition-colors">
            <ArrowLeft size={18} /> BACK
          </button>

          <div className="text-center mb-12">
            <span className="bg-indigo-50 text-indigo-600 px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">
              {track.replace('_', ' ')}
            </span>
            <div className="flex justify-center gap-2 mt-6 mb-2">
              {questions.map((_, i) => (
                <div key={i} className={`h-1.5 rounded-full transition-all duration-500 ${i <= currentIdx ? 'w-8 bg-indigo-600' : 'w-2 bg-slate-100'}`} />
              ))}
            </div>
            <p className="text-slate-400 font-bold text-sm">Question {currentIdx + 1} of {questions.length}</p>
          </div>

          <div className="min-h-[160px] flex items-center justify-center text-center px-4 mb-12">
            <AnimatePresence mode="wait">
              <motion.h3 
                key={currentIdx}
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
                className="text-4xl font-black text-slate-800 leading-tight"
              >
                {q?.text}
              </motion.h3>
            </AnimatePresence>
          </div>

          {/* Options (Using Emoji & Scores from Backend) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
            {q?.options.map((opt, i) => {
              const selected = answers[q.id]?.answer === opt;
              return (
                <button
                  key={i}
                  onClick={() => handleSelectAnswer(opt, q.scores[i], q.emoji[i])}
                  className={`py-6 px-8 rounded-[2rem] font-bold text-lg transition-all border-2 flex items-center justify-between ${
                    selected 
                    ? "bg-indigo-600 border-indigo-600 text-white shadow-xl scale-[1.02]" 
                    : "bg-slate-50 border-transparent text-slate-600 hover:border-indigo-200"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-2xl bg-white/10 p-2 rounded-xl">{q.emoji[i]}</span>
                    {opt}
                  </div>
                  {selected && <CheckCircle size={24} />}
                </button>
              );
            })}
          </div>

          <div className="flex justify-center">
            <button 
              onClick={handleNext}
              disabled={!answers[q?.id] || loading}
              className="group bg-slate-900 text-white px-16 py-5 rounded-[2rem] font-black text-xl flex items-center gap-3 shadow-2xl hover:bg-indigo-600 transition-all disabled:opacity-20 disabled:grayscale"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              ) : (
                <>
                  {currentIdx === questions.length - 1 ? 'Analyze My Profile' : 'Continue'}
                  <ChevronRight size={24} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Assessment;