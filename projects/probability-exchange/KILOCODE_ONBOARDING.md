# Market Pulse Dashboard - Kilocode Onboarding Guide

**Last Updated:** November 30, 2025
**Status:** Production-ready frontend + Backend with mock data
**Next Phase:** Real API integration (Kalshi, Polymarket, Manifold)

---

## 🎯 Project Overview

**Market Pulse** is a real-time prediction markets intelligence platform that aggregates data from:
- **Kalshi** - Regulated event contracts (US-based)
- **Polymarket** - Crypto-based prediction markets
- **Manifold Markets** - Play-money prediction markets

**Goal:** Match real-time news events to trading opportunities across all three platforms.

**Target Users:** Serious prediction market traders (data-driven, sophisticated users)

---

## 📁 Project Structure

```
/home/billy/projects/probability exchange/
├── market-pulse-dashboard/          # Main React dashboard (PRODUCTION-READY)
│   ├── src/
│   │   ├── components/             # UI components
│   │   ├── lib/                    # API client, WebSocket
│   │   ├── types/                  # TypeScript types
│   │   └── hooks/                  # React hooks
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── package.json
│
├── backend/                         # FastAPI backend (NEEDS REAL APIs)
│   ├── app/
│   │   ├── api/v1/api.py          # Main API routes (uses MockClient)
│   │   ├── core/                   # Config, logging, security
│   │   └── main_simple.py         # FastAPI app entry point
│   ├── api_clients.py              # ⚠️ THIS IS WHERE YOU'LL WORK
│   └── API_DOCUMENTATION.md
│
├── waitlist_landing_page/           # Email capture (LIVE)
│
└── api_clients.py                   # Same as backend/api_clients.py
```

---

## 🚀 What's Currently Working

### ✅ Frontend (100% Complete)
- **URL:** http://localhost:3000
- **Tech:** React 19 + TypeScript + Vite + Recharts
- **Features:**
  - Professional Bloomberg Terminal aesthetic
  - Real-time WebSocket updates
  - Interactive price/volume charts
  - Market detail modals
  - Search and filtering
  - Mobile responsive
  - Production build: 234KB gzipped

### ✅ Backend (Mock Data Only)
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Tech:** FastAPI + Python + WebSockets
- **Status:** Uses `MockClient` for demo data
- **Endpoints Working:**
  - `GET /api/v1/markets` - List markets
  - `GET /api/v1/markets/{id}` - Market details
  - `GET /api/v1/status` - API status
  - `WS /api/v1/ws/markets` - Real-time updates

---

## ⚠️ What Needs to Be Done: Real API Integration

### Current State
Backend file `backend/app/api/v1/api.py` uses a **MockClient** (lines 66-106) that returns fake data.

### Your Mission
Replace MockClient with real API clients for:
1. **Kalshi API**
2. **Polymarket API**
3. **Manifold Markets API**

---

## 📋 API Integration Checklist

### 1. Kalshi API Integration

**File to Edit:** `backend/api_clients.py` (lines ~200-300)

**Current Class:** `KalshiClient` (skeleton exists)

**What You Need:**
- API Key: Get from https://trading-api.kalshi.com
- Base URL: `https://trading-api.kalshi.com/v2`
- Auth: API key in headers

**Methods to Implement:**
```python
async def get_markets(self, category=None, limit=50):
    # Fetch from /markets endpoint
    # Return list of MarketData objects

async def get_market(self, market_id):
    # Fetch specific market
    # Return MarketData object

async def place_order(self, order: OrderRequest):
    # Place buy/sell order
    # Return OrderResponse
```

**API Docs:** https://docs.kalshi.com

---

### 2. Polymarket API Integration

**File to Edit:** `backend/api_clients.py` (lines ~100-200)

**Current Class:** `PolymarketClient` (skeleton exists)

**What You Need:**
- API Key: Get from https://polymarket.com
- Base URL: `https://gamma-api.polymarket.com`
- Auth: Bearer token or API key

**Methods to Implement:**
```python
async def get_markets(self, category=None, limit=50):
    # Fetch from /markets endpoint
    # Map to MarketData format

async def get_market(self, market_id):
    # Fetch specific market

async def place_order(self, order: OrderRequest):
    # Place order via Polymarket API
```

**API Docs:** https://docs.polymarket.com

---

### 3. Manifold Markets API Integration

**File to Edit:** `backend/api_clients.py` (lines ~300-400)

**Current Class:** `ManifoldClient` (skeleton exists)

