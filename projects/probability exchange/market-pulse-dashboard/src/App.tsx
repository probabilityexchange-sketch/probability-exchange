/**
 * App Component - Main dashboard application
 */

import { useState, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/Header';
import { StatusBar } from './components/StatusBar';
import { SearchBar } from './components/SearchBar';
import { MarketGrid } from './components/MarketGrid';
import { MarketStats, calculateMarketStats } from './components/MarketStats';
import { MarketDetailModal } from './components/MarketDetailModal';
import NewsFeed from './components/NewsFeed';
import { ErrorBoundary } from './components/ErrorBoundary';
import Sidebar, { MarketFilters } from './components/Sidebar';
import { useMarkets } from './hooks/useMarkets';
import { useWebSocket } from './hooks/useWebSocket';
import { useFavorites } from './hooks/useFavorites';
import { useToast } from './hooks/useToast';
import { Toast, ToastContainer } from './components/Toast';
import type { Market } from './types/market';
import type { NewsArticle } from './types/news';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function DashboardContent() {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedMarket, setSelectedMarket] = useState<Market | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [marketFilters, setMarketFilters] = useState<MarketFilters>({
    platforms: [],
    categories: [],
    priceRange: { min: 0, max: 100 },
    sortBy: 'trending',
  });

  // Fetch markets using React Query
  const { data, isLoading, refetch, updateMarket } = useMarkets(categoryFilter || null);

  // WebSocket connection for real-time updates
  const { connected: wsConnected } = useWebSocket((market) => {
    updateMarket(market);
  });

  // Favorites management
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // Toast notifications
  const { toasts, removeToast, showBreaking } = useToast();

  // Breaking news handler
  const handleBreakingNews = (article: NewsArticle) => {
    showBreaking(
      article.title,
      article.summary || 'Breaking news update',
      () => {
        // Scroll to news feed section when toast is clicked
        const newsFeedElement = document.getElementById('news-feed');
        if (newsFeedElement) {
          newsFeedElement.scrollIntoView({ behavior: 'smooth' });
        }
      }
    );
  };

  // Extract markets and categories
  const markets = data?.markets || [];
  const apiStatus = data?.error ? 'error' : 'operational';

  // Get unique categories
  const categories = useMemo(() => {
    return Array.from(new Set(markets.map((m) => m.category).filter(Boolean)));
  }, [markets]);

  // Filter markets based on search term and sidebar filters
  const filteredMarkets = useMemo(() => {
    let filtered = markets;

    // Apply search term filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (market) =>
          market.question?.toLowerCase().includes(term) ||
          market.title?.toLowerCase().includes(term) ||
          market.category?.toLowerCase().includes(term) ||
          market.platform?.toLowerCase().includes(term)
      );
    }

    // Apply platform filter
    if (marketFilters.platforms.length > 0) {
      filtered = filtered.filter((market) =>
        marketFilters.platforms.includes(market.platform?.toLowerCase() || '')
      );
    }

    // Apply category filter
    if (marketFilters.categories.length > 0) {
      filtered = filtered.filter((market) =>
        marketFilters.categories.includes(market.category?.toLowerCase() || '')
      );
    }

    // Apply sorting
    const sorted = [...filtered];
    switch (marketFilters.sortBy) {
      case 'volume':
        sorted.sort((a, b) => (b.volume || 0) - (a.volume || 0));
        break;
      case 'activity':
        sorted.sort((a, b) => (b.liquidity || 0) - (a.liquidity || 0));
        break;
      case 'newest':
        sorted.sort((a, b) =>
          new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
        );
        break;
      case 'trending':
      default:
        // Keep default order (already sorted by backend)
        break;
    }

    return sorted;
  }, [markets, searchTerm, marketFilters]);

  // Calculate market statistics
  const stats = useMemo(() => calculateMarketStats(markets), [markets]);

  // Handle market selection for modal
  const handleMarketSelect = (market: Market) => {
    setSelectedMarket(market);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    // Don't clear selectedMarket immediately to allow exit animation
    setTimeout(() => setSelectedMarket(null), 300);
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white overflow-x-hidden m-0 p-0">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Ambient Glow - Top Left */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary-500/10 rounded-full blur-[120px] opacity-60" />

        {/* Ambient Glow - Bottom Right */}
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] opacity-40" />

        {/* Grid Pattern Overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '64px 64px',
          }}
        />
      </div>

      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onFilterChange={setMarketFilters}
        currentFilters={marketFilters}
      />

      {/* Main Content */}
      <div className="relative z-10">
        <div className="w-full px-4 sm:px-6 lg:px-8 pt-2 pb-8">
          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="lg:hidden fixed bottom-6 right-6 p-4 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg z-30 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </button>

          <Header />

          <StatusBar
            wsConnected={wsConnected}
            apiStatus={apiStatus}
            marketsCount={markets.length}
            onRefresh={() => refetch()}
            isRefreshing={isLoading}
          />

          {/* Market Statistics Dashboard */}
          {!isLoading && markets.length > 0 && (
            <MarketStats
              totalMarkets={stats.totalMarkets}
              volume24h={stats.volume24h}
              averagePrice={stats.averagePrice}
              activeTraders={stats.activeTraders}
            />
          )}

          {/* News & AI Analysis Feed */}
          <div id="news-feed" className="my-8">
            <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Market News & AI Analysis
            </h2>
            <ErrorBoundary>
              <NewsFeed limit={10} onBreakingNews={handleBreakingNews} />
            </ErrorBoundary>
          </div>

          <SearchBar
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            category={categoryFilter}
            onCategoryChange={setCategoryFilter}
            categories={categories}
          />

          <MarketGrid
            markets={filteredMarkets}
            selectedMarketId={selectedMarket?.id}
            onMarketSelect={handleMarketSelect}
            isLoading={isLoading}
            favoriteMarkets={favorites}
            onToggleFavorite={toggleFavorite}
          />

          {/* Results Counter */}
          {!isLoading && markets.length > 0 && (
            <div className="mt-8 text-center">
              <p className="text-sm text-zinc-600 font-mono">
                Showing {filteredMarkets.length} of {markets.length} markets
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Market Detail Modal */}
      <MarketDetailModal
        market={selectedMarket}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />

      {/* Toast Notifications */}
      <ToastContainer>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={removeToast}
          />
        ))}
      </ToastContainer>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardContent />
    </QueryClientProvider>
  );
}
