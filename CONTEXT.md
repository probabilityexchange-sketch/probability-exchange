# Project Context

## What We're Building
A live-streaming crypto dashboard for Pump.fun (Solana memecoin platform) that displays:
- Real-time crypto prices (BTC, ETH, SOL)
- Trending memecoin tokens with price changes
- Prediction markets (Polymarket, Kalshi)
- AI-powered predictions using Grok
- Live leaderboards (gainers/losers, volume, liquidity, market cap categories)
- Price alerts with flash animations
- ASCII art and degen wisdom quotes

## Current Architecture

### Infrastructure
- **Server**: Linux Ubuntu at 5.161.184.246
- **Terminal Multiplexer**: tmux sessions
  - `pumpfun_stream` (port 7681) - Original dashboard
  - `pumpfun_v3` (port 7682) - V3 Enhanced dashboard
- **Web Terminal**: ttyd serving terminal via browser
- **Local Access**: SSH tunnels from local desktop to server
- **Streaming**: OBS Studio captures ttyd web terminal, streams to Pump.fun via RTMPS

### Dashboard Versions
- **V1**: Basic crypto prices and trending tokens
- **V2**: Added price alerts, leaderboard, ASCII art, news ticker
- **V3** (Current): Enhanced with:
  - 50+ token search terms (was 12)
  - 8 random terms per fetch cycle (was 3)
  - Volume leaderboard
  - Liquidity leaderboard  
  - Market cap categories (<$1M, $1M-$10M, >$10M)
  - Liquidity tracking for all tokens
  - K notation for market caps under $1M

### File Locations
- Dashboard scripts: `/opt/prediction-engine/`
  - `degen_dashboard_ai.py` (V1)
  - `degen_dashboard_v2_complete.py` (V2)
  - `degen_dashboard_v3.py` (V3 - current)
- ASCII art: `/opt/prediction-engine/scraped_ascii_art.json`
- Local connection script: `~/connect_dashboards.sh`

### Data Sources
- **DexScreener API**: Token prices, volumes, liquidity, market caps
- **CoinGecko API**: BTC/ETH/SOL prices
- **Polymarket API**: Prediction markets
- **Kalshi API**: Prediction markets (via local API at localhost:8002)
- **OpenRouter/Grok API**: AI predictions
- **CryptoPanic API**: News ticker (currently broken - needs auth token)

## Tech Stack
- **Language**: Python 3
- **Terminal UI**: Rich library (tables, markdown, panels, colors)
- **Web Terminal**: ttyd
- **Streaming**: OBS Studio (Linux desktop with wired connection)
- **APIs**: requests library for all HTTP calls
- **Async**: asyncio for main display loop

## Current State

### What Works ✅
- V3 dashboard running in tmux
- SSH tunnels connecting local machine to server
- Browser access at http://localhost:7682
- All leaderboards displaying (gainers/losers, volume, liquidity, mcap categories)
- Market cap formatting with K/M/B notation
- Price alerts for >3% movements
- Rotating display of tokens, predictions, ASCII art
- Gem of the Hour feature
- 100x Potential Meter
- Token data from 50+ search terms
- Liquidity data tracking

### Known Issues ⚠️
1. **Centering**: Terminal content not centered (ASCII art, tables)
   - Attempted Rich Align.center() but caused syntax errors
   - Best solution may be centering in OBS layout instead
2. **News Ticker**: CryptoPanic API requires auth token (not set up)
3. **SSH Tunnel Stability**: Tunnels disconnect periodically, need manual restart

### Recent Changes
- Added K notation for market caps <$1M (e.g., $500.5K)
- Expanded SEARCH_TERMS from 12 to 50+ tokens
- Increased search sampling from 3 to 8 terms per cycle
- Added liquidity tracking to all tokens
- Created 4 new leaderboard types (volume, liquidity, low mcap, mid mcap)
- Enhanced main leaderboard to show market cap next to each token

## Environment Variables
- `OPENROUTER_API_KEY`: For Grok AI predictions (set in server environment)

## Access & Streaming

### Local Access
```bash
# Connect SSH tunnels
~/connect_dashboards.sh

# Manual tunnel
ssh -f -N -L 7681:localhost:7681 -L 7682:localhost:7682 \
    -o ServerAliveInterval=60 -o ServerAliveCountMax=3 \
    root@5.161.184.246

# Access dashboards
http://localhost:7681  # V1
http://localhost:7682  # V3
```

### Server Access
```bash
# SSH to server
ssh root@5.161.184.246

# View tmux sessions
tmux ls

# Attach to V3 dashboard
tmux attach -t pumpfun_v3

# Restart dashboard
tmux send-keys -t pumpfun_v3 C-c
tmux send-keys -t pumpfun_v3 "python3 /opt/prediction-engine/degen_dashboard_v3.py" Enter
```

### OBS Streaming Setup
1. Add Browser Source in OBS
2. URL: http://localhost:7682
3. Width: 1920, Height: 1080
4. Custom CSS: (optional for styling)
5. Stream Settings: Custom RTMPS server
   - URL: rtmps://[pump.fun streaming URL]
   - Stream Key: [from Pump.fun]
6. Output Settings:
   - Bitrate: 1500-2500 Kbps
   - Resolution: 1280x720 or 1920x1080
   - Wired ethernet connection recommended

## Performance Notes
- Dashboard updates prices every 30-60 seconds
- Token pool refreshes every 60 seconds
- Leaderboard recalculates every 2 minutes
- Display rotation cycles every 4-6 seconds per page
- WiFi streaming was unstable; wired connection much better

## Future Considerations
- Add proper CryptoPanic API key for news ticker
- Implement direct Pump.fun trending API fetch
- Add more visual polish (centering, animations)
- Consider volume-weighted metrics
- Add token filtering by minimum liquidity
- Implement persistent SSH tunnel service
- Add health monitoring/auto-restart
