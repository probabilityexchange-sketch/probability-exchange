import { NewsArticle } from '../types/news';
import SentimentIndicator from './SentimentIndicator';
import ImpactMeter from './ImpactMeter';
import { motion } from 'framer-motion';

interface NewsCardProps {
  article: NewsArticle;
  index?: number;
}

export default function NewsCard({ article, index = 0 }: NewsCardProps) {
  const timeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ scale: 1.01, y: -2 }}
      className={`bg-zinc-900/50 border rounded-lg p-3 sm:p-4 hover:bg-zinc-800/50 transition-all cursor-pointer ${
        article.is_breaking
          ? 'border-red-500/50 bg-red-500/5'
          : 'border-zinc-700/50'
      }`}
      onClick={() => window.open(article.url, '_blank')}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold text-base sm:text-lg leading-tight mb-1">
            {article.is_breaking && (
              <span className="inline-block px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded mr-2 animate-pulse">
                BREAKING
              </span>
            )}
            {article.title}
          </h3>
          <p className="text-zinc-400 text-sm line-clamp-2">{article.description}</p>
        </div>
        <div className="sm:flex-shrink-0">
          <SentimentIndicator sentiment={article.sentiment} />
        </div>
      </div>

      {/* Impact and Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0 mt-3 pt-3 border-t border-zinc-700/50">
        <div className="flex items-center flex-wrap gap-2 sm:gap-4 text-xs text-zinc-500">
          <span className="font-medium text-zinc-400">{article.source}</span>
          <span className="hidden sm:inline">•</span>
          <span>{timeAgo(article.published_at)}</span>
          {article.related_markets.length > 0 && (
            <>
              <span className="hidden sm:inline">•</span>
              <div className="flex gap-1 flex-wrap">
                {article.related_markets.slice(0, 2).map((market) => (
                  <span
                    key={market}
                    className="px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded text-xs"
                  >
                    {market}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
        <div className="self-start sm:self-auto">
          <ImpactMeter impact={article.impact} />
        </div>
      </div>
    </motion.div>
  );
}
