# Open Questions

## Critical Decisions Needed 🔴

### Centering Approach
**Question**: Should we fix the Rich Align.center() implementation or handle centering in OBS?

**Options**:
1. **Debug and fix Rich Align approach**
   - Pros: Content naturally centered in terminal
   - Cons: Complex, caused syntax errors, may not work well with markdown
   - Effort: Medium-High

2. **Use OBS Transform/Positioning**
   - Pros: Simple, reliable, full control
   - Cons: Manual adjustment, not "real" centering
   - Effort: Low

3. **Hybrid: Center tables only, not markdown**
   - Pros: Tables (most important) get centered
   - Cons: Inconsistent, ASCII art still left-aligned
   - Effort: Medium

**Your preference?**

---

### News Ticker API
**Question**: Should we get CryptoPanic API key or use alternative news source?

**Options**:
1. **Get CryptoPanic free API key**
   - Pros: Purpose-built for crypto news
   - Cons: Requires signup, may have rate limits
   - Cost: Free tier available

2. **Use CoinGecko or CoinMarketCap news APIs**
   - Pros: Already using for prices, consolidated
   - Cons: News may be less timely
   - Cost: Free tiers available

3. **Scrape Twitter/X for crypto hashtags**
   - Pros: More real-time, trending topics
   - Cons: Requires Twitter API ($$), may be flaky
   - Cost: Twitter API pricing applies

4. **Disable news ticker for now**
   - Pros: Simplest, one less dependency
   - Cons: Missing feature, less engaging
   - Cost: Free

**Your preference?**

---

### SSH Tunnel Management
**Question**: How should we handle tunnel persistence?

**Options**:
1. **Manual reconnection (current)**
   - Pros: Simple, full control
   - Cons: Requires monitoring, can cause stream downtime
   
2. **autossh daemon**
   - Pros: Auto-reconnects, battle-tested
   - Cons: Another dependency, needs configuration
   
3. **systemd service**
   - Pros: Integrated with system, auto-start on boot
   - Cons: More complex setup, system-level config

4. **VPN connection**
   - Pros: Always-on, encrypted
   - Cons: Overkill, adds latency, costs money

**Your preference?**

---

## Medium Priority Questions 🟡

### Token Filtering
**Question**: Should we filter tokens by minimum liquidity to avoid displaying dead/scam tokens?

**Considerations**:
- Current: Display all tokens found by search
- Proposed: Only show tokens with >$10k liquidity
- Trade-off: Miss some ultra-low-cap gems vs. avoid rugs

**Your preference**: Filter or show all?

---

### Leaderboard Rotation Timing
**Question**: Are current rotation intervals good, or should we adjust?

**Current Timing**:
- Main leaderboard: Every 12 cycles (~60 seconds)
- Volume board: Every 25 cycles (~125 seconds)
- Market cap categories: Every 30 cycles (~150 seconds)
- Liquidity board: Every 35 cycles (~175 seconds)

**Should we**:
- Show each board more frequently?
- Make intervals equal?
- Add user-configurable timing?

---

### Gem of the Hour Criteria
**Question**: What defines a "gem" for the Gem of the Hour feature?

**Current**: Low mcap (<$10M) + decent volume (>$10k)

**Should we add**:
- Minimum liquidity requirement?
- Recent launch time window (e.g., <7 days old)?
- Holder count minimum?
- Price momentum (must be going up)?

---

### Error Handling Strategy
**Question**: When APIs fail, what should dashboard do?

**Options**:
1. **Show cached data with warning**
   - Pros: Keeps stream running
   - Cons: Stale data might mislead

2. **Show error message, skip that screen**
   - Pros: Transparent
   - Cons: Less content variety

3. **Use fallback/dummy data**
   - Pros: No gaps in stream
   - Cons: Not real data

4. **Retry with exponential backoff**
   - Pros: Might recover quickly
   - Cons: Delays display

**Your preference?**

---

## Low Priority Questions 🟢

### Streaming Resolution
**Question**: What's your target streaming resolution?

**Options**:
- 1280x720 (720p) - Lower bandwidth, safer
- 1920x1080 (1080p) - Better quality, higher bandwidth
- Current: ?

**Your setup**:
- Internet upload speed?
- Pump.fun requirements?

---

### Token Search Strategy
**Question**: Should we fetch more tokens per cycle or keep at 8?

**Current**: 8 random search terms per 60-second cycle

**Considerations**:
- More = better diversity
- More = higher API load, slower fetch
- DexScreener rate limits unknown

**Your preference?**

---

### Dashboard Variants
**Question**: Should we consolidate V1/V2/V3 or keep all running?

**Current**: 3 versions in parallel
- V1 on port 7681
- V3 on port 7682

**Options**:
1. Keep both (current)
2. Deprecate V1, only run V3
3. Create V4 with all fixes, sunset older versions

---

### Color Scheme
**Question**: Happy with current colors or want adjustments?

**Current**:
- Green for gains/positive
- Red for losses/negative
- Cyan for titles
- Yellow for highlights

**Should we**:
- Add more color variety?
- Theme it differently (dark mode, light mode, neon)?
- Match Pump.fun branding colors?

---

### Monitoring & Alerts
**Question**: Do you want notifications when dashboard goes down?

**Options**:
- Email alerts
- Discord webhook
- SMS/phone call (PagerDuty, etc.)
- None (manual monitoring)

---

## Future Feature Questions 🔮

### Multi-Chain Support
**Question**: Interest in showing tokens from other chains?

**Possible additions**:
- Base chain (Coinbase's L2)
- Ethereum mainnet memecoins
- Other Solana DEXes beyond Pump.fun

**Priority?**

---

### Interactive Features
**Question**: Should dashboard have viewer interaction?

**Ideas**:
- Chat commands to change what's displayed
- Voting on which tokens to feature
- Tip-triggered special displays
- Request specific token lookups

**Interest level?**

---

### Analytics & Tracking
**Question**: Want to track which tokens perform best after being featured?

**Could track**:
- Token performance 1hr/24hr after display
- Grok prediction accuracy
- Most-viewed tokens (if we add tracking)
- Viewer engagement patterns

**Useful?**

---

## Questions for Later 📅

- Mobile companion app?
- Discord bot integration?
- Automated trading based on displayed signals?
- Premium features or monetization?
- Community contributions/open source?

---

## Decisions Made (Moved from Questions) ✅

- ✅ Use DexScreener API for token data
- ✅ Stream via OBS from local machine, not server
- ✅ Use ttyd for web terminal rendering
- ✅ Expand to 50+ token search terms
- ✅ Add K notation for market caps <$1M
- ✅ Create multiple leaderboard types
- ✅ Use Rich library for terminal UI
