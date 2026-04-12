import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, Mic, Send, Image as ImageIcon, Video, 
  MoreHorizontal, X, Loader2, User, Bot 
} from 'lucide-react';
import { 
  sendMessage, startChat, 
  uploadImageEvidence, voiceToText 
} from '../services/api';
import Navbar from '../components/Navbar';

export default function Chat() {
  // --- LOGIC STATES ---
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mcqOpts, setMcq] = useState(null);
  const [emojiOpts, setEmoji] = useState(null);
  const [recording, setRecording] = useState(false);
  const [mediaRec, setMediaRec] = useState(null);
  const [uploadMsg, setUploadMsg] = useState(null);
  const [showMenu, setShowMenu] = useState(false);

  const bottomRef = useRef(null);
  const imageRef = useRef(null);
  const videoRef = useRef(null);
  const audioChunks = useRef([]);

  // --- INITIALIZATION ---
  // useEffect(() => {
  //   getChatHistory().then(r => {
  //     if (r.data.messages.length > 0) {
  //       setMessages(r.data.messages.map(m => ({ 
  //         role: m.role, content: m.content, type: m.input_type 
  //       })));
  //     } else {
  //       startChat().then(r => setMessages([{ role: 'assistant', content: r.data.content }]));
  //     }
  //   });
  // }, []);

  // useEffect(() => {
  //   bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  // }, [messages, loading]);

  // --- CORE SEND LOGIC ---
  const send = async (text, inputType = 'text') => {
    if (!text.trim() || loading) return;
    setMessages(m => [...m, { role: 'user', content: text, type: inputType }]);
    setInput(''); setMcq(null); setEmoji(null); setLoading(true); setShowMenu(false);
    
    try {
      const r = await sendMessage({ message: text, input_type: inputType, tag_evidence: false });
      setMessages(m => [...m, { role: 'assistant', content: r.data.reply }]);
      if (r.data.mcq_options?.length) setMcq(r.data.mcq_options);
      if (r.data.emoji_options?.length) setEmoji(r.data.emoji_options);
    } catch {
      setMessages(m => [...m, { role: 'assistant', content: 'Sorry, I hit a snag. Please try again.' }]);
    } finally { setLoading(false); }
  };

  // --- UPLOAD HANDLERS ---
  const handleFileUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setShowMenu(false);
    setUploadMsg(type === 'image' ? 'Analyzing image...' : 'Processing video...');
    
    const form = new FormData();
    form.append('file', file);
    form.append('context', '');

    try {
      const apiCall = type === 'image' ? uploadImageEvidence : uploadVideoEvidence;
      const r = await apiCall(form);
      const d = r.data;
      setMessages(m => [...m,
        { role: 'user', content: `[${type.toUpperCase()} Evidence: ${file.name}]`, type },
        { role: 'assistant', content: `${d.ai_analysis}\n\n${d.suggested_actions?.join('\n') || ''}` }
      ]);
    } catch {
      setMessages(m => [...m, { role: 'assistant', content: `Could not process ${type}.` }]);
    } finally { setLoading(false); setUploadMsg(null); e.target.value = ''; }
  };

  // --- VOICE LOGIC ---
  const toggleRecording = async () => {
    if (recording) {
      mediaRec.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      audioChunks.current = [];
      mr.ondataavailable = e => audioChunks.current.push(e.data);
      mr.onstop = async () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/webm' });
        const form = new FormData();
        form.append('file', blob, 'recording.webm');
        setLoading(true);
        try {
          const r = await voiceToText(form);
          if (r.data.transcription) setInput(r.data.transcription);
        } finally { setLoading(false); stream.getTracks().forEach(t => t.stop()); }
      };
      mr.start();
      setMediaRec(mr);
      setRecording(true);
    } catch { alert('Mic access denied'); }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar />

      <div className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-6 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-black text-slate-800 tracking-tight">AI Safety Companion</h2>
            <p className="text-slate-500 font-medium text-sm">Always active, always listening.</p>
          </div>
          <div className="flex -space-x-2">
            <div className="w-8 h-8 rounded-full bg-indigo-600 border-2 border-white flex items-center justify-center text-white"><Bot size={14}/></div>
            <div className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center text-slate-600"><User size={14}/></div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 bg-white rounded-[2.5rem] shadow-sm p-6 overflow-y-auto mb-6 border border-slate-100 space-y-6 scrollbar-hide">
          {messages.map((m, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] p-4 rounded-[1.8rem] text-sm leading-relaxed shadow-sm ${
                m.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-slate-50 text-slate-700 border border-slate-100 rounded-tl-none'
              }`}>
                {m.type && m.type !== 'text' && (
                  <span className="block text-[10px] uppercase font-black mb-1 opacity-60 tracking-widest">{m.type}</span>
                )}
                {m.content}
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-50 p-4 rounded-[1.5rem] rounded-tl-none border border-slate-100 flex items-center gap-3">
                <Loader2 className="animate-spin text-indigo-600" size={18} />
                <span className="text-sm text-slate-500 font-medium">{uploadMsg || 'Thinking...'}</span>
              </div>
            </div>
          )}

          {/* MCQ & Emoji Quick Replies */}
          <AnimatePresence>
            {(mcqOpts || emojiOpts) && !loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-wrap gap-2 py-2">
                {(mcqOpts || emojiOpts).map((opt, i) => (
                  <button 
                    key={i} onClick={() => send(opt, mcqOpts ? 'mcq' : 'emoji')}
                    className="bg-white border-2 border-slate-100 hover:border-indigo-600 hover:text-indigo-600 text-slate-600 px-4 py-2 rounded-full text-xs font-bold transition-all shadow-sm"
                  >
                    {opt}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Input Bar Section */}
        <div className="relative">
          {/* Floating Menu */}
          <AnimatePresence>
            {showMenu && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: -10 }} exit={{ opacity: 0, y: 20 }}
                className="absolute bottom-full left-0 mb-4 bg-white rounded-[2rem] shadow-2xl border border-slate-100 p-3 flex gap-3 z-50"
              >
                {[
                  { icon: <ImageIcon size={20}/>, label: "Image", color: "bg-emerald-500", ref: imageRef, type: 'image' },
                  { icon: <Video size={20}/>, label: "Video", color: "bg-rose-500", ref: videoRef, type: 'video' },
                ].map((item, i) => (
                  <button 
                    key={i} onClick={() => item.ref.current.click()}
                    className="flex flex-col items-center gap-1.5 p-3 hover:bg-slate-50 rounded-2xl transition-all"
                  >
                    <div className={`${item.color} text-white p-3 rounded-2xl shadow-lg shadow-inherit/20`}>{item.icon}</div>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{item.label}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hidden File Inputs */}
          <input ref={imageRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleFileUpload(e, 'image')} />
          <input ref={videoRef} type="file" accept="video/*" className="hidden" onChange={(e) => handleFileUpload(e, 'video')} />

          {/* Main Input Bar */}
          <div className="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 p-2 flex items-center gap-2">
            <button 
              onClick={() => setShowMenu(!showMenu)}
              className={`p-4 rounded-full transition-all ${showMenu ? 'bg-slate-900 text-white rotate-45' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}`}
            >
              <Plus size={22} />
            </button>

            <input 
              type="text" value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send(input)}
              placeholder={recording ? "Listening..." : "Describe the situation..."}
              className="flex-1 py-3 bg-transparent outline-none text-slate-700 placeholder:text-slate-400 font-medium"
            />

            <div className="flex items-center gap-1 pr-1">
              <button 
                onClick={toggleRecording}
                className={`p-4 rounded-full transition-all ${recording ? 'bg-rose-500 text-white animate-pulse' : 'text-slate-400 hover:bg-slate-100'}`}
              >
                <Mic size={20} />
              </button>
              
              <button 
                onClick={() => send(input)} disabled={!input.trim() || loading}
                className={`p-4 rounded-full transition-all ${input.trim() ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-slate-50 text-slate-300'}`}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}