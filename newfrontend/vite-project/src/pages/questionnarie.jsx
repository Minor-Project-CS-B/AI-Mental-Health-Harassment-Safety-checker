// import Navbar from "../components/Navbar.jsx";
     
// function Questionnaire() {
//   return (
//     <div>
//       <Navbar/>
//       <h2>Mental Health Assessment</h2>

//       <p>Question 1: How have you been feeling recently?</p>

//       <button>😊 Good</button>
//       <button>😐 Neutral</button>
//       <button>😟 Stressed</button>
//       <button>😢 Very Sad</button>

//     </div>
//   );
// }

// export default Questionnaire;
import Navbar from "../components/Navbar.jsx";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// 1. Import icons (Rename BarChart icon to BarChartIcon to avoid conflict)
import { ChevronRight, FileHeart, ShieldAlert, Zap, Mic, BarChart as BarChartIcon, Users, Repeat } from 'lucide-react';

// 2. Import charts (Combined into one single line to avoid redeclaration)
import { RadialBarChart, RadialBar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';


// --- CONFIGURATION DATA ---
const totalQuestions = 8;
const assessmentQuestions = [
  "How often do you feel stressed or overwhelmed?",
  "Have you felt isolated or excluded in recent interactions?",
  "Have you experienced repeated, unwelcome advances or comments?",
  "How often are you comfortable expressing your opinions online?",
  "How confident are you that your online interactions are safe?",
  "Have you noticed a change in your mood after digital communication?",
  "Do you ever feel pressure to conform to others' expectations online?",
  "How supported do you feel by your community when you face conflict?"
];

// --- STYLING CONSTANTS (Matched to image_1.png palette) ---
const theme = {
  bg: 'bg-indigo-50', // Light indigo background
  accent: 'text-indigo-600',
  button: 'bg-indigo-600 text-white rounded-full hover:bg-indigo-700',
  card: 'bg-white rounded-[2rem] shadow-xl p-10 border border-slate-100',
  textHeader: 'text-slate-900 font-extrabold',
  textSub: 'text-slate-600',
  emojiInactive: 'p-4 rounded-2xl bg-slate-100 text-slate-400 border border-slate-200 cursor-pointer transition',
  emojiActive: 'p-4 rounded-2xl bg-sky-100 text-sky-600 border border-sky-300 scale-105 shadow-md transition'
};

// Animation settings
const fadeInOut = {
  initial: { opacity: 0, y: 15 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -15 },
  transition: { duration: 0.4 }
};

// ==========================================
// MAIN ASSESSMENT COMPONENT
// ==========================================
const Assessment = () => {
  const [stage, setStage] = useState('intro'); // 'intro', 'questions', 'analyzing', 'results'
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(1);
  const [answers, setAnswers] = useState(Array(totalQuestions).fill(null));
  const [analyzingComplete, setAnalyzingComplete] = useState(false);

  // Restart handler
  const handleRestart = () => {
    setStage('intro');
    setCurrentQuestionIdx(1);
    setAnswers(Array(totalQuestions).fill(null));
    setAnalyzingComplete(false);
  };

  return (
    <div className={`min-h-screen ${theme.bg} font-sans selection:bg-indigo-100`}>
      {/* Top Background Pattern (Simulating the waves from image_1.png) */}
      <div className="absolute top-0 left-0 w-full h-1/2 bg-sky-100/50 -z-10 rounded-b-[5rem] overflow-hidden">
        <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-indigo-200/50 rounded-full blur-3xl opacity-50" />
      </div>

      {/* --- NAVBAR --- */}
      {/* <nav className="p-8">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-slate-500">
           <a href="/"className="hover:text-indigo-600 cursor-pointer">Home</a>
          <span className="text-slate-300">•</span>
          <span className="text-indigo-600 font-medium">Harassment Safety Check</span>
        </div>
      </nav> */}
       <Navbar/>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="max-w-7xl mx-auto px-4 py-12 flex justify-center items-center">
        <AnimatePresence mode="wait">
          {/* STAGE: INTRO (Screen 1 & 2 combined logic) */}
          {stage === 'intro' && (
            <motion.div key="intro" {...fadeInOut} className="grid md:grid-cols-2 gap-12 w-full">
              {/* Card 1: Mental Health Self Assessment */}
              <div className={`${theme.card} relative flex flex-col justify-between`}>
                <div>
                  <h2 className={`${theme.textHeader} text-3xl mb-6`}>Mental Health Self Assessment</h2>
                  <p className={`${theme.textSub} mb-12`}>This check will help understand your emotional wellbeing. Answer honestly for better guidance.</p>
                </div>
                <div className="flex items-center justify-between mt-auto">
                    <div className="space-y-1 text-slate-500 text-sm">
                        <p>Estimated time: 2 minutes</p>
                        <p>Questions: {totalQuestions}</p>
                    </div>
                    <button onClick={() => setStage('questions')} className={`${theme.button} px-10 py-3 font-semibold`}>
                        Start Questions
                    </button>
                </div>
                {/* SVG Illustration - Placeholder */}
                <div className="absolute -top-10 -right-10 w-48 h-48 text-sky-300 opacity-60">
                    <FileHeart size={192} strokeWidth={1}/>
                </div>
              </div>

              {/* Card 2: Harassment Safety Assessment */}
              <div className={`${theme.card} border-l-4 border-sky-400 relative`}>
                <h2 className={`${theme.textHeader} text-3xl mb-6`}>Harassment Safety Assessment</h2>
                <p className={`${theme.textSub} mb-12`}>Identify unsafe situations and receive safety guidance.</p>
                <div className="flex items-center gap-8 mb-12 text-slate-500">
                    <div className="flex items-center gap-2"><Zap size={18} className="text-sky-400"/> Anonymous</div>
                    <div className="flex items-center gap-2"><ShieldAlert size={18} className="text-sky-400"/> Secure</div>
                </div>
                <button className={`${theme.button} bg-sky-600 hover:bg-sky-700 w-full py-4 text-lg font-bold`}>
                  Start Safety Questions
                </button>
              </div>
            </motion.div>
          )}

          {/* STAGE: QUESTIONS (Screen 3 & 4 combined logic) */}
          {stage === 'questions' && (
            <motion.div key="questions" {...fadeInOut} className={`${theme.card} w-full max-w-4xl`}>
              <div className="text-center mb-10">
                <p className={`${theme.textSub} text-xl`}>Question {currentQuestionIdx} of {totalQuestions}</p>
                <div className="w-full bg-slate-100 h-3 rounded-full mt-6 relative overflow-hidden">
                    <motion.div 
                        className="absolute inset-0 bg-sky-400 rounded-full"
                        initial={{ width: '0%' }}
                        animate={{ width: `${(currentQuestionIdx / totalQuestions) * 100}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>
              </div>

              <div className="text-center mb-16 px-10">
                <h3 className={`${theme.textHeader} text-4xl mb-6 leading-tight`}>
                  {assessmentQuestions[currentQuestionIdx - 1]}
                </h3>
              </div>

              {/* Emoji Options */}
              <div className="grid grid-cols-4 gap-6 mb-16 max-w-xl mx-auto">
                {[
                  { label: "Rarely", emoji: "😟" },
                  { label: "Sometimes", emoji: "😕" },
                  { label: "Often", emoji: "😟" },
                  { label: "Always", emoji: "😢" }
                ].map((option, idx) => (
                  <div key={idx} className="text-center group" onClick={() => {
                    const newAnswers = [...answers];
                    newAnswers[currentQuestionIdx - 1] = idx;
                    setAnswers(newAnswers);
                  }}>
                    <div className={answers[currentQuestionIdx - 1] === idx ? theme.emojiActive : theme.emojiInactive}>
                      <span className="text-4xl">{option.emoji}</span>
                    </div>
                    <p className={`mt-3 text-sm font-medium ${answers[currentQuestionIdx - 1] === idx ? theme.accent : 'text-slate-500'}`}>{option.label}</p>
                  </div>
                ))}
              </div>

              {/* Description Input */}
              <div className="mb-16">
                <input 
                    type="text" 
                    placeholder="Describe your experience (optional)" 
                    className="w-full border-b border-slate-300 pb-3 text-lg text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-indigo-400"
                />
              </div>

              {/* Navigation */}
              <div className="flex justify-between items-center">
                <button 
                  disabled={currentQuestionIdx === 1}
                  onClick={() => setCurrentQuestionIdx(prev => prev - 1)}
                  className={`${theme.button} bg-slate-100 text-slate-700 hover:bg-slate-200 px-8 py-3 disabled:opacity-50`}
                >
                  Previous
                </button>
                <button 
                  onClick={() => {
                    if (currentQuestionIdx < totalQuestions) {
                      setCurrentQuestionIdx(prev => prev + 1);
                    } else {
                      setStage('analyzing');
                    }
                  }}
                  className={`${theme.button} px-12 py-3 font-semibold group flex items-center gap-2`}
                >
                  {currentQuestionIdx < totalQuestions ? 'Next' : 'Submit'}
                  <ChevronRight size={20} className="group-hover:translate-x-1 transition"/>
                </button>
              </div>
            </motion.div>
          )}

          {/* STAGE: ANALYZING (Screen 5) */}
          {stage === 'analyzing' && (
            <motion.div key="analyzing" {...fadeInOut} className="w-full text-center flex flex-col items-center">
              {/* Complex Animation (Simplified Spinner + Tap to Speak) */}
              <div className="relative mb-16 w-80 h-80">
                {/* Simulated Wave Background (image_1.png has these internal waves) */}
                <motion.div 
                    animate={{ scale: [1, 1.1, 1], opacity: [0.6, 1, 0.6] }} 
                    transition={{ repeat: Infinity, duration: 2 }}
                    className="absolute inset-0 bg-sky-200 rounded-full scale-105"
                />
                
                {/* Analysis Circle */}
                <div className="absolute inset-0 bg-indigo-950 rounded-full p-4 flex items-center justify-center shadow-2xl border-4 border-sky-300">
                    <div className="w-1/2 h-1/2 border-4 border-sky-400 border-dashed rounded-full animate-spin-slow"/>
                </div>

                {/* Satellite Floating Icons */}
                <div className="absolute -top-10 -left-10 p-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-sky-300 shadow-xl">
                    <BarChart size={36}/>
                </div>
                <div className="absolute top-1/2 -right-16 p-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-red-300 shadow-xl">
                    <Zap size={36}/>
                </div>
              </div>

              <h2 className={`${theme.textHeader} text-4xl mb-6 text-slate-800`}>Analyzing Your Responses...</h2>
              <p className={`${theme.textSub} text-xl max-w-xl mx-auto mb-16`}>Our system will analyze anonymously and securely.</p>
              
              <button 
                onClick={() => setStage('results')} 
                className={`${theme.button} bg-sky-600 hover:bg-sky-700 px-12 py-4 text-xl font-bold flex items-center gap-3`}
              >
                <Mic size={24}/>
                Tap to speak
              </button>
            </motion.div>
          )}

          {/* STAGE: RESULTS (Screen 6) */}
         

// --- STAGE: RESULTS DASHBOARD ---


// --- STAGE: RESULTS DASHBOARD (Re-imagined from user sketch image_11.png) ---
{stage === 'results' && (
  <motion.div key="results" {...fadeInOut} className="w-full max-w-7xl mx-auto space-y-10">
    
    <div className="grid lg:grid-cols-5 gap-10 items-start">
      
      {/* LEFT: Risk Indicator (Circular Gauge) */}
      <div className={`${theme.card} lg:col-span-2 flex flex-col items-center justify-center p-12 text-center h-full relative overflow-hidden group`}>
        {/* Subtle background color-zone indicator */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-orange-100/30 to-orange-100/50 -z-10"/>

        <h3 className="text-2xl font-black text-slate-800 tracking-tight mb-4">Final Safety Analysis</h3>
        
        <div className="w-full h-80 mt-6 relative">
          <ResponsiveContainer width="100%" height="100%">
            {/* Custom Radial Chart with multiple segments for Low/Med/High areas */}
            <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" barSize={25} data={[
              { name: 'Low', value: 33, fill: '#86efac', cornerRadius: 0 }, // Green zone
              { name: 'Medium', value: 66, fill: '#fdba74', cornerRadius: 0 }, // Orange zone
              { name: 'High', value: 100, fill: '#fca5a5', cornerRadius: 0 }, // Red zone
              { name: 'Your Score', value: 65, fill: '#4f46e5', cornerRadius: 10 } // Actual score pointer
            ]} startAngle={180} endAngle={0}>
                {/* Gauge Background Segments */}
                <RadialBar dataKey="value" />
            </RadialBarChart>
          </ResponsiveContainer>
          
          {/* Main Score & Risk Label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center top-10">
            <span className="text-sm text-slate-400 font-medium uppercase tracking-widest">Risk Level</span>
            <span className="text-6xl font-black text-indigo-700 mt-2">MEDIUM</span>
            <span className="text-xs text-indigo-500 font-bold bg-indigo-50 px-3 py-1 rounded-full mt-4 border border-indigo-100 shadow-[0_0_10px_rgba(79,70,229,0.2)]">Analysis Complete</span>
          </div>
        </div>

        <p className="text-sm text-slate-600 max-w-sm mt-8 leading-relaxed">
          The AI detected consistent signals of anxiety and high stress in your responses. This indicates a medium risk level.
        </p>
      </div>

      {/* RIGHT: 5-Factor Analysis (Polished Bar Chart) */}
      <div className={`${theme.card} lg:col-span-3 h-full`}>
        <h3 className="text-2xl font-black text-slate-800 tracking-tight mb-10 text-center lg:text-left">Factor Profile (Visual Analysis)</h3>
        
        <div className="w-full h-[450px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={[
              { factor: 'Happiness', score: 30, fill: '#86efac' }, // Green (Positive)
              { factor: 'Confidence', score: 45, fill: '#a7f3d0' }, // Green (Positive)
              { factor: 'Social Involvement', score: 40, fill: '#f97316' }, // Orange (Neutral)
              { factor: 'Anxiety', score: 75, fill: '#fdba74' }, // Orange (Neutral)
              { factor: 'Stress', score: 85, fill: '#fca5a5' }  // Red (Negative)
            ]} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="factor" axisLine={{ stroke: '#e2e8f0' }} tickLine={false} tick={{ fill: '#64748b', fontSize: 13, fontWeight: 500 }} />
              <YAxis domain={[0, 100]} hide={true} />
              
              {/* Reference Lines/Areas (Matched to image_11.png zones) */}
              <Tooltip cursor={{ fill: 'rgba(79,70,229,0.05)' }} contentStyle={{ borderRadius: '1rem', border: '1px solid #e2e8f0', padding: '12px' }} itemStyle={{color: '#1e293b'}} formatter={(value) => `${value}%`}/>

              <Bar dataKey="score" radius={[15, 15, 0, 0]}>
                {/* Dynamically assign the correct 'fill' color based on the data object */}
                {
                    [{factor: 'H', score: 30, fill: '#86efac'}, {factor: 'C', score: 45, fill: '#a7f3d0'}].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))
                }
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-center text-slate-400 mt-6 italic">Data points derived from conversational sentiment and entity analysis.</p>
      </div>
    </div>

    {/* DOWN SIDE: Actions & Support (Updated from previous version) */}
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div className="bg-indigo-600 p-8 rounded-[2rem] text-white shadow-xl relative overflow-hidden group">
            <div className="relative z-10">
                <h3 className="text-xl font-bold mb-3 flex items-center gap-2"><ShieldAlert size={20}/> Urgent SOS Helpline</h3>
                <p className="text-indigo-100 text-sm mb-6">If you feel unsafe right now, connect with our 24/7 helpline.</p>
                <button className="w-full bg-white text-indigo-600 py-4 rounded-xl font-extrabold hover:bg-indigo-50 transition flex items-center justify-center gap-2 scale-100 hover:scale-105 shadow-md">
                    <Zap size={20}/> CALL 1-800-SAFE
                </button>
            </div>
            <div className="absolute -bottom-10 -right-10 text-indigo-500/20 group-hover:scale-110 transition-transform">
                <ShieldAlert size={200} />
            </div>
        </div>

        <div className={`${theme.card} !p-6 flex flex-col justify-between`}>
            <div>
                <h4 className="font-bold text-slate-800 mb-4">Analysis Report</h4>
                <p className="text-slate-500 text-sm mb-6">A detailed AI report containing key conversation data and analysis insights.</p>
            </div>
            <button className="w-full flex items-center justify-center gap-3 bg-white text-slate-800 p-4 rounded-2xl border border-slate-200 hover:bg-slate-100 transition font-medium">
                <BarChart size={24}/> Download PDF (AI Analysis)
            </button>
        </div>

        <div className={`${theme.card} !p-6 flex flex-col justify-between md:col-span-2 lg:col-span-1`}>
            <div>
                <h4 className="font-bold text-slate-800 mb-4">Mental Health Tips</h4>
                <p className="text-slate-500 text-sm mb-6">Actionable strategies and exercises tailored to your profile.</p>
            </div>
            <button className="w-full flex items-center justify-center gap-3 bg-sky-600 text-white p-4 rounded-2xl hover:bg-sky-700 transition font-medium">
                <Users size={24}/> View My Tips (3)
            </button>
        </div>
    </div>

    {/* Bottom Control Bar */}
    <div className="mt-10 flex justify-center gap-4">
        <button onClick={handleRestart} className="px-8 py-3 rounded-2xl font-bold text-slate-500 hover:bg-white transition flex items-center gap-2">
            <Repeat size={18}/> Reassess Conversation
        </button>
    </div>
  </motion.div>
)}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Assessment;