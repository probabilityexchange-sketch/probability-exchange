/**
 * MarketCard Component - Individual market display card
 */

import { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart3, Clock, ExternalLink, Star } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import type { Market } from '@/types/market';
import { formatRelativeTime, formatProbability, formatPrice } from '@/lib/utils';

interface MarketCardProps {
  market: Market;
  onSelect?: (market: Market) => void;
  isSelected?: boolean;
  isFavorite?: boolean;
  onToggleFavorite?: (marketId: string) => void;
}

export function MarketCard({ market, onSelect, isSelected = false, isFavorite = false, onToggleFavorite }: MarketCardProps) {
  const [priceChange, setPriceChange] = useState<number | null>(null);
  const [isFlashing, setIsFlashing] = useState(false);
  const previousPrice = useRef(market.current_price);

  useEffect(() => {
    if (market.current_price !== previousPrice.current) {
      const change = market.current_price - previousPrice.current;
      setPriceChange(change);
      previousPrice.current = market.current_price;

      // Trigger flash animation
      setIsFlashing(true);
      setTimeout(() => setIsFlashing(false), 600);
    }
  }, [market.current_price]);

  // Generate sparkline data (7 days trend)
  const sparklineData = useMemo(() => {
    const days = 7;
    const data = [];
    for (let i = days - 1; i >= 0; i--) {
      const variance = (Math.random() - 0.5) * 0.1;
      data.push({
        price: Math.max(0.01, Math.min(0.99, market.current_price + variance))
      });
    }
    return data;
  }, [market.id]); // Only regenerate when market ID changes

  const formatVolume = (volume?: number) => {
    if (!volume) return 'N/A';
    if (volume >= 1000000) return `$${(volume / 1000000).toFixed(1)}M`;
    if (volume >= 1000) return `$${(volume / 1000).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  const isPriceUp = priceChange !== null && priceChange > 0;
  const isPriceDown = priceChange !== null && priceChange < 0;

  // Determine sparkline color based on trend
  const sparklineColor = isPriceUp ? '#10b981' : isPriceDown ? '#ef4444' : '#6366f1';

  // Platform badge colors
  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'kalshi':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'polymarket':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'manifold':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30';
    }
  };

  // Use last_updated or updated_at for relative time
  const timestamp = market.last_updated || market.updated_at || market.created_at;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      onClick={() => onSelect?.(market)}
      className={`group relative bg-dark-card/60 backdrop-blur-sm rounded-2xl border transition-all cursor-pointer overflow-hidden ${
        isSelected
          ? 'border-primary-500 shadow-glow-md'
          : 'border-dark-border hover:border-primary-500/50 hover:shadow-glow-sm'
      }`}
    >
      {/* Hover Gradient Effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      {/* Top Border Accent */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-base font-semibold text-white flex-1 line-clamp-2 leading-snug group-hover:text-primary-100 transition-colors">
            {market.question || market.title}
          </h3>

          <div className="flex items-center gap-2 shrink-0">
            {/* Favorite Button */}
            {onToggleFavorite && (
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleFavorite(market.id);
                }}
                className={`p-2 rounded-lg transition-colors ${
                  isFavorite
                    ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                    : 'bg-zinc-800/50 text-zinc-500 hover:bg-zinc-700/50 hover:text-yellow-400'
                }`}
                aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                <Star
                  className="w-4 h-4"
                  fill={isFavorite ? 'currentColor' : 'none'}
                  strokeWidth={2}
                />
              </motion.button>
            )}

            <div className={`px-2.5 py-1 rounded-lg text-xs font-semibold border ${getPlatformColor(market.platform)}`}>
              {market.platform}
            </div>
          </div>
        </div>

        {/* Price Display - PROMINENT */}
        <div className="relative">
          {isFlashing && (
            <motion.div
              initial={{ opacity: 0.3 }}
              animate={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className={`absolute inset-0 rounded-xl ${
                isPriceUp ? 'bg-success-500/20' : isPriceDown ? 'bg-danger-500/20' : 'bg-primary-500/20'
              }`}
            />
          )}

          <div className="relative text-center py-4">
            <div className="text-5xl font-bold font-mono tracking-tight text-white mb-2">
              {formatPrice(market.current_price)}
            </div>

            <AnimatePresence mode="wait">
              {priceChange !== null && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className={`flex items-center justify-center gap-1.5 text-sm font-semibold ${
                    isPriceUp ? 'text-success-500' : isPriceDown ? 'text-danger-500' : 'text-zinc-400'
                  }`}
                >
                  {isPriceUp && <TrendingUp className="w-4 h-4" strokeWidth={2.5} />}
                  {isPriceDown && <TrendingDown className="w-4 h-4" strokeWidth={2.5} />}
                  <span className="font-mono">
                    {isPriceUp && '+'}
                    {priceChange.toFixed(3)}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Mini Sparkline Chart - 7 Day Trend */}
        <div className="h-[50px] -mx-2 opacity-60 group-hover:opacity-100 transition-opacity">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sparklineData}>
              <defs>
                <linearGradient id={`sparkGradient-${market.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={sparklineColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={sparklineColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="price"
                stroke={sparklineColor}
                strokeWidth={1.5}
                fill={`url(#sparkGradient-${market.id})`}
                animationDuration={800}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
          <p className="text-[10px] text-zinc-600 text-center mt-1 font-mono">7 DAY TREND</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-dark-surface/50 rounded-xl p-3 border border-dark-border/50">
            <div className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wider">
              Probability
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {formatProbability(market.probability)}
            </div>
          </div>

          <div className="bg-dark-surface/50 rounded-xl p-3 border border-dark-border/50">
            <div className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wider flex items-center gap-1">
              <BarChart3 className="w-3 h-3" />
              24h Volume
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {formatVolume(market.volume_24h)}
            </div>
          </div>
        </div>

        {/* Volume Progress Bar */}
        <div className="space-y-2">
          <div className="h-1.5 bg-dark-surface/80 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min((market.volume_24h || 0) / 10000 * 100, 100)}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
            />
          </div>
        </div>

        {/* Footer Meta */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-zinc-500">
            <span className="font-medium">{market.category || 'General'}</span>
            <span className="text-zinc-700">•</span>
            <span className="text-zinc-600">{market.market_type || 'Binary'}</span>
          </div>

          <div className="flex items-center gap-1.5 text-zinc-600 group-hover:text-primary-400 transition-colors">
            <Clock className="w-3 h-3" />
            <span className="font-mono">{formatRelativeTime(timestamp)}</span>
          </div>
        </div>

        {/* Hover Action Hint */}
        <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <ExternalLink className="w-4 h-4 text-primary-400" strokeWidth={2} />
        </div>
      </div>
    </motion.div>
  );
}
