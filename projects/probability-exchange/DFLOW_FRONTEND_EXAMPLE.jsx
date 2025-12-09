/**
 * DFlow Solana Trading Frontend Integration
 *
 * React component example for integrating DFlow prediction market trading
 * with Phantom/Solflare wallet connection.
 *
 * Features:
 * - Solana wallet connection (Phantom, Solflare)
 * - Market discovery and browsing
 * - Trading interface with swap quotes
 * - Portfolio tracking
 * - Transaction management
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// Solana wallet adapter imports (install with: npm install @solana/wallet-adapter-react @solana/wallet-adapter-react-ui)
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import bs58 from 'bs58';

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api/v1/dflow';

/**
 * Main DFlow Trading Component
 */
export const DFlowTradingDashboard = () => {
  const { publicKey, signMessage, connected } = useWallet();
  const { connection } = useConnection();

  // State
  const [sessionId, setSessionId] = useState(null);
  const [markets, setMarkets] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState(null);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Authentication
  useEffect(() => {
    if (connected && publicKey && !sessionId) {
      authenticateWallet();
    }
  }, [connected, publicKey]);

  /**
   * Authenticate Solana wallet with backend
   */
  const authenticateWallet = async () => {
    try {
      setLoading(true);
      setError(null);

      // Step 1: Request challenge from backend
      const challengeResponse = await axios.post(`${API_BASE_URL}/auth/solana/challenge`, {
        wallet_address: publicKey.toString()
      });

      const { challenge, nonce } = challengeResponse.data;

      // Step 2: Sign challenge with wallet
      const message = new TextEncoder().encode(challenge);
      const signature = await signMessage(message);
      const signatureBase58 = bs58.encode(signature);

      // Step 3: Verify signature with backend
      const verifyResponse = await axios.post(`${API_BASE_URL}/auth/solana/verify`, {
        wallet_address: publicKey.toString(),
        challenge: challenge,
        signature: signatureBase58
      });

      if (verifyResponse.data.success) {
        setSessionId(verifyResponse.data.session_id);
        console.log('✓ Wallet authenticated successfully');

        // Load initial data
        await Promise.all([
          loadMarkets(),
          loadPositions()
        ]);
      }

    } catch (err) {
      console.error('Authentication failed:', err);
      setError('Failed to authenticate wallet. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load available prediction markets
   */
  const loadMarkets = async (category = null, limit = 50) => {
    try {
      const params = { limit };
      if (category) params.category = category;

      const response = await axios.get(`${API_BASE_URL}/markets`, { params });
      setMarkets(response.data.markets);
      console.log(`Loaded ${response.data.markets.length} markets`);
    } catch (err) {
      console.error('Failed to load markets:', err);
      setError('Failed to load markets');
    }
  };

  /**
   * Load user's positions
   */
  const loadPositions = async () => {
    if (!publicKey || !sessionId) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/portfolio/positions/${publicKey.toString()}`,
        { params: { session_id: sessionId } }
      );
      setPositions(response.data.positions);
    } catch (err) {
      console.error('Failed to load positions:', err);
    }
  };

  return (
    <div className="dflow-dashboard">
      <Header />

      {/* Wallet Connection */}
      <div className="wallet-section">
        <WalletMultiButton />
        {connected && sessionId && (
          <span className="auth-status">✓ Authenticated</span>
        )}
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {connected && sessionId ? (
        <>
          {/* Markets Section */}
          <MarketsSection
            markets={markets}
            onSelectMarket={setSelectedMarket}
            onRefresh={loadMarkets}
            loading={loading}
          />

          {/* Trading Section */}
          {selectedMarket && (
            <TradingSection
              market={selectedMarket}
              walletAddress={publicKey.toString()}
              sessionId={sessionId}
              onTradeComplete={() => {
                loadPositions();
                loadMarkets();
              }}
            />
          )}

          {/* Portfolio Section */}
          <PortfolioSection
            positions={positions}
            walletAddress={publicKey.toString()}
            sessionId={sessionId}
            onRefresh={loadPositions}
          />
        </>
      ) : (
        <div className="connect-prompt">
          <h2>Connect Your Solana Wallet</h2>
          <p>Connect Phantom or Solflare to trade prediction markets on Solana</p>
        </div>
      )}
    </div>
  );
};

/**
 * Markets browsing component
 */
const MarketsSection = ({ markets, onSelectMarket, onRefresh, loading }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const filteredMarkets = markets.filter(market => {
    const matchesSearch = market.question.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || market.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...new Set(markets.map(m => m.category).filter(Boolean))];

  return (
    <div className="markets-section">
      <div className="section-header">
        <h2>Available Markets</h2>
        <button onClick={onRefresh} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search markets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="category-filter"
        >
          {categories.map(cat => (
            <key={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Market List */}
      <div className="markets-grid">
        {filteredMarkets.map(market => (
          <MarketCard
            key={market.id}
            market={market}
            onSelect={() => onSelectMarket(market)}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * Individual market card
 */
const MarketCard = ({ market, onSelect }) => {
  return (
    <div className="market-card" onClick={onSelect}>
      <div className="market-question">{market.question}</div>

      <div className="market-prices">
        <div className="price-item yes">
          <span className="label">YES</span>
          <span className="price">${(market.yes_price * 100).toFixed(1)}¢</span>
        </div>
        <div className="price-item no">
          <span className="label">NO</span>
          <span className="price">${(market.no_price * 100).toFixed(1)}¢</span>
        </div>
      </div>

      <div className="market-stats">
        <div className="stat">
          <span className="label">24h Volume</span>
          <span className="value">${(market.volume_24h / 1000).toFixed(1)}K</span>
        </div>
        <div className="stat">
          <span className="label">Liquidity</span>
          <span className="value">${(market.liquidity / 1000).toFixed(1)}K</span>
        </div>
      </div>

      <div className="market-badge">
        <span className="chain">Solana</span>
        <span className="category">{market.category}</span>
      </div>
    </div>
  );
};

/**
 * Trading interface component
 */
const TradingSection = ({ market, walletAddress, sessionId, onTradeComplete }) => {
  const [tradeType, setTradeType] = useState('buy'); // buy or sell
  const [outcome, setOutcome] = useState('yes'); // yes or no
  const [amount, setAmount] = useState('');
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [swapMode, setSwapMode] = useState('declarative'); // imperative or declarative

  const USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';

  /**
   * Get swap quote
   */
  const getQuote = async () => {
    if (!amount || parseFloat(amount) <= 0) return;

    try {
      setLoading(true);

      const inputToken = USDC_MINT;
      const outputToken = outcome === 'yes' ? market.yes_token_mint : market.no_token_mint;
      const amountInSmallestUnit = (parseFloat(amount) * 1_000_000).toString(); // USDC has 6 decimals

      const response = await axios.post(`${API_BASE_URL}/trading/quote`, {
        input_token: inputToken,
        output_token: outputToken,
        amount: amountInSmallestUnit,
        slippage_tolerance: 0.01
      });

      setQuote(response.data.quote);
    } catch (err) {
      console.error('Failed to get quote:', err);
      alert('Failed to get quote. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Execute swap
   */
  const executeSwap = async () => {
    if (!quote) return;

    try {
      setLoading(true);

      const response = await axios.post(`${API_BASE_URL}/trading/swap`, {
        input_token: quote.in_token,
        output_token: quote.out_token,
        amount: quote.in_amount,
        wallet_address: walletAddress,
        session_id: sessionId,
        mode: swapMode,
        slippage_tolerance: 0.01
      });

      if (response.data.success) {
        alert('Trade executed successfully!');
        setAmount('');
        setQuote(null);
        onTradeComplete();
      }
    } catch (err) {
      console.error('Failed to execute swap:', err);
      alert('Trade failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Get quote when amount changes (with debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (amount) getQuote();
    }, 500);
    return () => clearTimeout(timer);
  }, [amount, outcome]);

  return (
    <div className="trading-section">
      <div className="section-header">
        <h2>Trade: {market.question}</h2>
        <button onClick={() => setQuote(null)}>Close</button>
      </div>

      <div className="trade-form">
        {/* Outcome Selection */}
        <div className="outcome-selector">
          <button
            className={`outcome-btn yes ${outcome === 'yes' ? 'active' : ''}`}
            onClick={() => setOutcome('yes')}
          >
            YES ${(market.yes_price * 100).toFixed(1)}¢
          </button>
          <button
            className={`outcome-btn no ${outcome === 'no' ? 'active' : ''}`}
            onClick={() => setOutcome('no')}
          >
            NO ${(market.no_price * 100).toFixed(1)}¢
          </button>
        </div>

        {/* Amount Input */}
        <div className="amount-input">
          <label>Amount (USDC)</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            min="0"
            step="0.01"
          />
        </div>

        {/* Swap Mode */}
        <div className="swap-mode">
          <label>
            <input
              type="radio"
              value="declarative"
              checked={swapMode === 'declarative'}
              onChange={(e) => setSwapMode(e.target.value)}
            />
            Declarative (Recommended)
          </label>
          <label>
            <input
              type="radio"
              value="imperative"
              checked={swapMode === 'imperative'}
              onChange={(e) => setSwapMode(e.target.value)}
            />
            Imperative (Advanced)
          </label>
        </div>

        {/* Quote Display */}
        {quote && (
          <div className="quote-display">
            <h3>Quote</h3>
            <div className="quote-row">
              <span>You pay:</span>
              <span>{(parseInt(quote.in_amount) / 1_000_000).toFixed(2)} USDC</span>
            </div>
            <div className="quote-row">
              <span>You receive:</span>
              <span>{(parseInt(quote.out_amount) / 1_000_000).toFixed(2)} {outcome.toUpperCase()} tokens</span>
            </div>
            <div className="quote-row">
              <span>Price impact:</span>
              <span className={quote.price_impact > 0.05 ? 'warning' : ''}>
                {(quote.price_impact * 100).toFixed(2)}%
              </span>
            </div>
            <div className="quote-row">
              <span>Slippage:</span>
              <span>{(quote.estimated_slippage * 100).toFixed(2)}%</span>
            </div>
          </div>
        )}

        {/* Execute Button */}
        <button
          className="execute-btn"
          onClick={executeSwap}
          disabled={!quote || loading}
        >
          {loading ? 'Processing...' : `Buy ${outcome.toUpperCase()}`}
        </button>
      </div>
    </div>
  );
};

/**
 * Portfolio positions component
 */
const PortfolioSection = ({ positions, walletAddress, sessionId, onRefresh }) => {
  const totalValue = positions.reduce((sum, pos) => sum + parseFloat(pos.current_value), 0);
  const totalPnL = positions.reduce((sum, pos) => sum + parseFloat(pos.pnl), 0);

  return (
    <div className="portfolio-section">
      <div className="section-header">
        <h2>Your Positions</h2>
        <button onClick={onRefresh}>Refresh</button>
      </div>

      <div className="portfolio-summary">
        <div className="summary-item">
          <span className="label">Total Value</span>
          <span className="value">${totalValue.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Total P&L</span>
          <span className={`value ${totalPnL >= 0 ? 'positive' : 'negative'}`}>
            {totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(2)}
          </span>
        </div>
        <div className="summary-item">
          <span className="label">Positions</span>
          <span className="value">{positions.length}</span>
        </div>
      </div>

      <div className="positions-table">
        <table>
          <thead>
            <tr>
              <th>Market</th>
              <th>Outcome</th>
              <th>Shares</th>
              <th>Avg Price</th>
              <th>Value</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position, idx) => (
              <tr key={idx}>
                <td>{position.market_id}</td>
                <td>
                  <span className={`outcome-badge ${position.outcome.toLowerCase()}`}>
                    {position.outcome}
                  </span>
                </td>
                <td>{parseFloat(position.shares).toFixed(2)}</td>
                <td>${parseFloat(position.average_price).toFixed(2)}</td>
                <td>${parseFloat(position.current_value).toFixed(2)}</td>
                <td className={parseFloat(position.pnl) >= 0 ? 'positive' : 'negative'}>
                  {parseFloat(position.pnl) >= 0 ? '+' : ''}
                  {parseFloat(position.pnl).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {positions.length === 0 && (
          <div className="empty-state">
            <p>No positions yet. Start trading to see your portfolio here.</p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Header component
 */
const Header = () => (
  <div className="header">
    <h1>DFlow Prediction Markets</h1>
    <p>Trade tokenized Kalshi markets on Solana</p>
  </div>
);

/**
 * Error banner component
 */
const ErrorBanner = ({ message, onDismiss }) => (
  <div className="error-banner">
    <span>{message}</span>
    <button onClick={onDismiss}>×</button>
  </div>
);

export default DFlowTradingDashboard;

/*
 * CSS Styles (add to your stylesheet)
 *
 * .dflow-dashboard { max-width: 1200px; margin: 0 auto; padding: 20px; }
 * .wallet-section { display: flex; align-items: center; gap: 15px; margin-bottom: 30px; }
 * .auth-status { color: #00C853; font-weight: 600; }
 * .markets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
 * .market-card { border: 1px solid #ddd; border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.2s; }
 * .market-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
 * .outcome-btn { flex: 1; padding: 15px; border: 2px solid transparent; border-radius: 8px; cursor: pointer; }
 * .outcome-btn.yes { background: #E8F5E9; color: #2E7D32; }
 * .outcome-btn.yes.active { border-color: #2E7D32; }
 * .outcome-btn.no { background: #FFEBEE; color: #C62828; }
 * .outcome-btn.no.active { border-color: #C62828; }
 * .positive { color: #00C853; }
 * .negative { color: #D32F2F; }
 */
