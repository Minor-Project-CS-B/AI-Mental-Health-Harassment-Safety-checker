import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, Brain, ShieldAlert, ArrowLeft, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getAssessmentQuestions, submitAssessment } from '../services/api';
import Navbar from '../components/Navbar';


// ══════════════════════════════════════════════════════════════════════════════
// SCREEN 1: Generating Questions (shown after track selection)
// ══════════════════════════════════════════════════════════════════════════════

function GeneratingScreen({ track }) {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { label: 'Reading your conversation history', icon: '💬' },
    { label: 'Understanding your current state',  icon: '🧠' },
    { label: 'Personalizing your questions',      icon: '✨' },
    { label: 'Finalizing your assessment',        icon: '📋' },
  ];

  useEffect(() => {
    const iv = setInterval(() => setActiveStep(s => Math.min(s + 1, steps.length - 1)), 1800);
    return () => clearInterval(iv);
  }, []);

  const isMH      = track === 'mental_health';
  const accent    = isMH ? '#4f46e5' : '#e11d48';
  const accentBg  = isMH ? 'rgba(79,70,229,0.08)' : 'rgba(225,29,72,0.08)';
  const accentBdr = isMH ? 'rgba(79,70,229,0.25)' : 'rgba(225,29,72,0.25)';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-[3rem] shadow-2xl p-12 border border-slate-100 w-full max-w-xl text-center"
        >
          {/* Pulsing orb */}
          <div className="relative w-32 h-32 mx-auto mb-10">
            {[0, 1, 2].map(i => (
              <motion.div
                key={i}
                className="absolute inset-0 rounded-full"
                style={{ border: `2px solid ${accent}` }}
                animate={{ scale: [1, 1.6 + i * 0.3], opacity: [0.5, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.5, ease: 'easeOut' }}
              />
            ))}
            <div
              className="relative w-32 h-32 rounded-full flex items-center justify-center text-5xl shadow-xl"
              style={{ background: `linear-gradient(135deg, ${accent}, ${isMH ? '#7c3aed' : '#f97316'})` }}
            >
              {isMH ? '🧠' : '🛡️'}
            </div>
          </div>

          <h2 className="text-3xl font-black text-slate-800 tracking-tight mb-3">
            Building your assessment
          </h2>
          <p className="text-slate-500 font-medium mb-10 leading-relaxed">
            Our AI is crafting 10 personalized questions based on your profile and conversation history.
          </p>

          {/* Step list */}
          <div className="flex flex-col gap-3 mb-10 text-left">
            {steps.map((step, i) => {
              const done    = i < activeStep;
              const active  = i === activeStep;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0.3 }}
                  animate={{ opacity: i <= activeStep ? 1 : 0.3 }}
                  transition={{ duration: 0.4 }}
                  className="flex items-center gap-4 px-5 py-4 rounded-2xl transition-all"
                  style={{
                    background:   i <= activeStep ? accentBg  : '#f8fafc',
                    border:       `1px solid ${i <= activeStep ? accentBdr : '#e2e8f0'}`,
                  }}
                >
                  <span className="text-xl w-8 text-center">
                    {done ? '✅' : step.icon}
                  </span>
                  <span
                    className="flex-1 text-sm font-semibold"
                    style={{ color: i <= activeStep ? '#1e293b' : '#94a3b8' }}
                  >
                    {step.label}
                  </span>
                  {active && (
                    <motion.div
                      className="w-5 h-5 rounded-full border-2 border-t-transparent"
                      style={{ borderColor: accent, borderTopColor: 'transparent' }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.7, repeat: Infinity, ease: 'linear' }}
                    />
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Progress bar */}
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: `linear-gradient(90deg, ${accent}, ${isMH ? '#7c3aed' : '#f97316'})` }}
              animate={{ width: `${((activeStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
          <p className="text-xs text-slate-400 font-bold mt-3 tracking-wide">
            {Math.round(((activeStep + 1) / steps.length) * 100)}% COMPLETE
          </p>
        </motion.div>
      </div>
    </div>
  );
}


// ══════════════════════════════════════════════════════════════════════════════
// SCREEN 2: Analyzing Answers (shown after submit)
// ══════════════════════════════════════════════════════════════════════════════

function AnalyzingScreen() {
  const [activeStep, setActiveStep] = useState(0);
  const [dots, setDots]             = useState('');

  const steps = [
    { label: 'Processing your responses',      icon: '📝' },
    { label: 'Running sentiment analysis',     icon: '🔍' },
    { label: 'Detecting risk patterns',        icon: '⚡' },
    { label: 'Generating your support plan',   icon: '💡' },
    { label: 'Finalizing results',             icon: '✅' },
  ];

  useEffect(() => {
    const iv = setInterval(() => setActiveStep(s => Math.min(s + 1, steps.length - 1)), 1400);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => setDots(d => d.length >= 3 ? '' : d + '.'), 400);
    return () => clearInterval(iv);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-[3rem] shadow-2xl p-12 border border-slate-100 w-full max-w-xl text-center"
        >
          {/* Scanning animation */}
          <div className="relative w-32 h-32 mx-auto mb-10">
            {/* Outer rotating ring */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{ border: '3px solid transparent', borderTopColor: '#4f46e5', borderRightColor: '#4f46e5' }}
              animate={{ rotate: 360 }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
            />
            {/* Inner rotating ring (opposite) */}
            <motion.div
              className="absolute inset-3 rounded-full"
              style={{ border: '2px solid transparent', borderBottomColor: '#7c3aed', borderLeftColor: '#7c3aed' }}
              animate={{ rotate: -360 }}
              transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
            />
            {/* Center */}
            <div className="absolute inset-6 rounded-full bg-indigo-600 flex items-center justify-center text-3xl shadow-lg">
              🔬
            </div>
          </div>

          <h2 className="text-3xl font-black text-slate-800 tracking-tight mb-3">
            Analyzing your responses{dots}
          </h2>
          <p className="text-slate-500 font-medium mb-10 leading-relaxed">
            Our AI engine is processing your answers using sentiment analysis, keyword detection, and risk classification.
          </p>

          {/* Step list */}
          <div className="flex flex-col gap-3 mb-10 text-left">
            {steps.map((step, i) => {
              const done   = i < activeStep;
              const active = i === activeStep;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0.3 }}
                  animate={{ opacity: i <= activeStep ? 1 : 0.3 }}
                  transition={{ duration: 0.4 }}
                  className="flex items-center gap-4 px-5 py-4 rounded-2xl"
                  style={{
                    background: i <= activeStep ? 'rgba(79,70,229,0.08)' : '#f8fafc',
                    border:     `1px solid ${i <= activeStep ? 'rgba(79,70,229,0.25)' : '#e2e8f0'}`,
                  }}
                >
                  <span className="text-xl w-8 text-center">
                    {done ? '✅' : step.icon}
                  </span>
                  <span
                    className="flex-1 text-sm font-semibold"
                    style={{ color: i <= activeStep ? '#1e293b' : '#94a3b8' }}
                  >
                    {step.label}
                  </span>
                  {active && (
                    <motion.div
                      className="w-5 h-5 rounded-full border-2"
                      style={{ borderColor: '#4f46e5', borderTopColor: 'transparent' }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.7, repeat: Infinity, ease: 'linear' }}
                    />
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Animated scan bar */}
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden relative">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500"
              animate={{ x: ['-100%', '100%'] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
              style={{ width: '60%' }}
            />
          </div>
          <p className="text-xs text-slate-400 font-bold mt-3 tracking-wide uppercase">
            AI Analysis in Progress
          </p>
        </motion.div>
      </div>
    </div>
  );
}


// ══════════════════════════════════════════════════════════════════════════════
// MAIN ASSESSMENT COMPONENT
// ══════════════════════════════════════════════════════════════════════════════

const Assessment = () => {
  const navigate = useNavigate();

  const [track,      setTrack]      = useState(null);
  const [questions,  setQs]         = useState([]);
  const [sessionId,  setSessionId]  = useState(null);
  const [answers,    setAns]        = useState({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [err,        setErr]        = useState(null);

  // 'idle' | 'generating' | 'questions' | 'analyzing' | 'done'
  const [phase, setPhase] = useState('idle');

  // ── Select track → generate questions ──────────────────────────────────────
  const selectTrack = async (t) => {
    setErr(null);
    setPhase('generating');
    setTrack(t);
    try {
      const r = await getAssessmentQuestions(t);
      setQs(r.data.questions);
      setSessionId(r.data.session_id);
      setPhase('questions');
    } catch {
      setErr('Failed to generate your assessment. Please try again.');
      setPhase('idle');
    }
  };

  // ── Select answer ──────────────────────────────────────────────────────────
  const handleSelectAnswer = (option, score) => {
    const q = questions[currentIdx];
    setAns(prev => ({
      ...prev,
      [q.id]: { question_id: q.id, question_text: q.text, answer: option, score }
    }));
  };

  // ── Next question or submit ────────────────────────────────────────────────
  const handleNext = async () => {
    const q = questions[currentIdx];
    if (!answers[q.id]) return;

    if (currentIdx < questions.length - 1) {
      setCurrentIdx(prev => prev + 1);
      return;
    }

    // Last question — submit
    setPhase('analyzing');
    try {
      await submitAssessment({
        session_id: sessionId,
        track,
        answers: Object.values(answers),
      });
      navigate('/dashboard');
    } catch {
      setErr('Submission failed. Please try again.');
      setPhase('questions');
    }
  };

  // ── Reset ──────────────────────────────────────────────────────────────────
  const reset = () => {
    setTrack(null); setQs([]); setSessionId(null);
    setAns({}); setCurrentIdx(0); setPhase('idle'); setErr(null);
  };

  // ── Render phases ──────────────────────────────────────────────────────────

  if (phase === 'generating') return <GeneratingScreen track={track} />;
  if (phase === 'analyzing')  return <AnalyzingScreen />;

  // ── Track selection ────────────────────────────────────────────────────────
  if (phase === 'idle') return (
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
          <p className="text-slate-500 text-lg font-medium">
            Select a specialized track for a deeper AI analysis.
          </p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {[
            {
              id: 'mental_health', label: 'Mental Wellbeing',
              icon: <Brain size={40}/>, color: 'bg-blue-600',
              desc: 'Deep dive into stress patterns, mood fluctuations, and emotional resilience.',
              bg: 'bg-blue-50',
            },
            {
              id: 'harassment', label: 'Safety & Harassment',
              icon: <ShieldAlert size={40}/>, color: 'bg-rose-600',
              desc: 'Secure assessment for workplace safety and social harassment concerns.',
              bg: 'bg-rose-50',
            },
          ].map(item => (
            <motion.button
              whileHover={{ y: -8 }} whileTap={{ scale: 0.98 }}
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
                Start Track <ChevronRight size={20}/>
              </div>
              <div className={`absolute -right-4 -bottom-4 w-24 h-24 ${item.color} opacity-5 rounded-full`}/>
            </motion.button>
          ))}
        </div>

        {err && (
          <p className="text-center mt-8 text-red-500 font-bold">⚠️ {err}</p>
        )}
      </div>
    </div>
  );

  // ── Questions ──────────────────────────────────────────────────────────────
  const q = questions[currentIdx];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-[3rem] shadow-2xl p-12 border border-slate-100 w-full max-w-4xl relative"
        >
          {/* Back */}
          <button
            onClick={reset}
            className="absolute top-10 left-10 flex items-center gap-1 text-slate-400 font-bold hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft size={18}/> BACK
          </button>

          {/* Progress dots */}
          <div className="text-center mb-12">
            <span className="bg-indigo-50 text-indigo-600 px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">
              {track?.replace('_', ' ')}
            </span>
            <div className="flex justify-center gap-2 mt-6 mb-2">
              {questions.map((_, i) => (
                <div
                  key={i}
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    i <= currentIdx ? 'w-8 bg-indigo-600' : 'w-2 bg-slate-100'
                  }`}
                />
              ))}
            </div>
            <p className="text-slate-400 font-bold text-sm">
              Question {currentIdx + 1} of {questions.length}
            </p>
          </div>

          {/* Question text */}
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

          {/* Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
            {q?.options.map((opt, i) => {
              const selected = answers[q.id]?.answer === opt;
              return (
                <button
                  key={i}
                  onClick={() => handleSelectAnswer(opt, q.scores[i])}
                  className={`py-6 px-8 rounded-[2rem] font-bold text-lg transition-all border-2 flex items-center justify-between ${
                    selected
                      ? 'bg-indigo-600 border-indigo-600 text-white shadow-xl scale-[1.02]'
                      : 'bg-slate-50 border-transparent text-slate-600 hover:border-indigo-200'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-2xl bg-white/10 p-2 rounded-xl">{q.emoji[i]}</span>
                    {opt}
                  </div>
                  {selected && <CheckCircle size={24}/>}
                </button>
              );
            })}
          </div>

          {/* Next / Submit button */}
          <div className="flex justify-center">
            <button
              onClick={handleNext}
              disabled={!answers[q?.id]}
              className="group bg-slate-900 text-white px-16 py-5 rounded-[2rem] font-black text-xl flex items-center gap-3 shadow-2xl hover:bg-indigo-600 transition-all disabled:opacity-20 disabled:grayscale"
            >
              {currentIdx === questions.length - 1 ? 'Analyze My Profile' : 'Continue'}
              <ChevronRight size={24} className="group-hover:translate-x-1 transition-transform"/>
            </button>
          </div>

          {err && <p className="text-center mt-6 text-red-500 font-bold">⚠️ {err}</p>}
        </motion.div>
      </div>
    </div>
  );
};

export default Assessment;