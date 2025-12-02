/**
 * Toast Component - Notification system for breaking news
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle, TrendingUp, Zap } from 'lucide-react';
import { useEffect } from 'react';

export interface ToastProps {
  id: string;
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error' | 'breaking';
  duration?: number;
  onClose: (id: string) => void;
  onClick?: () => void;
}

const iconMap = {
  info: AlertCircle,
  success: TrendingUp,
  warning: AlertCircle,
  error: AlertCircle,
  breaking: Zap,
};

const colorMap = {
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    icon: 'text-blue-400',
  },
  success: {
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    text: 'text-green-400',
    icon: 'text-green-400',
  },
  warning: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
    icon: 'text-yellow-400',
  },
  error: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    icon: 'text-red-400',
  },
  breaking: {
    bg: 'bg-gradient-to-r from-red-500/10 to-orange-500/10',
    border: 'border-red-500/50',
    text: 'text-red-400',
    icon: 'text-red-500',
  },
};

export function Toast({
  id,
  title,
  message,
  type = 'info',
  duration = 5000,
  onClose,
  onClick,
}: ToastProps) {
  const Icon = iconMap[type];
  const colors = colorMap[type];

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`relative w-80 sm:w-96 ${colors.bg} backdrop-blur-sm border ${colors.border} rounded-xl p-4 shadow-2xl ${
        onClick ? 'cursor-pointer hover:scale-[1.02]' : ''
      } transition-transform`}
      onClick={onClick}
    >
      {/* Breaking news pulse animation */}
      {type === 'breaking' && (
        <div className="absolute inset-0 rounded-xl bg-red-500/20 animate-pulse pointer-events-none" />
      )}

      <div className="relative flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${colors.icon}`}>
          <Icon className="w-5 h-5" strokeWidth={2} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={`font-semibold text-sm ${colors.text}`}>
              {type === 'breaking' && (
                <span className="inline-flex items-center gap-1 mr-2 px-2 py-0.5 bg-red-500/20 rounded text-xs">
                  <Zap className="w-3 h-3" />
                  BREAKING
                </span>
              )}
              {title}
            </h4>

            {/* Close button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose(id);
              }}
              className="flex-shrink-0 p-1 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-zinc-400 hover:text-white" />
            </button>
          </div>

          <p className="text-sm text-zinc-400 mt-1 line-clamp-2">{message}</p>

          {/* Progress bar for auto-dismiss */}
          {duration > 0 && (
            <motion.div
              className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 to-orange-500 rounded-b-xl"
              initial={{ scaleX: 1 }}
              animate={{ scaleX: 0 }}
              transition={{ duration: duration / 1000, ease: 'linear' }}
              style={{ transformOrigin: 'left' }}
            />
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function ToastContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
      <AnimatePresence mode="popLayout">{children}</AnimatePresence>
    </div>
  );
}
