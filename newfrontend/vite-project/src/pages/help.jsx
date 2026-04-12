import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Phone, Globe, ShieldAlert, Heart, Info } from 'lucide-react';
// Import both functions as seen in your api.js image
import { getHelp, getEmergency } from '../services/api'; 
import Navbar from '../components/Navbar';

export default function Help() {
  const [data, setData] = useState(null);
  const [emergencyData, setEmergencyData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fire both requests at once
    Promise.all([getHelp(), getEmergency()])
      .then(([helpRes, emergencyRes]) => {
        setData(helpRes.data);
        setEmergencyData(emergencyRes.data);
      })
      .catch(err => console.error("Error loading help data:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="h-screen flex items-center justify-center bg-[#FDFCFB]">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
    </div>
  );

  // Defining our colors and mapping them to your backend keys
  const sections = [
    { 
      key: 'mental_health', 
      label: 'Mental Health', 
      icon: <Heart size={20} />, 
      color: 'bg-[#FFF0F5]', // Light Pink
      text: 'text-pink-700',
      border: 'border-pink-200'
    },
    { 
      key: 'harassment_safety', 
      label: 'Safety Support', 
      icon: <ShieldAlert size={20} />, 
      color: 'bg-[#E0F2FE]', // Light Blue
      text: 'text-blue-700',
      border: 'border-blue-200'
    },
    { 
      key: 'online_resources', 
      label: 'Resources', 
      icon: <Globe size={20} />, 
      color: 'bg-[#FFFBEC]', // Soft Yellow
      text: 'text-yellow-800',
      border: 'border-yellow-200'
    },
  ];

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <div className="max-w-5xl mx-auto px-6 py-12">
        <header className="mb-10">
          <h2 className="text-4xl font-black text-slate-800 mb-2">Help & Support</h2>
          <p className="text-slate-500 italic text-sm">{data?.disclaimer}</p>
        </header>

        {/* Dynamic Emergency Section from getEmergency() */}
        {emergencyData && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-rose-50 border-2 border-rose-100 rounded-[2rem] p-8 mb-12 flex flex-col md:flex-row items-center justify-between gap-6"
          >
            <div className="flex items-center gap-5">
              <div className="bg-rose-500 text-white p-4 rounded-2xl shadow-lg">
                <ShieldAlert size={30} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-rose-900">Immediate Assistance</h3>
                <p className="text-rose-700/80">Available 24/7 for life-threatening situations.</p>
              </div>
            </div>
            {/* Assuming emergencyData has a 'number' field */}
            <a 
              href={`tel:${emergencyData.number || '112'}`} 
              className="bg-rose-600 text-white px-8 py-4 rounded-2xl font-black text-xl hover:bg-rose-700 transition-all shadow-md"
            >
              Call {emergencyData.number || '112'}
            </a>
          </motion.div>
        )}

        {/* Bento Grid for Resources */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sections.map((sec) => {
            const items = data?.resources?.[sec.key];
            if (!items?.length) return null;

            return (
              <div key={sec.key} className={`${sec.color} ${sec.border} border-2 rounded-[2.5rem] p-6`}>
                <div className={`flex items-center gap-2 mb-6 font-bold uppercase tracking-widest text-xs ${sec.text}`}>
                  {sec.icon} {sec.label}
                </div>

                <div className="space-y-4">
                  {items.map((item, i) => (
                    <div key={i} className="bg-white/80 backdrop-blur-md p-5 rounded-3xl shadow-sm border border-white/50 hover:shadow-md transition-shadow">
                      <h4 className="font-bold text-slate-800 mb-1">{item.name}</h4>
                      <p className="text-xs text-slate-500 leading-relaxed mb-4">{item.description}</p>
                      
                      <div className="flex items-center justify-between">
                        {item.number && (
                          <a href={`tel:${item.number}`} className={`font-black text-sm ${sec.text} flex items-center gap-1`}>
                            <Phone size={14} /> {item.number}
                          </a>
                        )}
                        {item.url && (
                          <a href={item.url} target="_blank" rel="noreferrer" className="text-[10px] font-bold text-slate-400 hover:text-indigo-600 underline">
                            WEBSITE
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}