**What You Need:**
- API Key: Get from https://manifold.markets
- Base URL: `https://api.manifold.markets/v0`
- Auth: API key in headers

**Methods to Implement:**
```python
async def get_markets(self, category=None, limit=50):
    # Fetch from /markets endpoint
    # Return MarketData objects

async def get_market(self, market_id):
    # Fetch specific market

async def place_order(self, order: OrderRequest):
    # Place bet on Manifold
```

**API Docs:** https://docs.manifold.markets/api

---

## 🔧 Key Files to Understand

### 1. `backend/api_clients.py` (731 lines)

**Most Important File** - This is where ALL API integration happens.

**Key Classes:**
```python
@dataclass
class MarketData:
    """Universal market data format - ALL APIs map to this"""
    id: str
    platform: str  # "kalshi", "polymarket", "manifold"
    question: str
    current_price: float  # 0.0 to 1.0
    probability: float    # 0.0 to 1.0
    volume_24h: float
    category: str
    status: str  # "open", "closed", "resolved"
    # ... more fields

class PredictionMarketAggregator:
    """Combines data from all 3 platforms"""
    def add_client(self, name: str, client):
        # Register Kalshi/Polymarket/Manifold client

    async def get_all_markets(self, category=None, limit_per_platform=20):
        # Fetch from ALL platforms simultaneously
        # Merge and return combined results

# YOUR WORK: Implement these 3 classes
class KalshiClient: ...
class PolymarketClient: ...
class ManifoldClient: ...
```

### 2. `backend/app/api/v1/api.py` (361 lines)

**API Routes** - This file calls your API clients.

**Key Function to Update:**
```python
async def initialize_aggregator():
    """Currently uses MockClient - REPLACE WITH REAL CLIENTS"""
    global market_aggregator
    market_aggregator = PredictionMarketAggregator()

    # TODO: Replace MockClient with:
    kalshi = KalshiClient(api_key=settings.KALSHI_API_KEY)
    polymarket = PolymarketClient(api_key=settings.POLYMARKET_API_KEY)
    manifold = ManifoldClient(api_key=settings.MANIFOLD_API_KEY)

    market_aggregator.add_client("kalshi", kalshi)
    market_aggregator.add_client("polymarket", polymarket)
    market_aggregator.add_client("manifold", manifold)
```

### 3. `backend/app/core/config.py` (157 lines)

**Environment Configuration** - Add API keys here.

**What to Add:**
```python
class Settings(BaseSettings):
    # Add these:
    KALSHI_API_KEY: str = ""
    POLYMARKET_API_KEY: str = ""
    MANIFOLD_API_KEY: str = ""
```

Then create `backend/.env`:
```bash
KALSHI_API_KEY=your_kalshi_key
POLYMARKET_API_KEY=your_polymarket_key
MANIFOLD_API_KEY=your_manifold_key
```

---

## 🧪 Testing Your Integration

### 1. Start Backend
```bash
cd "/home/billy/projects/probability exchange/backend"
python3 -m uvicorn app.main_simple:app --reload
```

### 2. Test API Endpoints
```bash
# Get markets from all platforms
curl http://localhost:8000/api/v1/markets

# Get Kalshi markets only
curl http://localhost:8000/api/v1/markets?platform=kalshi

# Get crypto category
curl http://localhost:8000/api/v1/markets?category=crypto

# Check status
curl http://localhost:8000/api/v1/status
```

### 3. Start Frontend
```bash
cd "/home/billy/projects/probability exchange/market-pulse-dashboard"
npm run dev
```

Open http://localhost:3000 - Should show REAL market data!

---

## 📊 Data Flow

```
┌─────────────────┐
│  Kalshi API     │──┐
└─────────────────┘  │
                     │
┌─────────────────┐  │    ┌──────────────────────┐
│ Polymarket API  │──┼───▶│ PredictionMarket     │
└─────────────────┘  │    │ Aggregator           │
                     │    └──────────────────────┘
┌─────────────────┐  │              │
│ Manifold API    │──┘              │
└─────────────────┘                 │
                                    ▼
                         ┌──────────────────────┐
                         │ FastAPI Backend      │
                         │ /api/v1/markets      │
                         └──────────────────────┘
                                    │
                                    │ HTTP/WebSocket
                                    ▼
                         ┌──────────────────────┐
                         │ React Dashboard      │
                         │ (localhost:3000)     │
                         └──────────────────────┘
```

---

## 🐛 Common Issues & Solutions

