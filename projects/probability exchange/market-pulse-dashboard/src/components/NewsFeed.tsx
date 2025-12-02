import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { NewsArticle } from '../types/news';
import NewsCard from './NewsCard';
import NewsCardSkeleton from './NewsCardSkeleton';

interface NewsFeedProps {
  category?: string;
  limit?: number;
  onBreakingNews?: (article: NewsArticle) => void;
}

export default function NewsFeed({ category, limit = 20, onBreakingNews }: NewsFeedProps) {
  const notifiedArticles = useRef(new Set<string>());
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(category);

  const { data, isLoading, error } = useQuery({
    queryKey: ['news', selectedCategory, limit],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      params.append('limit', limit.toString());

      const response = await fetch(`http://localhost:8000/api/v1/news?${params}`);
      if (!response.ok) throw new Error('Failed to fetch news');
      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Detect and notify about breaking news
  useEffect(() => {
    if (!data?.articles || !onBreakingNews) return;

    const breakingNews = data.articles.filter(
      (article: NewsArticle) =>
        article.is_breaking && !notifiedArticles.current.has(article.id)
    );

    breakingNews.forEach((article: NewsArticle) => {
      notifiedArticles.current.add(article.id);
      onBreakingNews(article);
    });
  }, [data?.articles, onBreakingNews]);

  const categories = [
    { id: 'crypto', name: 'Crypto', icon: '₿' },
    { id: 'politics', name: 'Politics', icon: '🏛️' },
    { id: 'technology', name: 'Tech', icon: '💻' },
    { id: 'economy', name: 'Economy', icon: '📊' },
    { id: 'climate', name: 'Climate', icon: '🌍' },
  ];

  if (error) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-lg">
        <p className="text-red-400">Error loading news: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-3 px-3 sm:mx-0 sm:px-0">
        <button
          onClick={() => setSelectedCategory(undefined)}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0 ${
            !selectedCategory
              ? 'bg-blue-500 text-white'
              : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 active:bg-zinc-600'
          }`}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0 ${
              selectedCategory === cat.id
                ? 'bg-blue-500 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 active:bg-zinc-600'
            }`}
          >
            <span className="mr-1">{cat.icon}</span>
            {cat.name}
          </button>
        ))}
      </div>

      {/* News Feed */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <NewsCardSkeleton key={i} index={i} />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {data?.articles?.length === 0 ? (
            <div className="p-6 bg-zinc-800/50 border border-zinc-700 rounded-lg text-center">
              <p className="text-zinc-400">No news articles found</p>
            </div>
          ) : (
            data?.articles?.map((article: NewsArticle, index: number) => (
              <NewsCard key={article.id} article={article} index={index} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
