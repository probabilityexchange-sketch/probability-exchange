import { motion } from 'framer-motion';

interface NewsCardSkeletonProps {
  index?: number;
}

export default function NewsCardSkeleton({ index = 0 }: NewsCardSkeletonProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="bg-zinc-900/50 border border-zinc-700/50 rounded-lg p-4"
    >
      {/* Header skeleton */}
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex-1 space-y-2">
          {/* Title skeleton */}
          <div className="h-6 bg-zinc-800 rounded animate-pulse w-3/4" />
          {/* Description skeleton */}
          <div className="space-y-1">
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-full" />
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-5/6" />
          </div>
        </div>
        {/* Sentiment badge skeleton */}
        <div className="h-8 w-24 bg-zinc-800 rounded-lg animate-pulse" />
      </div>

      {/* Footer skeleton */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-700/50">
        <div className="flex items-center gap-4">
          {/* Source skeleton */}
          <div className="h-3 w-20 bg-zinc-800 rounded animate-pulse" />
          <div className="h-3 w-3 bg-zinc-800 rounded-full animate-pulse" />
          {/* Time skeleton */}
          <div className="h-3 w-16 bg-zinc-800 rounded animate-pulse" />
          <div className="h-3 w-3 bg-zinc-800 rounded-full animate-pulse" />
          {/* Tags skeleton */}
          <div className="flex gap-1">
            <div className="h-5 w-12 bg-zinc-800 rounded animate-pulse" />
            <div className="h-5 w-12 bg-zinc-800 rounded animate-pulse" />
          </div>
        </div>
        {/* Impact meter skeleton */}
        <div className="h-8 w-16 bg-zinc-800 rounded animate-pulse" />
      </div>
    </motion.div>
  );
}
