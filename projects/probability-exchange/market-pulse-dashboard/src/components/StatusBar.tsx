/**
 * StatusBar Component - Connection and API status indicators
 */

import { motion } from 'framer-motion';
import { Wifi, WifiOff, Database, TrendingUp, RefreshCw } from 'lucide-react';

interface StatusBarProps {
  wsConnected: boolean;
  apiStatus: 'healthy' | 'degraded' | 'error' | 'operational';
  marketsCount: number;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export function StatusBar({
  wsConnected,
  apiStatus,
  marketsCount,
  onRefresh,
  isRefreshing = false,
}: StatusBarProps) {
  const isApiHealthy = apiStatus === 'operational' || apiStatus === 'healthy';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="flex flex-wrap items-center justify-between gap-3 mb-6"
    >
      <div className="flex items-center gap-3 flex-wrap">
        {/* WebSocket Status */}
        <div
          className={`flex items-center gap-2.5 px-4 py-2 rounded-xl backdrop-blur-sm border transition-all ${
            wsConnected
              ? 'bg-success-500/10 border-success-500/30'
              : 'bg-danger-500/10 border-danger-500/30'
          }`}
        >
          <span className="relative flex h-2 w-2">
            {wsConnected && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75" />
            )}
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                wsConnected ? 'bg-success-500' : 'bg-danger-500'
              }`}
            />
          </span>
          {wsConnected ? (
            <Wifi className="w-3.5 h-3.5 text-success-500" strokeWidth={2.5} />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-danger-500" strokeWidth={2.5} />
          )}
          <span
            className={`text-xs font-semibold font-mono tracking-wide ${
              wsConnected ? 'text-success-500' : 'text-danger-500'
            }`}
          >
            {wsConnected ? 'WS ACTIVE' : 'WS OFFLINE'}
          </span>
        </div>

        {/* API Status */}
        <div
          className={`flex items-center gap-2.5 px-4 py-2 rounded-xl backdrop-blur-sm border transition-all ${
            isApiHealthy
              ? 'bg-primary-500/10 border-primary-500/30'
              : 'bg-danger-500/10 border-danger-500/30'
          }`}
        >
          <Database
            className={`w-3.5 h-3.5 ${
              isApiHealthy ? 'text-primary-400' : 'text-danger-500'
            }`}
            strokeWidth={2.5}
          />
          <span
            className={`text-xs font-semibold font-mono tracking-wide ${
              isApiHealthy ? 'text-primary-400' : 'text-danger-500'
            }`}
          >
            API {isApiHealthy ? 'OK' : 'ERROR'}
          </span>
        </div>

        {/* Markets Count */}
        <div className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-dark-surface/80 border border-dark-border backdrop-blur-sm">
          <TrendingUp className="w-3.5 h-3.5 text-zinc-400" strokeWidth={2.5} />
          <span className="text-xs font-semibold font-mono text-zinc-300 tracking-wide">
            {marketsCount.toLocaleString()}
          </span>
          <span className="text-xs font-medium text-zinc-500">MARKETS</span>
        </div>
      </div>

      {/* Refresh Button */}
      {onRefresh && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onRefresh}
          disabled={isRefreshing}
          className="group relative px-5 py-2 rounded-xl bg-dark-surface border border-dark-border hover:border-primary-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
        >
          {/* Hover Gradient Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />

          <div className="relative flex items-center gap-2">
            <RefreshCw
              className={`w-3.5 h-3.5 text-zinc-400 group-hover:text-white transition-colors ${
                isRefreshing ? 'animate-spin' : ''
              }`}
              strokeWidth={2.5}
            />
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-white transition-colors tracking-wide">
              {isRefreshing ? 'REFRESHING...' : 'REFRESH'}
            </span>
          </div>
        </motion.button>
      )}
    </motion.div>
  );
}
