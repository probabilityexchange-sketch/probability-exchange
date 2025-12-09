/**
 * VolumeChart Component - Bar chart showing 24h volume distribution
 */

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';

interface VolumeDataPoint {
  time: string;
  volume: number;
  period: string;
}

interface VolumeChartProps {
  data: VolumeDataPoint[];
  totalVolume: number;
}

export function VolumeChart({ data, totalVolume }: VolumeChartProps) {
  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const percentage = totalVolume > 0 ? (data.volume / totalVolume * 100) : 0;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-dark-card/95 backdrop-blur-md border border-primary-500/30 rounded-xl p-3 shadow-2xl"
      >
        <p className="text-xs text-zinc-400 mb-1.5 font-mono">
          {data.period}
        </p>
        <p className="text-2xl font-bold text-white font-mono">
          ${formatVolume(data.volume)}
        </p>
        <p className="text-xs text-primary-400 mt-1">
          {percentage.toFixed(1)}% of total
        </p>
      </motion.div>
    );
  };

  // Color based on volume level
  const getBarColor = (volume: number) => {
    const maxVolume = Math.max(...data.map(d => d.volume));
    const ratio = volume / maxVolume;

    if (ratio > 0.7) return '#10b981'; // High volume - green
    if (ratio > 0.4) return '#6366f1'; // Medium volume - primary
    return '#ef4444'; // Low volume - red
  };

  return (
    <div className="w-full h-[250px] sm:h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <XAxis
            dataKey="time"
            stroke="#52525b"
            style={{ fontSize: '11px', fontFamily: 'monospace' }}
            tickLine={false}
            axisLine={{ stroke: '#27272a', strokeWidth: 1 }}
            tick={{ fill: '#71717a' }}
          />

          <YAxis
            stroke="#52525b"
            style={{ fontSize: '11px', fontFamily: 'monospace' }}
            tickLine={false}
            axisLine={{ stroke: '#27272a', strokeWidth: 1 }}
            tick={{ fill: '#71717a' }}
            tickFormatter={(value) => formatVolume(value)}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }} />

          <Bar
            dataKey="volume"
            radius={[6, 6, 0, 0]}
            animationDuration={1000}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.volume)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Format volume for display
 */
function formatVolume(volume: number): string {
  if (volume >= 1000000) return `$${(volume / 1000000).toFixed(1)}M`;
  if (volume >= 1000) return `$${(volume / 1000).toFixed(1)}K`;
  return `$${volume.toFixed(0)}`;
}

/**
 * Generate mock volume data for last 24 hours (6 periods of 4h each)
 */
export function generateVolumeData(totalVolume: number = 50000): VolumeDataPoint[] {
  const periods = 6;
  const data: VolumeDataPoint[] = [];

  const periodLabels: string[] = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'];
  const periodNames: string[] = [
    'Midnight-4AM',
    '4AM-8AM',
    '8AM-Noon',
    'Noon-4PM',
    '4PM-8PM',
    '8PM-Midnight'
  ];

  // Distribute volume with realistic pattern (higher during business hours)
  const weights = [0.8, 1.0, 1.5, 1.8, 1.6, 1.2]; // Lower at night, higher during day
  const totalWeight = weights.reduce((sum, w) => sum + w, 0);

  for (let i = 0; i < periods; i++) {
    const weight = weights[i];
    if (weight !== undefined) {
      const baseVolume = (totalVolume * weight) / totalWeight;
      const variance = baseVolume * 0.3;
      const volume = baseVolume + (Math.random() - 0.5) * variance;

      data.push({
        time: periodLabels[i] || '00:00',
        volume: Math.max(0, volume),
        period: periodNames[i] || 'Unknown'
      });
    }
  }

  return data;
}
