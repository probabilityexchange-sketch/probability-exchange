/**
 * PriceChart Component - Line chart showing price history over time
 */

import { XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { motion } from 'framer-motion';

interface PriceDataPoint {
  time: Date;
  price: number;
}

interface PriceChartProps {
  data: PriceDataPoint[];
  currentPrice: number;
}

export function PriceChart({ data, currentPrice }: PriceChartProps) {
  // Format data for recharts
  const chartData = data.map(point => ({
    time: point.time.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }),
    price: point.price,
    timestamp: point.time.getTime()
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const time = new Date(data.timestamp);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-dark-card/95 backdrop-blur-md border border-primary-500/30 rounded-xl p-3 shadow-2xl"
      >
        <p className="text-xs text-zinc-400 mb-1.5 font-mono">
          {time.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
          })}
        </p>
        <p className="text-2xl font-bold text-white font-mono">
          ${data.price.toFixed(3)}
        </p>
        <p className="text-xs text-primary-400 mt-1">
          {data.price > currentPrice ? '+' : ''}
          {((data.price - currentPrice) / currentPrice * 100).toFixed(2)}% vs current
        </p>
      </motion.div>
    );
  };

  // Calculate min/max for Y-axis with padding
  const prices = chartData.map(d => d.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const padding = (maxPrice - minPrice) * 0.1;

  return (
    <div className="w-full h-[300px] sm:h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <XAxis
            dataKey="time"
            stroke="#52525b"
            style={{ fontSize: '11px', fontFamily: 'monospace' }}
            tickLine={false}
            axisLine={{ stroke: '#27272a', strokeWidth: 1 }}
            tick={{ fill: '#71717a' }}
          />

          <YAxis
            domain={[minPrice - padding, maxPrice + padding]}
            stroke="#52525b"
            style={{ fontSize: '11px', fontFamily: 'monospace' }}
            tickLine={false}
            axisLine={{ stroke: '#27272a', strokeWidth: 1 }}
            tick={{ fill: '#71717a' }}
            tickFormatter={(value) => `$${value.toFixed(3)}`}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#6366f1', strokeWidth: 1, strokeDasharray: '5 5' }} />

          <Area
            type="monotone"
            dataKey="price"
            stroke="#6366f1"
            strokeWidth={2.5}
            fill="url(#priceGradient)"
            animationDuration={1000}
            dot={false}
            activeDot={{
              r: 6,
              fill: '#6366f1',
              stroke: '#fff',
              strokeWidth: 2
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Generate mock price history for last 24 hours
 */
export function generatePriceHistory(currentPrice: number, hours: number = 24): PriceDataPoint[] {
  const data: PriceDataPoint[] = [];
  const now = Date.now();

  for (let i = hours; i >= 0; i--) {
    const time = new Date(now - i * 60 * 60 * 1000);

    // Add realistic random walk with mean reversion
    const randomWalk = (Math.random() - 0.5) * 0.08;
    const meanReversion = (0.5 - currentPrice) * 0.02;
    const price = Math.max(0.01, Math.min(0.99, currentPrice + randomWalk + meanReversion));

    data.push({ time, price });
  }

  return data;
}
