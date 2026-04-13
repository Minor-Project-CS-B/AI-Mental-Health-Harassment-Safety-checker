import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
// === BACKEND SERVICE IMPORTS ===
import { getOnboardingQuestions, submitOnboarding } from '../services/api';

const theme = {
  card: "bg-white rounded-[2.5rem] shadow-xl p-10 border border-slate-100",
  textHeader: "text-slate-800 font-bold",
  textSub: "text-slate-500 font-medium",
  emojiActive: "w-20 h-20 rounded-2xl bg-indigo-50 border-2 border-indigo-500 flex items-center justify-center cursor-pointer transition-all scale-105 shadow-md",
  emojiInactive: "w-20 h-20 rounded-2xl bg-slate-50 border-2 border-transparent flex items-center justify-center cursor-pointer hover:bg-slate-100 transition-all",
  buttonNext: "px-12 py-3 bg-indigo-600 text-white rounded-2xl font-semibold hover:bg-indigo-700 transition-all flex items-center gap-2",
  buttonPrev: "px-8 py-3 bg-slate-100 text-slate-600 rounded-2xl font-medium hover:bg-slate-200 transition-all",
  buttonSubmit: "px-12 py-3 bg-green-600 text-white rounded-2xl font-bold hover:bg-green-700 transition-all shadow-lg shadow-green-200"
};

const Onboarding = () => {
  const navigate = useNavigate();
  
  // === BACKEND STATE ===
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // Keyed by question ID
  const [currentIdx, setCurrentIdx] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // === FETCH QUESTIONS FROM BACKEND ===
  useEffect(() => {
    getOnboardingQuestions()
      .then(res => {
        // If backend says already done, skip to dashboard
        if (res.data.already_complete) {
          navigate('/dashboard');
          return;
        }
        setQuestions(res.data.questions || res.data);
      })
      .catch(() => setError('Failed to load questions from server.'))
      .finally(() => setLoading(false));
  }, [navigate]);

  const q = questions[currentIdx];

  const handleSelect = (option, score, emoji) => {
    setAnswers(prev => ({
      ...prev,
      [q.id]: {
        question_id: q.id,
        question_text: q.text,
        answer: option,
        score: score,
        emoji: emoji
      }
    }));
  };

  const handleFinalSubmit = async () => {
    setSubmitting(true);
    try {
      // Send the array of answers to the backend
      await submitOnboarding({ answers: Object.values(answers) });
      navigate('/dashboard');
    } catch (err) {
      setError('Submission failed. Please check your connection.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${theme.card} w-full max-w-4xl`}
      >
        {/* Progress Bar */}
        <div className="text-center mb-10">
          <p className={`${theme.textSub} text-xl`}>Question {currentIdx + 1} of {questions.length}</p>
          <div className="w-full bg-slate-100 h-3 rounded-full mt-6 relative overflow-hidden">
            <motion.div 
              className="absolute inset-0 bg-indigo-500 rounded-full"
              animate={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Dynamic Question Text from Backend */}
        <AnimatePresence mode="wait">
          <motion.div 
            key={currentIdx}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="text-center mb-16 px-10"
          >
            <h3 className={`${theme.textHeader} text-4xl mb-6 leading-tight`}>
              {q?.text}
            </h3>
          </motion.div>
        </AnimatePresence>

        {/* Dynamic Emoji Options from Backend */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16 max-w-2xl mx-auto">
          {q?.options?.map((option, idx) => {
            const isSelected = answers[q.id]?.answer === option;
            return (
              <div 
                key={idx} 
                className="text-center group" 
                onClick={() => handleSelect(option, q.scores[idx], q.emoji[idx])}
              >
                <div className={isSelected ? theme.emojiActive : theme.emojiInactive}>
                  <span className="text-4xl">{q.emoji[idx]}</span>
                </div>
                <p className={`mt-3 text-sm font-medium ${isSelected ? 'text-indigo-600' : 'text-slate-500'}`}>
                  {option}
                </p>
              </div>
            );
          })}
        </div>

        {error && <p className="text-red-500 text-center mb-4">⚠️ {error}</p>}

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center">
          <button 
            onClick={() => setCurrentIdx(prev => prev - 1)}
            disabled={currentIdx === 0}
            className={`${theme.buttonPrev} disabled:opacity-30`}
          >
            Previous
          </button>

          {currentIdx < questions.length - 1 ? (
            <button 
              onClick={() => setCurrentIdx(prev => prev + 1)}
              disabled={!answers[q.id]}
              className={`${theme.buttonNext} disabled:opacity-50 disabled:grayscale`}
            >
              Next
              <ChevronRight size={20} />
            </button>
          ) : (
            <button 
              onClick={handleFinalSubmit}
              disabled={!answers[q?.id] || submitting}
              className={`${theme.buttonSubmit} disabled:opacity-50`}
            >
              {submitting ? "Processing..." : "Finish & View Results"}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default Onboarding;