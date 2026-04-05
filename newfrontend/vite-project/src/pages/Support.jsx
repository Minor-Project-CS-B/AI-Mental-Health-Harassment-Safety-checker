import React, { useState } from "react";
import { useTheme } from "../context/ThemeContext";
// import { helplines } from "../data/questions";

const typeColors = {
  "Mental Health": { dark: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",   light: "text-cyan-600 bg-cyan-50 border-cyan-200" },
  "Women Safety":  { dark: "text-pink-400 bg-pink-500/10 border-pink-500/20",   light: "text-pink-600 bg-pink-50 border-pink-200" },
  "Emergency":     { dark: "text-red-400 bg-red-500/10 border-red-500/20",      light: "text-red-600 bg-red-50 border-red-200" },
  "Child Safety":  { dark: "text-amber-400 bg-amber-500/10 border-amber-500/20",light: "text-amber-600 bg-amber-50 border-amber-200" },
  "Cyber Safety":  { dark: "text-violet-400 bg-violet-500/10 border-violet-500/20", light: "text-violet-600 bg-violet-50 border-violet-200" },
  "Women Rights":  { dark: "text-rose-400 bg-rose-500/10 border-rose-500/20",   light: "text-rose-600 bg-rose-50 border-rose-200" },
};

const faqs = [
  { q: "Is this tool a medical diagnosis?", a: "No. MindSafe AI provides AI-based support suggestions only. It is not a substitute for professional medical or legal advice." },
  { q: "Is my data private?", a: "Absolutely. No personally identifiable information is collected or stored permanently. All processing happens locally in your session." },
  { q: "What if I'm in immediate danger?", a: "Please call Police (100) or Women Helpline (1091) immediately. Do not wait — your safety comes first." },
  { q: "Can I use this anonymously?", a: "Yes. You can use MindSafe AI without providing any real personal information." },
  { q: "What is the POSH Act?", a: "The Prevention of Sexual Harassment Act (2013) protects employees and students from sexual harassment. Every institution with 10+ employees must have an Internal Complaints Committee." },
];

export default function Support({ setPage }) {
  const { dark } = useTheme();
  const [openFaq, setOpenFaq] = useState(null);

  const base = dark ? "bg-[#080c14] text-white" : "bg-gradient-to-br from-slate-50 via-cyan-50/10 to-white text-slate-900";
  const card = dark ? "bg-[#0d1322] border-white/[0.07]" : "bg-white border-slate-200/70 shadow-sm";

  return (
    <div className={`min-h-screen transition-colors duration-300 ${base}`}>
      {/* Header */}
      <div className={`sticky top-0 z-50 border-b backdrop-blur-xl ${dark ? "bg-[#080c14]/90 border-white/[0.06]" : "bg-white/90 border-slate-200/60"}`}>
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center gap-4">
          <button onClick={() => setPage("dashboard")} className={`text-sm font-medium transition-colors ${dark ? "text-slate-500 hover:text-white" : "text-slate-400 hover:text-slate-700"}`}>← Dashboard</button>
          <span className={`text-sm font-bold ${dark ? "text-slate-300" : "text-slate-700"}`}>Help & Support</span>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10 space-y-10">
        {/* Emergency banner */}
        <div className="rounded-2xl border border-red-500/30 bg-red-500/[0.07] p-6 flex items-center gap-4 flex-wrap">
          <div className="text-4xl">🚨</div>
          <div className="flex-1">
            <p className="text-red-400 font-extrabold text-lg mb-1">In Immediate Danger?</p>
            <p className="text-red-300/70 text-sm">Don't wait. Call now.</p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <a href="tel:100" className="px-5 py-2.5 rounded-xl bg-red-500 text-white font-bold text-sm hover:-translate-y-0.5 transition-all shadow-lg shadow-red-500/30">Police: 100</a>
            <a href="tel:1091" className="px-5 py-2.5 rounded-xl bg-pink-500 text-white font-bold text-sm hover:-translate-y-0.5 transition-all shadow-lg shadow-pink-500/30">Women: 1091</a>
          </div>
        </div>

        {/* Helplines */}
        <div>
          <p className={`text-xs font-bold uppercase tracking-widest mb-3 ${dark ? "text-slate-500" : "text-slate-400"}`}>All Helplines</p>
          <h2 className="text-2xl font-extrabold mb-6">Support Contacts</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {helplines.map((h, i) => {
              const col = typeColors[h.type] || typeColors["Mental Health"];
              return (
                <div key={i} className={`rounded-2xl border p-5 transition-all hover:-translate-y-0.5 ${card}`}>
                  <span className={`inline-block text-[0.65rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border mb-3 ${dark ? col.dark : col.light}`}>{h.type}</span>
                  <p className={`font-semibold text-sm mb-2 ${dark ? "text-slate-200" : "text-slate-700"}`}>{h.name}</p>
                  <a href={`tel:${h.number.replace(/-/g,"")}`}
                    className="text-xl font-extrabold text-cyan-500 hover:text-cyan-400 transition-colors block mb-1">{h.number}</a>
                  <p className={`text-xs ${dark ? "text-slate-600" : "text-slate-400"}`}>{h.available}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Safety tips */}
        <div>
          <h2 className="text-2xl font-extrabold mb-6">🛡️ Safety Awareness Tips</h2>
          <div className={`rounded-2xl border divide-y ${card} ${dark ? "divide-white/[0.05]" : "divide-slate-100"}`}>
            {[
              "Trust your instincts — if a situation feels unsafe, remove yourself immediately.",
              "Document every incident with date, time, location, and screenshots.",
              "Block and report anyone harassing you online — never engage or retaliate.",
              "Under POSH Act 2013, every institution must have an Internal Complaints Committee.",
              "Cyberstalking is a criminal offence under Section 66A of the IT Act.",
              "You can file an FIR at any police station regardless of location.",
              "National Commission for Women provides free legal aid and counseling.",
              "You do not need to prove severity — every uncomfortable situation matters.",
            ].map((t, i) => (
              <div key={i} className={`flex gap-4 px-6 py-4`}>
                <span className="text-cyan-500 font-bold text-sm w-5 flex-shrink-0 mt-0.5">{i+1}.</span>
                <p className={`text-sm leading-relaxed ${dark ? "text-slate-400" : "text-slate-500"}`}>{t}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div>
          <h2 className="text-2xl font-extrabold mb-6">❓ Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((f, i) => (
              <div key={i} className={`rounded-2xl border overflow-hidden transition-all ${card}`}>
                <button onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className={`w-full flex items-center justify-between px-6 py-4 text-left transition-colors ${dark ? "hover:bg-white/[0.03]" : "hover:bg-slate-50"}`}>
                  <span className={`text-sm font-semibold ${dark ? "text-slate-200" : "text-slate-700"}`}>{f.q}</span>
                  <span className={`text-lg transition-transform duration-200 flex-shrink-0 ml-4 ${openFaq === i ? "rotate-45" : ""}`}>+</span>
                </button>
                {openFaq === i && (
                  <div className={`px-6 pb-5 ${dark ? "text-slate-400" : "text-slate-500"}`}>
                    <p className="text-sm leading-relaxed">{f.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Disclaimer */}
        <div className={`rounded-2xl border p-6 ${dark ? "bg-amber-500/[0.05] border-amber-500/20" : "bg-amber-50 border-amber-200"}`}>
          <p className={`font-bold mb-2 ${dark ? "text-amber-400" : "text-amber-600"}`}>⚠️ Important Disclaimer</p>
          <p className={`text-sm leading-relaxed ${dark ? "text-amber-500/70" : "text-amber-700/70"}`}>
            MindSafe AI provides AI-based support suggestions only and is not a substitute for professional medical, psychological, or legal advice. If you are in crisis, please contact emergency services or a licensed professional immediately.
          </p>
        </div>
      </div>
    </div>
  );
}
