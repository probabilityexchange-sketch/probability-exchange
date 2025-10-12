# Key Decisions

## Architecture Decisions

### ✅ Use ttyd for Web Terminal (Early)
**Decision**: Stream terminal via ttyd web interface instead of direct terminal capture  
**Reasoning**: 
- Perfect rendering of colors, emojis, box-drawing characters
- Works across different systems (local/remote)
- Easy to capture in OBS as browser source
- No terminal emulator compatibility issues

**Alternatives Considered**:
- Direct terminal capture (flaky rendering)
- ImageMagick text rendering (limited emoji/color support)

---

### ✅ Use DexScreener API Instead of Direct Pump.fun API (Mid)
**Decision**: Fetch token data from DexScreener API search  
**Reasoning**:
- Pump.fun has no public API or streaming support
- DexScreener aggregates Solana DEX data including Pump.fun tokens
- Provides comprehensive data: price, volume, liquidity, market cap
- Well-documented, reliable, no auth required

**Trade-offs**:
- Not "official" Pump.fun data
- May have slight delays vs. direct source
- Rate limiting concerns (mitigated by caching)

---

### ✅ Client-Side OBS Streaming vs Server-Side (Early)
**Decision**: Stream from local Linux desktop OBS, not server  
**Reasoning**:
- Better control over stream quality
- Can preview before streaming
- Easier to adjust layouts/overlays
- Server resources freed for dashboard

**Requirements**:
- SSH tunnel to access server dashboards
- Wired ethernet connection (WiFi was unstable)
- Keep tunnel alive with ServerAliveInterval

---

### ✅ Multiple Leaderboard Types (V3)
**Decision**: Create 4 distinct leaderboard views  
**Reasoning**:
- Different traders care about different metrics
- Volume leaders show liquidity/activity
- Market cap categories help find gems vs. established coins
- Liquidity shows safety/rugpull resistance
- More engaging content variety

**Implementation**:
- Rotate through boards in main loop
- Keep all data in single leaderboard_data dict
- Update all boards together every 2 minutes

---

### ✅ Expanded Token Search from 12 to 50+ Terms (V3)
**Decision**: Dramatically increase search term pool  
**Reasoning**:
- More diverse token coverage
- Better representation of memecoin ecosystem
- Users want to see variety, not same 12 tokens
- Still random sampling (8 per cycle) to manage API rate limits

**Trade-offs**:
- More API calls per cycle
- Slightly slower initial load
- Benefits far outweigh costs

---

### ✅ K Notation for Small Market Caps (V3)
**Decision**: Display <$1M market caps as "$500.5K" instead of "$0.00M"  
**Reasoning**:
- User specifically requested this
- More precise for low-cap gems
- Follows financial convention
- Easier to read at a glance

**Implementation**:
- Three-tier formatting: K (<$1M), M ($1M-$1B), B (>$1B)
- Consistent across all displays

---

### ⚠️ Centering Approach (Recent - Unresolved)
**Decision**: Attempted to center all content using Rich's Align.center()  
**Status**: Caused syntax errors, currently reverted  
**Reasoning**:
- User wants professional centered layout
- Rich library has Align class for centering
- Should work in theory

**Issues**:
- Multi-line console.print wrapping broke
- Unclosed parentheses from automated replacements
- Complex nesting of Panel/Markdown/Table made it fragile

**Current Recommendation**:
- Handle centering in OBS layout instead
- Or manually center each display function carefully
- Consider using console width calculations + padding

---

### ✅ Liquidity Tracking (V3)
**Decision**: Add liquidity data to all token fetches  
**Reasoning**:
- Critical metric for avoiding rugpulls
- Shows "real" volume vs. inflated numbers
- Enables Volume/Liquidity ratio calculation
- Free data from DexScreener API

---

### ✅ Price Alerts with Flash Animations (V2)
**Decision**: Show full-screen alerts for >3% price moves  
**Reasoning**:
- Creates exciting "breaking news" moments
- Engages stream viewers
- Helps traders catch opportunities
- 3% threshold avoids noise, 3-minute cooldown prevents spam

---

### ✅ Rich Library for Terminal UI (Early)
**Decision**: Use Rich instead of raw terminal codes or curses  
**Reasoning**:
- Modern, well-maintained
- Beautiful tables, panels, markdown rendering
- Handles colors, styles, emojis automatically
- Works great with ttyd
- Much cleaner code than manual ANSI codes

**Alternatives Considered**:
- curses (too low-level)
- blessed (less feature-rich)
- Raw ANSI codes (unmaintainable)

---

## Data Design Decisions

### ✅ Global State Management
**Decision**: Use global variables for shared state  
**Reasoning**:
- Simple async architecture
- Clear data flow
- Easy to understand
- No need for complex state management

**Global State**:
- `all_tokens`: Master list of fetched tokens
- `leaderboard_data`: All leaderboard categories
- `price_history`: For alert detection
- `crypto_prices`: BTC/ETH/SOL prices
- `news_ticker`: Scrolling news items

---

### ✅ 2-Minute Leaderboard Update Interval
**Decision**: Recalculate leaderboards every 2 minutes  
**Reasoning**:
- Balance freshness vs. API load
- Price movements need time to be meaningful
- Reduces flickering/instability
- Matches DexScreener data update frequency

---

### ✅ Token Pool Refresh Strategy
**Decision**: Refresh token pool every 60 seconds, shuffle for randomness  
**Reasoning**:
- Keep data fresh but not excessive
- Shuffling creates variety in display
- 60s matches typical price update intervals
- Separate pool allows display decoupling from fetch

---

## UI/UX Decisions

### ✅ Rotating Display Model
**Decision**: Cycle through different page types vs. split screen  
**Reasoning**:
- Keeps interface clean and focused
- Works well with streaming single-view
- Each element gets full attention
- Easy to add new page types

**Rotation**:
- Logo every 20 cycles
- Leaderboards every 12/25/30/35 cycles
- Gem of Hour every 15 cycles
- ASCII art every 4 cycles
- Regular content (token/quote/market) fills gaps

---

### ✅ ASCII Art from Scraped File
**Decision**: Pre-scrape and store ASCII art vs. fetch live  
**Reasoning**:
- Faster display
- No external dependencies during runtime
- Curated quality
- Offline-capable

---

### ✅ Emoji-Heavy Visual Language
**Decision**: Use lots of emojis throughout  
**Reasoning**:
- Fits crypto/meme culture
- Visual interest for stream viewers
- Quick visual parsing
- Fun and engaging

---

## Operational Decisions

### ✅ tmux for Session Management
**Decision**: Run dashboards in tmux sessions  
**Reasoning**:
- Persist across SSH disconnects
- Easy to attach/detach
- Multiple dashboards simultaneously
- Standard tool for long-running processes

---

### ✅ Separate Dashboard Versions in Parallel
**Decision**: Keep V1, V2, V3 running simultaneously  
**Reasoning**:
- Easy rollback if needed
- Compare features side-by-side
- No downtime during updates
- Different ports for each

---

## Decisions to Revisit

1. **News Ticker API**: Need to set up proper CryptoPanic auth token or find alternative
2. **Centering Implementation**: Either fix Rich Align approach or pivot to OBS-based centering
3. **SSH Tunnel Management**: Consider systemd service or autossh for reliability
4. **Direct Pump.fun API**: If they add public API, should switch from DexScreener
5. **Error Handling**: Currently minimal; should add retry logic and graceful degradation
