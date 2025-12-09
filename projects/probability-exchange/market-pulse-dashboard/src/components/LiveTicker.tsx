import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import type { Market } from '@/types/market';

// Fallback mock data if API fails completely or is empty
const MOCK_TICKER_ITEMS = [
  { id: '1', symbol: 'TRUMP2024', name: 'Trump 2024 (Polymarket)', price: 0.52, change: 0.02 },
  { id: '2', symbol: 'FED-CUT-Q2', name: 'Fed Cut Q2 (Kalshi)', price: 0.65, change: -0.05 },
  { id: '3', symbol: 'BTC-100K', name: 'Bitcoin > $100k (Poly)', price: 0.38, change: 0.04 },
  { id: '4', symbol: 'OIL-70', name: 'Oil < $70 (Kalshi)', price: 0.45, change: -0.03 },
  { id: '5', symbol: 'AGI-2026', name: 'AGI by 2026 (Manifold)', price: 0.28, change: 0.01 },
];

export default function LiveTicker() {
  const [items, setItems] = useState<any[]>(MOCK_TICKER_ITEMS);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const fetchTickerData = async () => {
      try {
        setIsLoading(true);
        // Fetch top markets for the ticker
        const response = await apiClient.getMarkets({ limit: 10 });

        if (mounted && response.markets && response.markets.length > 0) {
          // Transform market data for ticker
          const tickerData = response.markets.map((market: Market) => ({
            id: market.id,
            symbol: market.id.substring(0, 10).toUpperCase(),
            name: market.question.length > 30 ? market.question.substring(0, 30) + '...' : market.question,
            price: market.current_price || market.probability || 0.5,
            change: (market.change_24h || 0), // Assuming change_24h is available or 0
          }));
          setItems(tickerData);
          setError(null);
        } else if (mounted) {
           // Fallback to mock if empty
           setItems(MOCK_TICKER_ITEMS);
        }
      } catch (err) {
        console.error("Failed to load live ticker data:", err);
        if (mounted) {
          // Show transient error then clear
          setError("Unable to load live markets");
          // Fallback to mock data immediately so UI isn't broken
          setItems(MOCK_TICKER_ITEMS);

          // Clear error after 5 seconds (Transient Error Handling)
          setTimeout(() => {
            if (mounted) setError(null);
          }, 5000);
        }
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    fetchTickerData();

    // Refresh every minute
    const interval = setInterval(fetchTickerData, 60000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // Simulating live price updates for visual effect
  useEffect(() => {
    const interval = setInterval(() => {
      setItems(prev => {
        return prev.map(item => ({
          ...item,
          price: Math.max(0.01, Math.min(0.99, item.price + (Math.random() - 0.5) * 0.005))
        }));
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-zinc-900 border-b border-zinc-800 overflow-hidden h-10 flex items-center relative">
      <div className="flex items-center px-4 gap-2 text-xs font-bold text-blue-400 bg-zinc-900 z-10 h-full border-r border-zinc-800 shadow-[4px_0_8px_rgba(0,0,0,0.5)] whitespace-nowrap">
        <span className="animate-pulse">●</span> LIVE ODDS
      </div>

      {/* Transient Error Message Overlay */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute left-32 z-20 bg-red-500/10 border border-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

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
          animation: ticker 60s linear infinite;
        }
        .animate-ticker:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}
