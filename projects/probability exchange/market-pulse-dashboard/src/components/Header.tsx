/**
 * Header Component - Dashboard header with branding
 */

import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

export function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="relative mb-6"
    >
      {/* Background Glow Effect */}
      <div className="absolute -inset-1 bg-gradient-glow opacity-50 blur-3xl pointer-events-none" />

      <div className="relative bg-dark-card/40 backdrop-blur-xl rounded-2xl border border-dark-border overflow-hidden">
        {/* Subtle Top Border Accent */}
        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/50 to-transparent" />

        <div className="px-8 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Logo Section */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-primary-500/20 blur-xl rounded-full" />
                <div className="relative bg-gradient-primary p-2.5 rounded-xl">
                  <Activity className="w-6 h-6 text-white" strokeWidth={2.5} />
                </div>
              </div>

              <div>
                <h1 className="text-2xl md:text-3xl font-bold font-mono tracking-tight">
                  <span className="text-white">probex</span>
                  <span className="text-zinc-600">.markets</span>
                </h1>
                <p className="text-sm text-zinc-500 font-medium mt-0.5">
                  Real-Time Market Intelligence
                </p>
              </div>
            </div>

            {/* Live Indicator */}
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-dark-surface/80 border border-dark-border">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-success-500" />
              </span>
              <span className="text-xs font-mono font-semibold text-success-500 uppercase tracking-wider">
                Live
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
