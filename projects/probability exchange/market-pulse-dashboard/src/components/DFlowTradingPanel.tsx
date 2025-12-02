/**
 * DFlow Trading Panel - Solana Prediction Markets
 * Integrated with dashboard design system and Solana wallets
 */

import { useState, useEffect, useMemo } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, DollarSign, BarChart3, Wallet, ChevronDown } from 'lucide-react';
import { dflowClient, type DFlowMarket, type Position } from '../lib/dflow-api-client';
import bs58 from 'bs58';

export function DFlowTradingPanel() {
  const { publicKey, signMessage, connected } = useWallet();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [markets, setMarkets] = useState<DFlowMarket[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<DFlowMarket | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'markets' | 'trade' | 'portfolio'>('markets');

  // Authenticate wallet when connected
  useEffect(() => {
    if (connected && publicKey && !sessionId) {
      authenticateWallet();
    }
  }, [connected, publicKey]);

  // Load markets on mount
  useEffect(() => {
    loadMarkets();
  }, []);

  // Load positions when session is established
  useEffect(() => {
    if (sessionId && publicKey) {
      loadPositions();
    }
  }, [sessionId, publicKey]);

  const authenticateWallet = async () => {
    if (!publicKey || !signMessage) return;

    try {
      setLoading(true);
      setError(null);

      // Get challenge
      const challengeData = await dflowClient.createAuthChallenge(publicKey.toString());

      // Sign challenge
      const message = new TextEncoder().encode(challengeData.challenge);
      const signature = await signMessage(message);
      const signatureBase58 = bs58.encode(signature);

      // Verify signature
      const authResult = await dflowClient.verifySignature(
        publicKey.toString(),
        challengeData.challenge,
        signatureBase58
      );

      if (authResult.success) {
        setSessionId(authResult.session_id);
        console.log('✓ Wallet authenticated');
      }
    } catch (err) {
      console.error('Authentication failed:', err);
      setError('Failed to authenticate wallet. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadMarkets = async () => {
    try {
      setLoading(true);
      const data = await dflowClient.getMarkets();
      setMarkets(data.markets);
    } catch (err) {
      console.error('Failed to load markets:', err);
      setError('Failed to load markets');
    } finally {
      setLoading(false);
    }
  };

  const loadPositions = async () => {
    if (!publicKey || !sessionId) return;

    try {
      const data = await dflowClient.getUserPositions(publicKey.toString(), sessionId);
      setPositions(data.positions);
    } catch (err) {
      console.error('Failed to load positions:', err);
    }
  };

  // Filter markets
  const filteredMarkets = useMemo(() => {
    return markets.filter((market) => {
      const matchesSearch = market.question.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || market.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [markets, searchTerm, categoryFilter]);

  // Get unique categories
  const categories = useMemo(() => {
    return Array.from(new Set(markets.map((m) => m.category).filter(Boolean)));
  }, [markets]);

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-surface border-b border-dark-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                DFlow Solana Markets
              </h1>
              <p className="text-zinc-400 mt-1">Trade tokenized Kalshi markets on Solana</p>
            </div>
            <WalletMultiButton className="!bg-gradient-primary hover:opacity-90 transition-opacity" />
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 m-4">
          <p className="text-red-400">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-300 mt-2 text-sm underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {connected && sessionId ? (
          <>
            {/* Tab Navigation */}
            <div className="flex space-x-1 bg-dark-surface rounded-lg p-1 mb-6">
              {['markets', 'trade', 'portfolio'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all ${
                    activeTab === tab
                      ? 'bg-gradient-primary text-white shadow-glow-sm'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <AnimatePresence mode="wait">
              {activeTab === 'markets' && (
                <MarketsView
                  markets={filteredMarkets}
                  searchTerm={searchTerm}
                  onSearchChange={setSearchTerm}
                  categoryFilter={categoryFilter}
                  onCategoryChange={setCategoryFilter}
                  categories={categories}
                  onSelectMarket={(market) => {
                    setSelectedMarket(market);
                    setActiveTab('trade');
                  }}
                  loading={loading}
                />
              )}

              {activeTab === 'trade' && (
                <TradeView
                  market={selectedMarket}
                  walletAddress={publicKey?.toString() || ''}
                  sessionId={sessionId || ''}
                  onTradeComplete={() => {
                    loadPositions();
                    setActiveTab('portfolio');
                  }}
                />
              )}

              {activeTab === 'portfolio' && (
                <PortfolioView
                  positions={positions}
                  walletAddress={publicKey?.toString() || ''}
                  onRefresh={loadPositions}
                />
              )}
            </AnimatePresence>
          </>
        ) : (
          <ConnectPrompt />
        )}
      </div>
    </div>
  );
}

// Markets View Component
function MarketsView({
  markets,
  searchTerm,
  onSearchChange,
  categoryFilter,
  onCategoryChange,
  categories,
  onSelectMarket,
  loading,
}: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search markets..."
            className="w-full bg-dark-surface border border-dark-border rounded-lg pl-10 pr-4 py-3 text-white placeholder-zinc-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
          />
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="bg-dark-surface border border-dark-border rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
        >
          <option value="all">All Categories</option>
          {categories.map((cat: string) => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Markets Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-zinc-400 mt-4">Loading markets...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {markets.map((market: DFlowMarket) => (
            <MarketCard key={market.id} market={market} onSelect={() => onSelectMarket(market)} />
          ))}
        </div>
      )}

      {!loading && markets.length === 0 && (
        <div className="text-center py-12">
          <p className="text-zinc-400">No markets found</p>
        </div>
      )}
    </motion.div>
  );
}

// Market Card Component
function MarketCard({ market, onSelect }: { market: DFlowMarket; onSelect: () => void }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={onSelect}
      className="bg-dark-surface border border-dark-border rounded-lg p-6 cursor-pointer hover:border-blue-500/50 transition-all"
    >
      <h3 className="text-lg font-semibold mb-4 line-clamp-2">{market.question}</h3>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
          <p className="text-xs text-green-400 mb-1">YES</p>
          <p className="text-xl font-bold text-green-400">{(market.yes_price * 100).toFixed(1)}¢</p>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <p className="text-xs text-red-400 mb-1">NO</p>
          <p className="text-xl font-bold text-red-400">{(market.no_price * 100).toFixed(1)}¢</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-zinc-400">
        <div className="flex items-center gap-1">
          <BarChart3 className="w-4 h-4" />
          <span>${(market.volume_24h / 1000).toFixed(1)}K</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs">Solana</span>
          {market.category && (
            <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded text-xs">
              {market.category}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// Trade View Component
function TradeView({ market, walletAddress, sessionId, onTradeComplete }: any) {
  const [amount, setAmount] = useState('');
  const [outcome, setOutcome] = useState<'yes' | 'no'>('yes');
  const [loading, setLoading] = useState(false);

  if (!market) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-400">Select a market to trade</p>
      </div>
    );
  }

  const handleTrade = async () => {
    // Trade logic here - simplified for brevity
    alert('Trade functionality - integrate with dflowClient.executeSwap()');
    onTradeComplete();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-2xl mx-auto space-y-6"
    >
      <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">{market.question}</h2>

        {/* Outcome Selection */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => setOutcome('yes')}
            className={`p-6 rounded-lg border-2 transition-all ${
              outcome === 'yes'
                ? 'border-green-500 bg-green-500/10'
                : 'border-dark-border hover:border-green-500/50'
            }`}
          >
            <p className="text-sm text-zinc-400 mb-2">YES</p>
            <p className="text-3xl font-bold text-green-400">{(market.yes_price * 100).toFixed(1)}¢</p>
          </button>
          <button
            onClick={() => setOutcome('no')}
            className={`p-6 rounded-lg border-2 transition-all ${
              outcome === 'no'
                ? 'border-red-500 bg-red-500/10'
                : 'border-dark-border hover:border-red-500/50'
            }`}
          >
            <p className="text-sm text-zinc-400 mb-2">NO</p>
            <p className="text-3xl font-bold text-red-400">{(market.no_price * 100).toFixed(1)}¢</p>
          </button>
        </div>

        {/* Amount Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-zinc-400 mb-2">Amount (USDC)</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white text-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
          />
        </div>

        {/* Trade Button */}
        <button
          onClick={handleTrade}
          disabled={!amount || loading}
          className="w-full bg-gradient-primary text-white font-bold py-4 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? 'Processing...' : `Buy ${outcome.toUpperCase()}`}
        </button>
      </div>
    </motion.div>
  );
}

// Portfolio View Component
function PortfolioView({ positions, walletAddress, onRefresh }: any) {
  const totalValue = positions.reduce((sum: number, pos: Position) => sum + parseFloat(pos.current_value), 0);
  const totalPnL = positions.reduce((sum: number, pos: Position) => sum + parseFloat(pos.pnl), 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-sm text-zinc-400 mb-2">Total Value</p>
          <p className="text-3xl font-bold">${totalValue.toFixed(2)}</p>
        </div>
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-sm text-zinc-400 mb-2">Total P&L</p>
          <p className={`text-3xl font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
          </p>
        </div>
        <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
          <p className="text-sm text-zinc-400 mb-2">Positions</p>
          <p className="text-3xl font-bold">{positions.length}</p>
        </div>
      </div>

      {/* Positions List */}
      <div className="bg-dark-surface border border-dark-border rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-dark-border flex items-center justify-between">
          <h3 className="text-lg font-semibold">Your Positions</h3>
          <button onClick={onRefresh} className="text-blue-400 hover:text-blue-300 text-sm">
            Refresh
          </button>
        </div>

        {positions.length === 0 ? (
          <div className="p-12 text-center">
            <Wallet className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
            <p className="text-zinc-400">No positions yet</p>
            <p className="text-sm text-zinc-500 mt-2">Start trading to see your portfolio here</p>
          </div>
        ) : (
          <div className="divide-y divide-dark-border">
            {positions.map((position: Position, idx: number) => (
              <div key={idx} className="px-6 py-4 hover:bg-dark-hover transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium">{position.market_id}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          position.outcome === 'YES'
                            ? 'bg-green-500/10 text-green-400'
                            : 'bg-red-500/10 text-red-400'
                        }`}
                      >
                        {position.outcome}
                      </span>
                      <span className="text-sm text-zinc-400">{parseFloat(position.shares).toFixed(2)} shares</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">${parseFloat(position.current_value).toFixed(2)}</p>
                    <p
                      className={`text-sm ${
                        parseFloat(position.pnl) >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {parseFloat(position.pnl) >= 0 ? '+' : ''}
                      {parseFloat(position.pnl).toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Connect Prompt Component
function ConnectPrompt() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-lg mx-auto text-center py-16"
    >
      <div className="bg-dark-surface border border-dark-border rounded-lg p-12">
        <Wallet className="w-16 h-16 text-blue-400 mx-auto mb-6" />
        <h2 className="text-2xl font-bold mb-3">Connect Your Solana Wallet</h2>
        <p className="text-zinc-400 mb-8">
          Connect Phantom or Solflare to trade tokenized prediction markets on Solana
        </p>
        <WalletMultiButton className="!bg-gradient-primary hover:opacity-90 transition-opacity !mx-auto" />
      </div>
    </motion.div>
  );
}
