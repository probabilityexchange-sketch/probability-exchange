import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onFilterChange: (filters: MarketFilters) => void;
  currentFilters: MarketFilters;
}

export interface MarketFilters {
  platforms: string[];
  categories: string[];
  priceRange: {
    min: number;
    max: number;
  };
  sortBy: 'volume' | 'activity' | 'trending' | 'newest';
}

export default function Sidebar({ isOpen, onClose, onFilterChange, currentFilters }: SidebarProps) {
  const [localFilters, setLocalFilters] = useState<MarketFilters>(currentFilters);

  const platforms = [
    { id: 'kalshi', name: 'Kalshi', icon: '📊' },
    { id: 'polymarket', name: 'Polymarket', icon: '🎯' },
    { id: 'manifold', name: 'Manifold', icon: '🌟' },
  ];

  const categories = [
    { id: 'politics', name: 'Politics', icon: '🏛️' },
    { id: 'crypto', name: 'Crypto', icon: '₿' },
    { id: 'sports', name: 'Sports', icon: '⚽' },
    { id: 'technology', name: 'Tech', icon: '💻' },
    { id: 'economy', name: 'Economy', icon: '📈' },
    { id: 'science', name: 'Science', icon: '🔬' },
  ];

  const sortOptions = [
    { id: 'volume', name: 'Volume', icon: '💰' },
    { id: 'activity', name: 'Activity', icon: '🔥' },
    { id: 'trending', name: 'Trending', icon: '📈' },
    { id: 'newest', name: 'Newest', icon: '🆕' },
  ];

  const togglePlatform = (platformId: string) => {
    const newPlatforms = localFilters.platforms.includes(platformId)
      ? localFilters.platforms.filter(p => p !== platformId)
      : [...localFilters.platforms, platformId];

    const newFilters = { ...localFilters, platforms: newPlatforms };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const toggleCategory = (categoryId: string) => {
    const newCategories = localFilters.categories.includes(categoryId)
      ? localFilters.categories.filter(c => c !== categoryId)
      : [...localFilters.categories, categoryId];

    const newFilters = { ...localFilters, categories: newCategories };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const setSortBy = (sortBy: MarketFilters['sortBy']) => {
    const newFilters = { ...localFilters, sortBy };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const defaultFilters: MarketFilters = {
      platforms: [],
      categories: [],
      priceRange: { min: 0, max: 100 },
      sortBy: 'trending',
    };
    setLocalFilters(defaultFilters);
    onFilterChange(defaultFilters);
  };

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          x: isOpen ? 0 : '-100%',
        }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="fixed left-0 top-0 bottom-0 w-80 bg-zinc-900 border-r border-zinc-800 z-50 lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] overflow-y-auto"
      >
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>🔍</span>
              <span>Quick Filters</span>
            </h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-zinc-800 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Sort By */}
          <div>
            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
              Sort By
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {sortOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSortBy(option.id as MarketFilters['sortBy'])}
                  className={`p-3 rounded-lg text-sm font-medium transition-all ${
                    localFilters.sortBy === option.id
                      ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  <span className="mr-1.5">{option.icon}</span>
                  {option.name}
                </button>
              ))}
            </div>
          </div>

          {/* Platforms */}
          <div>
            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
              Platforms
            </h3>
            <div className="space-y-2">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  onClick={() => togglePlatform(platform.id)}
                  className={`w-full p-3 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                    localFilters.platforms.includes(platform.id)
                      ? 'bg-blue-500/10 border-2 border-blue-500 text-blue-400'
                      : 'bg-zinc-800 border-2 border-transparent text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  <span>{platform.icon}</span>
                  <span className="flex-1 text-left">{platform.name}</span>
                  {localFilters.platforms.includes(platform.id) && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div>
            <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-3">
              Categories
            </h3>
            <div className="space-y-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => toggleCategory(category.id)}
                  className={`w-full p-3 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                    localFilters.categories.includes(category.id)
                      ? 'bg-purple-500/10 border-2 border-purple-500 text-purple-400'
                      : 'bg-zinc-800 border-2 border-transparent text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  <span>{category.icon}</span>
                  <span className="flex-1 text-left">{category.name}</span>
                  {localFilters.categories.includes(category.id) && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Clear Filters */}
          {(localFilters.platforms.length > 0 || localFilters.categories.length > 0) && (
            <button
              onClick={clearFilters}
              className="w-full p-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-sm font-medium transition-colors"
            >
              Clear All Filters
            </button>
          )}
        </div>
      </motion.aside>
    </>
  );
}
