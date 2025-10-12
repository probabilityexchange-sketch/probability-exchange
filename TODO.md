# TODO List

## High Priority 🔥

### Fix Centering Issue
- [ ] Resolve syntax errors in centered version
- [ ] Test Rich Align.center() with simple examples first
- [ ] Alternative: Use OBS Transform to center browser source
- [ ] Document final centering approach

### Improve Connection Stability
- [ ] Set up autossh or systemd service for persistent SSH tunnel
- [ ] Add tunnel health check script
- [ ] Configure automatic reconnection on failure
- [ ] Consider VPN or other persistent connection methods

### News Ticker
- [ ] Get CryptoPanic API auth token
- [ ] Test news ticker with proper authentication
- [ ] Alternative: Find different crypto news API (CoinGecko, CoinMarketCap)
- [ ] Add fallback if news API fails

## Medium Priority 📊

### Dashboard Enhancements

#### Visual Polish
- [ ] Add smooth transitions between screens
- [ ] Implement fade effects for page changes
- [ ] Add loading indicators during API fetches
- [ ] Better error state displays (when APIs fail)
- [ ] Color-code more elements (green/red for up/down)

#### Data Quality
- [ ] Add minimum liquidity filter (e.g., >$10k) to avoid dead tokens
- [ ] Implement token blocklist for scams/rugs
- [ ] Add volume/liquidity ratio warnings
- [ ] Show token age (new vs. established)
- [ ] Add holder count if available

#### New Features
- [ ] Trending momentum indicator (velocity of price change)
- [ ] Social sentiment integration (Twitter/Discord mentions)
- [ ] Wallet tracking for "smart money" wallets
- [ ] Top holder concentration metrics
- [ ] Contract verification status

### Performance Optimization
- [ ] Profile API call patterns, reduce redundant calls
- [ ] Implement smarter caching strategy
- [ ] Batch API requests where possible
- [ ] Add request timeout handling
- [ ] Log slow operations

### Code Quality
- [ ] Add comprehensive error handling
- [ ] Implement logging framework (replace prints)
- [ ] Add unit tests for key functions
- [ ] Refactor global state into class structure
- [ ] Type hints for all functions
- [ ] Document all API interactions

## Low Priority 🔧

### Infrastructure
- [ ] Set up monitoring/alerting (Prometheus + Grafana?)
- [ ] Add health check endpoint
- [ ] Implement graceful shutdown handling
- [ ] Add restart script with health verification
- [ ] Docker containerization for easier deployment

### Dashboard Features
- [ ] Multi-chain support (Base, Ethereum memecoins)
- [ ] Historical price charts (mini sparklines)
- [ ] Comparison mode (token A vs token B)
- [ ] Whale alert integration
- [ ] DEX screener links/QR codes for tokens

### Streaming Enhancements
- [ ] OBS scene switcher (multiple layouts)
- [ ] Overlay graphics (borders, alerts)
- [ ] Chat integration from Pump.fun
- [ ] Donation/tip alerts
- [ ] Viewer count display

### Analytics
- [ ] Track prediction accuracy (Grok vs. reality)
- [ ] Log all displayed tokens for analysis
- [ ] Viewer engagement metrics
- [ ] Token performance tracking

## Nice to Have 💡

### Advanced Features
- [ ] Machine learning price prediction
- [ ] Portfolio tracker integration
- [ ] Paper trading simulation
- [ ] Alert webhooks (Discord/Telegram)
- [ ] API for external consumers
- [ ] Mobile-responsive web version

### Content Generation
- [ ] More ASCII art scrapers
- [ ] AI-generated memes based on market action
- [ ] Dynamic quote generation using Grok
- [ ] Trending hashtag integration
- [ ] Market sentiment analysis display

### Community
- [ ] Open source the dashboard
- [ ] Documentation for setup
- [ ] Video tutorial for streaming setup
- [ ] Community contribution guidelines
- [ ] Plugin system for custom displays

## Completed ✅

### V1 → V2 Migration
- [x] Add live price alerts
- [x] Create leaderboard system
- [x] Add ASCII art rotation
- [x] Implement Grok AI predictions
- [x] Add news ticker (structure - needs API key)
- [x] Gem of the Hour feature
- [x] 100x Potential Meter

### V2 → V3 Migration
- [x] Expand token search from 12 to 50+ terms
- [x] Increase search sampling to 8 terms per cycle
- [x] Add volume leaderboard
- [x] Add liquidity leaderboard
- [x] Add market cap category boards (low/mid)
- [x] Track liquidity for all tokens
- [x] Fix market cap display with K notation
- [x] Enhanced main leaderboard with market caps

### Infrastructure Setup
- [x] Install and configure ttyd
- [x] Set up tmux sessions
- [x] Create SSH tunnel connection script
- [x] Configure OBS for browser source capture
- [x] Test RTMPS streaming to Pump.fun

## Blocked/Waiting ⏸️

- **News Ticker**: Waiting for CryptoPanic API key decision
- **Centering**: Needs debugging session or pivot to OBS solution
- **Pump.fun Direct API**: Waiting for public API release (if ever)

## Questions Needing Answers ❓

See QUESTIONS.md for decision points requiring input.
