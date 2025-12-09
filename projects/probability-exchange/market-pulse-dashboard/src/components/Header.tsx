/**
 * Header Component - Dashboard header with branding
 */

import { motion } from 'framer-motion';

export function Header() {
  return (
    <header className="w-full pb-6 mb-8" style={{ margin: 0, padding: '0 0 1.5rem 0' }}>
      <div className="flex items-center justify-between" style={{ margin: 0, padding: 0 }}>
        {/* Logo - Matching waitlist style */}
        <div className="flex items-center gap-2 cursor-pointer group">
          <span className="text-2xl md:text-3xl font-['IBM_Plex_Mono'] font-bold tracking-tighter text-white group-hover:opacity-80 transition-opacity">
            probex<span className="text-zinc-600 font-semibold tracking-tight">.markets</span>
          </span>
        </div>

        {/* Social Link - Matching waitlist style */}
        <a
          href="https://x.com/probabilityex"
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors duration-300 bg-white/5 hover:bg-white/10 px-4 py-2 rounded-full border border-white/5 hover:border-white/20"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          <span className="hidden md:inline font-medium">@probabilityex</span>
        </a>
      </div>

      {/* Subtitle */}
      <div className="mt-6">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
          Market Intelligence <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">
            Dashboard
          </span>
        </h1>
        <p className="text-lg text-zinc-400 max-w-2xl">
          Real-time prediction markets with AI-powered news analysis
        </p>
      </div>
    </header>
  );
}
