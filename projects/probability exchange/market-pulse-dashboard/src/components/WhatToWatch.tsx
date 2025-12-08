import { motion } from 'framer-motion';
import { ArrowRight, Calendar, AlertCircle, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { NewsArticle } from '@/types/news';

export default function WhatToWatch() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['news', 'whatToWatch'],
    queryFn: () => apiClient.getNews(5),
    refetchInterval: 60000, // Refresh every minute
  });

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return dateString;
    }
  };

  const getImpactColor = (score: number, isBreaking: boolean) => {
    if (isBreaking && score > 0.5) return 'bg-red-500/20 text-red-400 border-red-500/20';
    if (score > 0.7) return 'bg-red-500/20 text-red-400 border-red-500/20';
    if (score > 0.4) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20';
    return 'bg-blue-500/20 text-blue-400 border-blue-500/20';
  };

  const getImpactLabel = (score: number, isBreaking: boolean) => {
    if (isBreaking) return 'BREAKING';
    if (score > 0.8) return 'CRITICAL';
    if (score > 0.6) return 'HIGH IMPACT';
    return 'WATCH';
  };

  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800 rounded-xl overflow-hidden h-full flex flex-col">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between shrink-0">
        <h2 className="font-bold text-white flex items-center gap-2">
          <Calendar className="w-5 h-5 text-purple-400" />
          What to Watch
        </h2>
        <div className="flex items-center gap-2">
          {isLoading && <RefreshCw className="w-3 h-3 text-zinc-500 animate-spin" />}
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
            Live
          </span>
        </div>
      </div>

      <div className="overflow-y-auto custom-scrollbar flex-1 divide-y divide-zinc-800/50">
        {isLoading && !data ? (
           <div className="p-8 text-center text-zinc-500 text-sm">Loading market events...</div>
        ) : isError ? (
           <div className="p-8 text-center text-red-400 text-sm cursor-pointer hover:underline" onClick={() => refetch()}>
             Failed to load. Click to retry.
           </div>
        ) : data?.articles.length === 0 ? (
           <div className="p-8 text-center text-zinc-500 text-sm">No significant market events found.</div>
        ) : (
          data?.articles.map((article: NewsArticle) => (
            <div key={article.id} className="p-4 hover:bg-zinc-800/30 transition-colors group cursor-pointer">
              <div className="flex justify-between items-start mb-1 gap-2">
                <h3 className="font-semibold text-zinc-200 group-hover:text-white transition-colors line-clamp-2 text-sm">
                  {article.title}
                </h3>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase border whitespace-nowrap ${getImpactColor(article.impact.score, article.is_breaking)}`}>
                  {getImpactLabel(article.impact.score, article.is_breaking)}
                </span>
              </div>

              <div className="flex items-center justify-between mb-2">
                 <p className="text-xs text-zinc-500">{formatDate(article.published_at)}</p>
                 <span className="text-[10px] text-zinc-600 uppercase font-medium">{article.source}</span>
              </div>

              <p className="text-sm text-zinc-400 mb-3 leading-relaxed line-clamp-3">
                {article.description}
              </p>

              {article.related_markets.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2 mb-2">
                  {article.related_markets.slice(0, 2).map((market, idx) => (
                    <span key={idx} className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded">
                      #{market}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center text-xs font-medium text-blue-400 group-hover:text-blue-300 transition-colors">
                Analysis & Markets <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
