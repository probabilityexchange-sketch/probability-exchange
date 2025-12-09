import { motion } from 'framer-motion';
import { ArrowRight, Calendar, AlertCircle } from 'lucide-react';

const UPCOMING_EVENTS = [
  {
    id: 1,
    title: "Fed Interest Rate Decision",
    date: "Dec 18, 2:00 PM EST",
    impact: "High",
    description: "Markets pricing in 25bps cut. Watch Treasury yields and USD.",
    marketLink: "#"
  },
  {
    id: 2,
    title: "SEC Spot ETF Deadline",
    date: "Jan 10",
    impact: "Critical",
    description: "Final deadline for Ark 21Shares Bitcoin ETF application.",
    marketLink: "#"
  },
  {
    id: 3,
    title: "Iowa Caucus",
    date: "Jan 15",
    impact: "High",
    description: "First major test for GOP candidates. Trump polling +30%.",
    marketLink: "#"
  }
];

export default function WhatToWatch() {
  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800 rounded-xl overflow-hidden">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <h2 className="font-bold text-white flex items-center gap-2">
          <Calendar className="w-5 h-5 text-purple-400" />
          What to Watch
        </h2>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
          This Week
        </span>
      </div>

      <div className="divide-y divide-zinc-800/50">
        {UPCOMING_EVENTS.map((event) => (
          <div key={event.id} className="p-4 hover:bg-zinc-800/30 transition-colors group cursor-pointer">
            <div className="flex justify-between items-start mb-1">
              <h3 className="font-semibold text-zinc-200 group-hover:text-white transition-colors">
                {event.title}
              </h3>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${
                event.impact === 'Critical'
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {event.impact}
              </span>
            </div>

            <p className="text-xs text-zinc-500 mb-2">{event.date}</p>
            <p className="text-sm text-zinc-400 mb-3 leading-relaxed">
              {event.description}
            </p>

            <div className="flex items-center text-xs font-medium text-blue-400 group-hover:text-blue-300 transition-colors">
              View Markets <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
