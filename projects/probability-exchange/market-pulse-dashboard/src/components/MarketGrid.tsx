/**
 * MarketGrid Component - Grid layout for market cards
 */

import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp } from 'lucide-react';
import { MarketCard } from './MarketCard';
import type { Market } from '@/types/market';

interface MarketGridProps {
  markets: Market[];
  selectedMarketId?: string | null;
  onMarketSelect?: (market: Market) => void;
  isLoading?: boolean;
  favoriteMarkets?: string[];
  onToggleFavorite?: (marketId: string) => void;
}

// Skeleton Card for Loading State
function SkeletonCard() {
  return (
    <div className="bg-dark-card/60 backdrop-blur-sm rounded-2xl border border-dark-border overflow-hidden">
      <div className="p-6 space-y-4">
        {/* Header Skeleton */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 space-y-2">
            <div className="h-5 bg-zinc-800/50 rounded-lg w-3/4 animate-pulse" />
            <div className="h-5 bg-zinc-800/30 rounded-lg w-1/2 animate-pulse" />
          </div>
          <div className="h-6 w-20 bg-zinc-800/50 rounded-lg animate-pulse" />
        </div>

        {/* Price Skeleton */}
        <div className="py-4 space-y-2">
          <div className="h-12 bg-zinc-800/50 rounded-xl w-2/3 mx-auto animate-pulse" />
          <div className="h-4 bg-zinc-800/30 rounded-lg w-1/3 mx-auto animate-pulse" />
        </div>

        {/* Stats Skeleton */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-dark-surface/50 rounded-xl p-3 border border-dark-border/50">
            <div className="h-3 bg-zinc-800/30 rounded w-16 mb-2 animate-pulse" />
            <div className="h-7 bg-zinc-800/50 rounded-lg w-12 animate-pulse" />
          </div>
          <div className="bg-dark-surface/50 rounded-xl p-3 border border-dark-border/50">
            <div className="h-3 bg-zinc-800/30 rounded w-20 mb-2 animate-pulse" />
            <div className="h-7 bg-zinc-800/50 rounded-lg w-16 animate-pulse" />
          </div>
        </div>

        {/* Progress Bar Skeleton */}
        <div className="h-1.5 bg-zinc-800/30 rounded-full animate-pulse" />

        {/* Footer Skeleton */}
        <div className="flex items-center justify-between">
          <div className="h-3 bg-zinc-800/30 rounded w-24 animate-pulse" />
          <div className="h-3 bg-zinc-800/30 rounded w-16 animate-pulse" />
        </div>
      </div>
    </div>
  );
}

export function MarketGrid({
  markets,
  selectedMarketId,
  onMarketSelect,
  isLoading = false,
  favoriteMarkets = [],
  onToggleFavorite,
}: MarketGridProps) {
  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
      >
        {[...Array(6)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </motion.div>
    );
  }

  if (markets.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-center py-24"
      >
        <div className="text-center max-w-md">
          {/* Empty State Icon */}
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 bg-primary-500/10 rounded-full blur-xl" />
            <div className="relative bg-dark-card/80 rounded-full p-5 border border-dark-border">
              <Search className="w-14 h-14 text-zinc-600" strokeWidth={1.5} />
            </div>
          </div>

          <h3 className="text-xl font-semibold text-white mb-2">No Markets Found</h3>
          <p className="text-zinc-500 mb-6">
            We couldn't find any markets matching your search criteria.
            <br />
            Try adjusting your filters or search terms.
          </p>

          {/* Suggestions */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-dark-surface/50 border border-dark-border">
            <TrendingUp className="w-4 h-4 text-primary-400" strokeWidth={2} />
            <span className="text-sm text-zinc-400">
              Try searching for popular topics like "politics" or "sports"
            </span>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <AnimatePresence mode="popLayout">
        <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
          {markets.map((market, index) => (
            <motion.div
              key={market.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <MarketCard
                market={market}
                onSelect={onMarketSelect}
                isSelected={market.id === selectedMarketId}
                isFavorite={favoriteMarkets.includes(market.id)}
                onToggleFavorite={onToggleFavorite}
              />
            </motion.div>
          ))}
        </div>
      </AnimatePresence>
    </motion.div>
  );
}