### Issue: API Rate Limits
**Solution:** Implement caching in `PredictionMarketAggregator`
```python
self._cache = {}
self._cache_ttl = 60  # seconds
```

### Issue: Different Response Formats
**Solution:** Each client maps to `MarketData` standard format
```python
# Kalshi might return:
{"ticker": "BTCUP", "yes_price": 0.67}

# You map to:
MarketData(
    id="BTCUP",
    platform="kalshi",
    current_price=0.67,
    question=kalshi_data["question"]
)
```

### Issue: WebSocket Updates
**Solution:** Each client should support `async def subscribe_to_updates()`
Then push updates via FastAPI WebSocket

---

## 📖 API Documentation Links

- **Kalshi:** https://docs.kalshi.com
- **Polymarket:** https://docs.polymarket.com
- **Manifold:** https://docs.manifold.markets/api

---

## 🎓 Code Examples

### Example: Implementing KalshiClient

```python
class KalshiClient:
    def __init__(self, api_key: str, base_url: str = "https://trading-api.kalshi.com/v2"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {api_key}"}
        )

    async def get_markets(self, category: Optional[str] = None, limit: int = 50) -> List[MarketData]:
        url = f"{self.base_url}/markets"
        params = {"limit": limit}
        if category:
            params["category"] = category

        async with self.session.get(url, params=params) as response:
            data = await response.json()

            # Map Kalshi format to MarketData
            markets = []
            for kalshi_market in data["markets"]:
                market = MarketData(
                    id=kalshi_market["ticker"],
                    platform="kalshi",
                    question=kalshi_market["title"],
                    description=kalshi_market.get("description", ""),
                    category=kalshi_market.get("category", "other"),
                    current_price=kalshi_market["yes_price"],
                    probability=kalshi_market["yes_price"],
                    volume_24h=kalshi_market.get("volume_24h", 0),
                    total_volume=kalshi_market.get("volume", 0),
                    status=kalshi_market["status"],
                    url=f"https://kalshi.com/markets/{kalshi_market['ticker']}",
                    last_updated=datetime.utcnow()
                )
                markets.append(market)

            return markets
```

---

## ✅ Definition of Done

Your API integration is complete when:

1. ✅ All 3 clients (Kalshi, Polymarket, Manifold) implemented
2. ✅ `get_markets()` returns real data from each platform
3. ✅ Data correctly mapped to `MarketData` format
4. ✅ Frontend displays real markets at http://localhost:3000
5. ✅ WebSocket updates work for price changes
6. ✅ No errors in backend logs
7. ✅ API status endpoint shows all platforms "connected"
8. ✅ Can filter by category and platform
9. ✅ Error handling for API failures
10. ✅ Tests pass (create basic tests in `backend/tests/`)

---

## 🚀 After Integration

Once APIs are working:

1. **Deploy Backend:** Use Render, Railway, or Fly.io
2. **Update Frontend:** Change `.env.production` to point to deployed backend
3. **Deploy Frontend:** Use Netlify or Vercel (already configured)
4. **Add Monitoring:** Sentry for errors, Uptime monitoring
5. **Add Analytics:** Track which markets users view most

---

## 💡 Tips

1. **Start with Manifold** - Easiest API, no auth required for reading
2. **Use Mock Data First** - Test your client structure with fake data
3. **Map Data Carefully** - Each platform has different field names
4. **Handle Errors Gracefully** - Some markets might be missing fields
5. **Use Type Hints** - TypeScript on frontend, Python type hints on backend
6. **Test Each Platform Separately** - Don't try all 3 at once

---

## 📞 Need Help?

**Frontend Issues:**
- Check: `market-pulse-dashboard/src/lib/api-client.ts`
- Logs: Browser console at http://localhost:3000

**Backend Issues:**
- Check: `backend/app/api/v1/api.py`
- Logs: `/tmp/backend.log` or terminal output

**API Questions:**
- Refer to each platform's documentation
- Check existing code patterns in `api_clients.py`

---

## 🎯 Quick Start Commands

```bash
# Terminal 1: Backend
cd "/home/billy/projects/probability exchange/backend"
python3 -m uvicorn app.main_simple:app --reload --port 8000

# Terminal 2: Frontend
cd "/home/billy/projects/probability exchange/market-pulse-dashboard"
npm run dev

# Terminal 3: Test APIs
curl http://localhost:8000/api/v1/markets
curl http://localhost:8000/api/v1/status
```

---

**Good luck! The frontend is production-ready and waiting for real data. Focus on `backend/api_clients.py` and you'll have a fully functional platform.**
