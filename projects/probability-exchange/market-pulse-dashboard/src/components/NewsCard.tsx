import { useState } from 'react';
import { NewsArticle } from '../types/news';
import SentimentIndicator from './SentimentIndicator';
import ImpactMeter from './ImpactMeter';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, AlertTriangle, ExternalLink, TrendingUp, TrendingDown } from 'lucide-react';

interface NewsCardProps {
  article: NewsArticle;
  index?: number;
}

export default function NewsCard({ article, index = 0 }: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

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

  const getSignalColor = (score: number) => {
    if (score >= 3) return 'bg-purple-500 text-white shadow-purple-500/50';
    if (score === 2) return 'bg-blue-500 text-white shadow-blue-500/50';
    if (score === 1) return 'bg-zinc-700 text-zinc-300';
    return 'bg-zinc-800 text-zinc-500';
  };

  const getSignalLabel = (score: number) => {
    if (score >= 3) return 'HIGH SIGNAL';
    if (score === 2) return 'MEDIUM SIGNAL';
    if (score === 1) return 'LOW SIGNAL';
    return 'NO SIGNAL';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ y: -2 }}
      className={`bg-zinc-900/50 border rounded-lg overflow-hidden transition-all ${
        article.is_breaking
          ? 'border-red-500/50 bg-red-500/5'
          : 'border-zinc-700/50 hover:border-zinc-600'
      }`}
    >
      <div className="p-3 sm:p-4 cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4 mb-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              {article.is_breaking && (
                <span className="inline-block px-2 py-0.5 bg-red-500 text-white text-[10px] font-bold rounded animate-pulse">
                  BREAKING
                </span>
              )}
              {/* Signal Score Badge */}
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded shadow-sm ${getSignalColor(article.signal_score || 0)}`}>
                {getSignalLabel(article.signal_score || 0)}
              </span>
            </div>

            <h3 className="text-white font-semibold text-base sm:text-lg leading-tight mb-1 group-hover:text-blue-400 transition-colors">
              {article.title}
            </h3>
            <p className="text-zinc-400 text-sm line-clamp-2">{article.description}</p>
          </div>
          <div className="sm:flex-shrink-0 flex flex-row sm:flex-col items-center sm:items-end gap-2">
            <SentimentIndicator sentiment={article.sentiment} />
            <ImpactMeter impact={article.impact} />
          </div>
        </div>

        {/* Impact and Metadata */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0 mt-3 pt-3 border-t border-zinc-700/50">
          <div className="flex items-center flex-wrap gap-2 sm:gap-4 text-xs text-zinc-500">
            <span className="font-medium text-zinc-400">{article.source}</span>
            <span>•</span>
            <span>{timeAgo(article.published_at)}</span>
          </div>

          <button
            className={`flex items-center gap-1 text-xs font-bold uppercase transition-colors ${
              isExpanded ? 'text-blue-400' : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {isExpanded ? 'Hide Market Impact' : 'Show Market Impact'}
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Expandable Impact Section */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-zinc-950/50 border-t border-zinc-800"
          >
            <div className="p-4 space-y-4">
              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">
                Prediction Market Impact Analysis
              </h4>

              {article.impact_details && article.impact_details.length > 0 ? (
                <div className="grid gap-3">
                  {article.impact_details.map((detail, idx) => (
                    <div key={idx} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 flex flex-col sm:flex-row sm:items-center gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                            {detail.platform}
                          </span>
                          <span className="text-sm font-medium text-zinc-200">
                            {detail.market_name}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-500 italic">
                          "{detail.interpretation}"
                        </p>
                      </div>

                      <div className="flex items-center gap-4 bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                        <div className="text-center">
                          <div className="text-[10px] text-zinc-500 uppercase">Was</div>
                          <div className="text-zinc-400 font-mono">{(detail.start_prob * 100).toFixed(0)}%</div>
                        </div>
                        <div className="text-zinc-600">
                          <ArrowRightIcon />
                        </div>
                        <div className="text-center">
                          <div className="text-[10px] text-zinc-500 uppercase">Now</div>
                          <div className={`font-bold font-mono ${
                            detail.end_prob > detail.start_prob ? 'text-green-400' :
                            detail.end_prob < detail.start_prob ? 'text-red-400' : 'text-zinc-200'
                          }`}>
                            {(detail.end_prob * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      <a
                        href={detail.market_url}
                        target="_blank"
                        rel="noreferrer"
                        className="p-2 hover:bg-blue-500/10 hover:text-blue-400 text-zinc-500 rounded-lg transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-sm text-zinc-500 italic">
                  No specific market linkages detected yet.
                </div>
              )}

              {/* Disclaimer Footer */}
              <div className="mt-4 pt-3 border-t border-zinc-800/50 flex items-start gap-2 text-[10px] text-zinc-600">
                <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                <p>
                  <span className="font-bold text-zinc-500">Risk Disclaimer:</span> Prediction markets are volatile and speculative.
                  Odds data may be delayed by 30-60 seconds. Liquidity varies by market.
                  This is not financial advice; do your own research.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ArrowRightIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3.33331 8H12.6666" stroke="currentColor" strokeWidth="1.33" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M8.66669 4L12.6667 8L8.66669 12" stroke="currentColor" strokeWidth="1.33" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
