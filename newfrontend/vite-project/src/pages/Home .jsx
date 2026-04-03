// import Navbar from "../components/Navbar.jsx";
// function Home() {
//   return (
//     <div>
//         <Navbar/>
//       <h1>AI Mental Health & Harassment Safety Checker</h1>

//       <p>
//         This tool helps identify mental stress or unsafe situations
//         using AI-based analysis.
//       </p>

//       <button>Start Assessment</button>
//     </div>
//   );
// }

// export default Home;


import React, { useState } from 'react';
import { Menu, X, Rocket, Zap, Shield, ChevronRight } from 'lucide-react';

const Home = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0f172a] text-white selection:bg-indigo-500/30">
      {/* --- ATTRACTIVE NAVBAR --- */}
      <nav className="fixed w-full z-50 bg-[#0f172a]/80 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-2 group cursor-pointer">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:rotate-12 transition-transform">
                <Rocket size={24} />
              </div>
              <span className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                ProjectX
              </span>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
              <a href="#features" className="hover:text-indigo-400 transition-colors">Features</a>
              <a href="#about" className="hover:text-indigo-400 transition-colors">About</a>
              <a href="/questions" className="hover:text-indigo-400 transition-colors">Viva Prep</a>
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-full transition-all shadow-[0_0_20px_rgba(79,70,229,0.4)]">
                Launch App
              </button>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 text-slate-300">
                {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav Dropdown */}
        {isMenuOpen && (
          <div className="md:hidden bg-[#1e293b] border-b border-slate-800 px-4 pt-2 pb-6 space-y-2">
            <a href="#" className="block px-3 py-2 text-base hover:bg-slate-800 rounded-md">Features</a>
            <a href="#" className="block px-3 py-2 text-base hover:bg-slate-800 rounded-md">Abou  nzjanjzi t</a>
            <button className="w-full mt-4 bg-indigo-600 text-white py-3 rounded-xl">Get Started</button>
          </div>
        )}
      </nav>

      {/* --- HERO SECTION --- */}
      {/* --- UPDATED HERO SECTION --- */}
<main className="pt-32 pb-20 px-4">
  <div className="max-w-7xl mx-auto text-center">
    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-8 animate-pulse">
      <Shield size={16} />
      <span>AI-Powered Digital Safety Shield</span>
    </div>
    
    <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight leading-tight">
      Creating a <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400">Safer Digital Space</span>
    </h1>
    
    <p className="text-slate-400 text-lg md:text-xl max-w-3xl mx-auto mb-10 leading-relaxed">
      Detecting harassment and supporting mental well-being through advanced Natural Language Processing. Our AI monitors and flags toxic behavior in real-time to protect your community.
    </p>

    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
      <button className="group flex items-center gap-2 bg-indigo-600 text-white px-8 py-4 rounded-2xl font-bold hover:bg-indigo-500 transition-all scale-100 hover:scale-105 shadow-[0_0_30px_rgba(79,70,229,0.3)]">
        Analyze Content 
        <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
      </button>
      <button className="px-8 py-4 rounded-2xl font-bold border border-slate-700 hover:bg-slate-800 transition-all text-slate-300">
        How it Works
      </button>
    </div>

    {/* UPDATED FEATURE GRID */}
    <div className="grid md:grid-cols-3 gap-8 mt-24 text-left">
      {[
        { 
          icon: <Zap className="text-yellow-400" />, 
          title: "Real-time Detection", 
          desc: "Instant identification of harassment, hate speech, and cyberbullying using custom NLP models." 
        },
        { 
          icon: <Shield className="text-cyan-400" />, 
          title: "Mental Health Support", 
          desc: "Sentiment analysis tools designed to detect signs of distress and provide immediate resources." 
        },
        { 
          icon: <Rocket className="text-purple-400" />, 
          title: "Automated Reporting", 
          desc: "Generates detailed safety logs and alerts to help moderators maintain a healthy environment." 
        }
      ].map((feature, i) => (
        <div key={i} className="p-8 rounded-3xl bg-slate-800/40 border border-slate-700 hover:border-indigo-500/50 transition-all backdrop-blur-sm group">
          <div className="mb-4 p-3 bg-slate-900 rounded-2xl w-fit group-hover:scale-110 transition-transform shadow-lg">
            {feature.icon}
          </div>
          <h3 className="text-xl font-bold mb-2 text-white">{feature.title}</h3>
          <p className="text-slate-400 leading-relaxed text-sm">{feature.desc}</p>
        </div>
      ))}
    </div>
  </div>
</main>
{/* Background Decor */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 -z-10 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full" />
      </div>
    </div>
  );
};

export default Home;
