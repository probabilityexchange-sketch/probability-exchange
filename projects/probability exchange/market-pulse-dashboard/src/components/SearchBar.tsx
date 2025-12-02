/**
 * SearchBar Component - Market search and filter controls
 */

import { motion } from 'framer-motion';
import { Search, Filter, X } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SearchBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  category: string;
  onCategoryChange: (value: string) => void;
  categories: string[];
}

export function SearchBar({
  searchTerm,
  onSearchChange,
  category,
  onCategoryChange,
  categories,
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);

  // Keyboard shortcut (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('market-search')?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleClear = () => {
    onSearchChange('');
    document.getElementById('market-search')?.focus();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="flex flex-col sm:flex-row gap-3 mb-8"
    >
      {/* Search Input */}
      <div className="relative flex-1 group">
        {/* Focus Glow Effect */}
        {isFocused && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute -inset-0.5 bg-gradient-primary opacity-20 blur-xl rounded-2xl"
          />
        )}

        <div className="relative">
          <Search
            className={`absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 transition-colors ${
              isFocused ? 'text-primary-400' : 'text-zinc-500'
            }`}
            strokeWidth={2}
          />

          <input
            id="market-search"
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Search markets, categories, platforms..."
            className="w-full pl-14 pr-24 py-4 rounded-2xl bg-dark-surface/80 backdrop-blur-sm border border-dark-border text-white placeholder-zinc-600 focus:outline-none focus:border-primary-500/50 transition-all"
          />

          <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
            {searchTerm && (
              <button
                onClick={handleClear}
                className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                aria-label="Clear search"
              >
                <X className="w-4 h-4 text-zinc-500" strokeWidth={2} />
              </button>
            )}

            <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-dark-card/80 border border-dark-border text-xs font-mono text-zinc-500">
              <span className="text-[10px]">⌘</span>K
            </kbd>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="relative">
        <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" strokeWidth={2} />
        <select
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="appearance-none w-full sm:w-auto pl-12 pr-10 py-4 rounded-2xl bg-dark-surface/80 backdrop-blur-sm border border-dark-border text-white focus:outline-none focus:border-primary-500/50 transition-all cursor-pointer"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
            backgroundPosition: 'right 0.75rem center',
            backgroundRepeat: 'no-repeat',
            backgroundSize: '1.5em 1.5em',
          }}
        >
          <option value="" className="bg-dark-card">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat} className="bg-dark-card">
              {cat}
            </option>
          ))}
        </select>

        {category && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-primary-500 rounded-full border-2 border-dark-bg"
          />
        )}
      </div>
    </motion.div>
  );
}
