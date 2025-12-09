/**
 * MarketStats Component - Dashboard metrics cards with animated numbers
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, DollarSign, Users } from 'lucide-react';

interface MarketStatsProps {
  totalMarkets: number;
  volume24h: number;
  averagePrice: number;
  activeTraders: number;
}

export function MarketStats({
  totalMarkets,
  volume24h,
  averagePrice,
  activeTraders
}: MarketStatsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <StatCard
        icon={<BarChart3 className="w-5 h-5" />}
        label="Total Markets"
        value={totalMarkets}
        format="number"
        gradient="from-blue-500 to-cyan-500"
      />

      <StatCard
        icon={<DollarSign className="w-5 h-5" />}
        label="24h Volume"
        value={volume24h}
        format="currency"
        gradient="from-purple-500 to-pink-500"
      />

      <StatCard
        icon={<TrendingUp className="w-5 h-5" />}
        label="Avg Price"
        value={averagePrice}
        format="price"
        gradient="from-emerald-500 to-teal-500"
      />

      <StatCard
        icon={<Users className="w-5 h-5" />}
        label="Active Traders"
        value={activeTraders}
        format="number"
        gradient="from-orange-500 to-red-500"
      />
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  format: 'number' | 'currency' | 'price';
  gradient: string;
}

function StatCard({ icon, label, value, format, gradient }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  // Animated count-up effect
  useEffect(() => {
    const duration = 1500; // 1.5 seconds
    const steps = 60;
    const increment = value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(current);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  const formatValue = (val: number): string => {
    switch (format) {
      case 'currency':
        if (val >= 1000000) return `$${(val / 1000000).toFixed(2)}M`;
        if (val >= 1000) return `$${(val / 1000).toFixed(1)}K`;
        return `$${val.toFixed(0)}`;
      case 'price':
        return `$${val.toFixed(3)}`;
      case 'number':
      default:
        if (val >= 1000000) return `${(val / 1000000).toFixed(2)}M`;
        if (val >= 1000) return `${(val / 1000).toFixed(1)}K`;
        return val.toFixed(0);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative group"
    >
      {/* Gradient Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-5 rounded-2xl group-hover:opacity-10 transition-opacity`} />

      {/* Border Gradient */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-transparent via-transparent to-transparent group-hover:via-primary-500/10 transition-all" />

      {/* Card Content */}
      <div className="relative bg-dark-card/60 backdrop-blur-sm rounded-2xl border border-dark-border group-hover:border-primary-500/30 transition-all p-6">
        {/* Icon */}
        <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${gradient} mb-4`}>
          <div className="text-white">
            {icon}
          </div>
        </div>

        {/* Label */}
        <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
          {label}
        </p>

        {/* Value */}
        <motion.p
          key={displayValue}
          initial={{ opacity: 0.5 }}
          animate={{ opacity: 1 }}
          className="text-3xl sm:text-4xl font-bold text-white font-mono"
        >
          {formatValue(displayValue)}
        </motion.p>

        {/* Trend Indicator (optional - could be enhanced with real data) */}
        <div className="mt-3 flex items-center gap-1.5">
          <TrendingUp className="w-3 h-3 text-success-500" />
          <span className="text-xs text-success-500 font-semibold">
            +12.5%
          </span>
          <span className="text-xs text-zinc-600">vs yesterday</span>
        </div>

        {/* Hover Glow Effect */}
        <div className={`absolute -inset-[1px] bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-20 blur-xl rounded-2xl -z-10 transition-opacity`} />
      </div>
    </motion.div>
  );
}

/**
 * Calculate market statistics from markets array
 */
export function calculateMarketStats(markets: any[]) {
  if (!markets || markets.length === 0) {
    return {
      totalMarkets: 0,
      volume24h: 0,
      averagePrice: 0,
      activeTraders: 0
    };
  }

  const totalVolume = markets.reduce((sum, m) => sum + (m.volume_24h || 0), 0);
  const avgPrice = markets.reduce((sum, m) => sum + m.current_price, 0) / markets.length;

  // Estimate active traders based on volume (rough approximation)
  const activeTraders = Math.floor(totalVolume / 100);

  return {
    totalMarkets: markets.length,
    volume24h: totalVolume,
    averagePrice: avgPrice,
    activeTraders
  };
}
