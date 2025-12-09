/**
 * MarketDetailModal Component - Detailed market view with charts
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, TrendingUp, TrendingDown, BarChart3, Clock, Calendar } from 'lucide-react';
import type { Market } from '@/types/market';
import { PriceChart, generatePriceHistory } from './PriceChart';
import { VolumeChart, generateVolumeData } from './VolumeChart';

interface MarketDetailModalProps {
  market: Market | null;
  isOpen: boolean;
  onClose: () => void;
}

export function MarketDetailModal({ market, isOpen, onClose }: MarketDetailModalProps) {
  if (!market) return null;

  // Generate mock data for charts
  const priceHistory = generatePriceHistory(market.current_price, 24);
  const volumeData = generateVolumeData(market.volume_24h || 50000);

  const formatPrice = (price: number) => `$${price.toFixed(3)}`;
  const formatVolume = (volume?: number) => {
    if (!volume) return 'N/A';
    if (volume >= 1000000) return `$${(volume / 1000000).toFixed(2)}M`;
    if (volume >= 1000) return `$${(volume / 1000).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  const priceChange = market.change_24h || 0;
  const isPriceUp = priceChange > 0;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', duration: 0.5 }}
              className="w-full max-w-5xl max-h-[90vh] overflow-y-auto pointer-events-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="bg-dark-card/95 backdrop-blur-xl rounded-3xl border border-primary-500/30 shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="relative bg-gradient-to-br from-primary-500/10 via-transparent to-purple-500/10 border-b border-dark-border p-6 sm:p-8">
                  {/* Close Button */}
                  <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 rounded-xl bg-dark-surface/50 hover:bg-dark-surface border border-dark-border hover:border-primary-500/50 transition-all group"
                  >
                    <X className="w-5 h-5 text-zinc-400 group-hover:text-white transition-colors" />
                  </button>

                  {/* Title */}
                  <div className="pr-12">
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${getPlatformColor(market.platform)}`}>
                        {market.platform}
                      </span>
                      <span className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-zinc-500/20 text-zinc-400 border border-zinc-500/30">
                        {market.category || 'General'}
                      </span>
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-bold text-white leading-tight mb-2">
                      {market.question || market.title}
                    </h2>
                    {market.description && (
                      <p className="text-zinc-400 text-sm leading-relaxed">
                        {market.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 sm:p-8 space-y-8">
                  {/* Price Stats Row */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {/* Current Price */}
                    <div className="bg-dark-surface/50 rounded-2xl p-6 border border-dark-border">
                      <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
                        Current Price
                      </p>
                      <p className="text-4xl font-bold text-white font-mono mb-2">
                        {formatPrice(market.current_price)}
                      </p>
                      <div className={`flex items-center gap-1.5 text-sm font-semibold ${
                        isPriceUp ? 'text-success-500' : 'text-danger-500'
                      }`}>
                        {isPriceUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        <span>{isPriceUp && '+'}{(priceChange * 100).toFixed(2)}%</span>
                        <span className="text-zinc-600">24h</span>
                      </div>
                    </div>

                    {/* Probability */}
                    <div className="bg-dark-surface/50 rounded-2xl p-6 border border-dark-border">
                      <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
                        Probability
                      </p>
                      <p className="text-4xl font-bold text-white font-mono mb-2">
                        {((market.probability || market.current_price) * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-zinc-600">
                        Market consensus
                      </p>
                    </div>

                    {/* Volume */}
                    <div className="bg-dark-surface/50 rounded-2xl p-6 border border-dark-border">
                      <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" />
                        24h Volume
                      </p>
                      <p className="text-4xl font-bold text-white font-mono mb-2">
                        {formatVolume(market.volume_24h)}
                      </p>
                      <p className="text-sm text-zinc-600">
                        Total: {formatVolume(market.total_volume)}
                      </p>
                    </div>
                  </div>

                  {/* Price Chart */}
                  <div className="bg-dark-surface/30 rounded-2xl p-6 border border-dark-border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Price History</h3>
                      <span className="text-xs text-zinc-500 font-mono">Last 24 hours</span>
                    </div>
                    <PriceChart data={priceHistory} currentPrice={market.current_price} />
                  </div>

                  {/* Volume Chart */}
                  <div className="bg-dark-surface/30 rounded-2xl p-6 border border-dark-border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Volume Distribution</h3>
                      <span className="text-xs text-zinc-500 font-mono">Last 24 hours</span>
                    </div>
                    <VolumeChart data={volumeData} totalVolume={market.volume_24h || 50000} />
                  </div>

                  {/* Market Info */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-dark-surface/30 rounded-xl p-4 border border-dark-border">
                      <div className="flex items-center gap-2 text-zinc-400 mb-1">
                        <Clock className="w-4 h-4" />
                        <span className="text-xs font-medium uppercase tracking-wider">Last Updated</span>
                      </div>
                      <p className="text-white font-mono">
                        {market.updated_at ? new Date(market.updated_at).toLocaleString() : 'Just now'}
                      </p>
                    </div>

                    <div className="bg-dark-surface/30 rounded-xl p-4 border border-dark-border">
                      <div className="flex items-center gap-2 text-zinc-400 mb-1">
                        <Calendar className="w-4 h-4" />
                        <span className="text-xs font-medium uppercase tracking-wider">Close Time</span>
                      </div>
                      <p className="text-white font-mono">
                        {market.close_time ? new Date(market.close_time).toLocaleString() : 'TBD'}
                      </p>
                    </div>
                  </div>

                  {/* Action Button */}
                  {market.url && (
                    <a
                      href={market.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full bg-gradient-to-r from-primary-500 to-purple-500 hover:from-primary-600 hover:to-purple-600 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl"
                    >
                      <span>Trade on {market.platform}</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

// Platform badge colors (same as MarketCard)
function getPlatformColor(platform: string) {
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
}
