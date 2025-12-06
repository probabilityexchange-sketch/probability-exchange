import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

// Mock data for live ticker (will be replaced by live data or API later)
const TICKER_ITEMS = [
  { id: '1', symbol: 'TRUMP2024', name: 'Trump 2024 (Polymarket)', price: 0.52, change: 0.02 },
  { id: '2', symbol: 'FED-CUT-Q2', name: 'Fed Cut Q2 (Kalshi)', price: 0.65, change: -0.05 },
  { id: '3', symbol: 'BTC-100K', name: 'Bitcoin > $100k (Poly)', price: 0.38, change: 0.04 },
  { id: '4', symbol: 'OIL-70', name: 'Oil < $70 (Kalshi)', price: 0.45, change: -0.03 },
  { id: '5', symbol: 'AGI-2026', name: 'AGI by 2026 (Manifold)', price: 0.28, change: 0.01 },
];

export default function LiveTicker() {
  const [items, setItems] = useState(TICKER_ITEMS);

  // Rotate items every 3 seconds for mobile, or scroll for desktop
  useEffect(() => {
    const interval = setInterval(() => {
      setItems(prev => {
        // Simulate live price updates
        return prev.map(item => ({
          ...item,
          price: Math.max(0.01, Math.min(0.99, item.price + (Math.random() - 0.5) * 0.02))
        }));
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-zinc-900 border-b border-zinc-800 overflow-hidden h-10 flex items-center">
      <div className="flex items-center px-4 gap-2 text-xs font-bold text-blue-400 bg-zinc-900 z-10 h-full border-r border-zinc-800 shadow-[4px_0_8px_rgba(0,0,0,0.5)] whitespace-nowrap">
        <span className="animate-pulse">●</span> LIVE ODDS
      </div>

      <div className="flex-1 overflow-hidden relative">
        <div className="animate-ticker flex items-center gap-8 px-4 whitespace-nowrap">
          {/* Duplicate items for seamless loop */}
          {[...items, ...items].map((item, i) => (
            <div key={`${item.id}-${i}`} className="flex items-center gap-2 group cursor-pointer hover:bg-zinc-800/50 px-2 py-1 rounded transition-colors">
              <span className="text-zinc-300 font-medium text-xs sm:text-sm">{item.name}</span>
              <span className={`font-mono font-bold text-xs sm:text-sm ${
                item.change >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {(item.price * 100).toFixed(1)}%
              </span>
              {item.change >= 0 ? (
                <TrendingUp className="w-3 h-3 text-green-400" />
              ) : (
                <TrendingDown className="w-3 h-3 text-red-400" />
              )}
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes ticker {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-ticker {
          animation: ticker 30s linear infinite;
        }
        .animate-ticker:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}
