import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, ArrowRight, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Market } from '@/types/market';

export default function DashboardSnippet() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['markets', 'movers'],
    queryFn: () => apiClient.getMarkets({ sort_by: 'movers', limit: 3 }),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">
          Biggest Movers (24h)
        </h3>
        {isLoading && <RefreshCw className="w-3 h-3 text-zinc-500 animate-spin" />}
      </div>

      <div className="space-y-3">
        {isLoading && !data ? (
           <div className="text-center text-zinc-600 text-xs py-2">Loading movers...</div>
        ) : isError ? (
           <div className="text-center text-red-400 text-xs py-2 cursor-pointer" onClick={() => refetch()}>Error loading</div>
        ) : (
          data?.markets.map((market: Market) => {
            const change = market.change_24h || 0;
            const isPositive = change >= 0;
            const price = market.current_price || market.probability || 0;

            return (
              <div key={market.id} className="flex items-center justify-between group cursor-pointer">
                <div className="flex flex-col max-w-[70%]">
                  <span className="font-medium text-zinc-200 text-sm group-hover:text-blue-400 transition-colors truncate">
                    {market.question}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">
                      {market.platform ? market.platform.charAt(0).toUpperCase() + market.platform.slice(1) : 'Unknown'}
                    </span>
                    <span className="text-xs text-zinc-500">
                      Current: {(price * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className={`flex items-center gap-1 text-sm font-bold ${
                  isPositive ? 'text-green-400' : 'text-red-400'
                }`}>
                  {isPositive ? '+' : ''}{(change * 100).toFixed(0)}%
                  {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                </div>
              </div>
            );
          })
        )}
      </div>
      <button className="w-full mt-4 py-2 text-xs font-medium text-zinc-400 hover:text-white bg-zinc-800/50 hover:bg-zinc-800 rounded transition-colors flex items-center justify-center gap-1">
        View All Movers <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  );
}
