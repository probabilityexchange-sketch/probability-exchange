import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Check } from 'lucide-react';

export default function App() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email) return;
    setStatus('loading');
    setTimeout(() => {
      setStatus('success');
      setEmail('');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white selection:bg-indigo-500/30 overflow-hidden font-sans relative">
      
      {/* Force Load IBM Plex Mono */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');`}
      </style>

      {/* --- BACKGROUND GLOWS --- */}
      <div className="fixed top-[-10%] left-[20%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="fixed bottom-[-10%] right-[20%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />

      {/* --- HEADER --- */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-6 py-6 md:px-12 backdrop-blur-sm bg-black/0">
        
        {/* LOGO */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-2 cursor-pointer group"
        >
          {/* UPDATED: Bold weight + Tighter Tracking = Logo Feel */}
          <span className="text-xl md:text-2xl font-['IBM_Plex_Mono'] font-bold tracking-tighter text-white group-hover:opacity-80 transition-opacity">
            probex<span className="text-zinc-600 font-semibold tracking-tight">.markets</span>
          </span>
        </motion.div>

        {/* SOCIAL LINK */}
        <motion.a 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          href="https://x.com/probabilityex" 
          target="_blank" 
          rel="noopener noreferrer"
          className="group flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors duration-300 bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full border border-white/5 hover:border-white/20"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          <span className="hidden md:inline font-medium">@probabilityex</span>
        </motion.a>
      </nav>

      {/* --- HERO CONTENT --- */}
      <main className="flex flex-col items-center justify-center min-h-screen px-4 text-center relative z-10">
        
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-4xl mx-auto space-y-6"
        >
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium uppercase tracking-wider mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            Waitlist Open
          </div>

          <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight text-white">
            Unlock the Future <br /> 
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">
              of Predictions.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            The next-generation prediction exchange platform. <br className="hidden md:block"/>
            Secure your early access before we launch.
          </p>
        </motion.div>

        {/* INPUT FORM */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-full max-w-md mt-10"
        >
          <form onSubmit={handleSubmit} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full opacity-20 group-hover:opacity-40 transition duration-500 blur-md"></div>
            
            <div className="relative flex items-center bg-[#0A0A0A] rounded-full p-2 border border-white/10 focus-within:border-white/20 transition-colors shadow-2xl">
              <input 
                type="email" 
                placeholder="Enter your email..." 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={status === 'success'}
                className="flex-1 bg-transparent text-white placeholder-zinc-600 px-6 py-2 outline-none text-base disabled:opacity-50"
              />
              
              <button 
                disabled={status === 'loading' || status === 'success'}
                className={`
                  h-10 px-6 rounded-full font-medium transition-all duration-300 flex items-center gap-2
                  ${status === 'success' 
                    ? 'bg-green-500 text-black' 
                    : 'bg-white text-black hover:bg-zinc-200 hover:scale-[1.02] active:scale-[0.98]'}
                `}
              >
                {status === 'loading' && <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />} 
                {status === 'success' && <><Check className="w-4 h-4" /> Joined</>}
                {status === 'idle' && <>Join <ArrowRight className="w-4 h-4" /></>}
              </button>
            </div>
          </form>

          <p className="mt-6 text-sm text-zinc-600">
            Join 2,000+ others. Unsubscribe anytime.
          </p>
        </motion.div>
      </main>
    </div>
  );
}