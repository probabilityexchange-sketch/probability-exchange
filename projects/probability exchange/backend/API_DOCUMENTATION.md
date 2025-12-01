# Market Pulse Pro Backend API Documentation

## Status: Running Successfully

**Backend URL:** `http://localhost:8000`
**API Version:** v1
**Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## API Endpoints

### Health & Status

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "marketpulse-backend",
  "version": "1.0.0"
}
```

#### GET `/api/v1/health`
Alternative health check endpoint.

**Response:** Same as `/health`

#### GET `/api/v1/status`
Detailed API status including platform connectivity and WebSocket status.

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2025-11-30T22:44:17.953691",
  "platforms": {
    "polymarket": {
      "connected": true,
      "last_check": "2025-11-30T22:44:17.953668",
      "status": "active"
    }
  },
  "aggregator": {
    "clients_count": 1,
    "initialized": true
  },
  "websocket": {
    "active_connections": 0,
    "status": "active"
  }
}
```

---

### Market Data Endpoints

#### GET `/api/v1/markets`
Get aggregated markets from all platforms.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "crypto", "stocks")
- `limit` (optional, default: 50): Number of markets to return

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/markets?limit=5"
curl "http://localhost:8000/api/v1/markets?category=crypto&limit=10"
```

**Response:**
```json
{
  "markets": [
    {
      "id": "market_0",
      "platform": "polymarket",
      "question": "Will Bitcoin increase by 10% this week?",
      "description": "Market about Bitcoin price movement",
      "category": "crypto",
      "market_type": "binary",
      "outcomes": null,
      "current_price": 0.45,
      "probability": 0.45,
      "volume_24h": 1000,
      "total_volume": 5000,
      "liquidity": 800,
      "status": "open",
      "url": null,
      "last_updated": "2025-11-30T22:44:16.577570"
    }
  ],
  "total": 1,
  "timestamp": "2025-11-30T22:44:16.577649"
}
```

#### GET `/api/v1/markets/{market_id}`
Get detailed information for a specific market.

**Path Parameters:**
- `market_id`: Unique market identifier

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/markets/market_1"
```

**Response:**
```json
{
  "id": "market_1",
  "platform": "polymarket",
  "question": "Will Bitcoin increase by 10% this week?",
  "description": "Market about Bitcoin price movement",
  "category": "crypto",
  "market_type": "binary",
  "outcomes": null,
  "current_price": 0.67,
  "probability": 0.67,
  "volume_24h": 2500,
  "total_volume": 10000,
  "liquidity": 2000,
  "open_time": null,
  "close_time": null,
  "resolution_date": null,
  "status": "open",
  "url": null,
  "last_updated": "2025-11-30T22:44:28.030421"
}
```

**Error Response (404):**
```json
{
  "detail": "Market not found"
}
```

#### GET `/api/v1/markets/compare`
Compare the same market across different platforms.

**Query Parameters:**
- `question` (required): Market question to compare across platforms

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/markets/compare?question=Will%20Bitcoin%20increase"
```

**Response:**
```json
{
  "question": "Will Bitcoin increase",
  "platforms": {
    "polymarket": {
      "id": "market_0",
      "platform": "polymarket",
      "question": "Will Bitcoin increase by 10% this week?",
      "probability": 0.45,
      "current_price": 0.45,
      "volume_24h": 1000,
      "status": "open",
      "last_updated": "2025-11-30T22:44:16.577570"
    }
  },
  "timestamp": "2025-11-30T22:44:16.577649"
}
```

---

### WebSocket Endpoint

#### WS `/api/v1/ws/markets`
Real-time market updates via WebSocket connection.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/markets');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market update:', data);
};
```

**Message Types:**

**Market Update:**
```json
{
  "type": "market_update",
  "data": {
    "id": "market_1",
    "platform": "polymarket",
    "current_price": 0.68,
    "probability": 0.68,
    "volume_24h": 2550,
    "last_updated": "2025-11-30T22:45:00.000000"
  },
  "timestamp": "2025-11-30T22:45:00.000000"
}
```

**Acknowledgment:**
```json
{
  "type": "ack",
  "timestamp": "2025-11-30T22:45:00.000000"
}
```

**Features:**
- Broadcasts market updates every 5 seconds
- Automatic reconnection on disconnect
- Keepalive ping/pong mechanism

---

## Market Data Schema

### Market Object

| Field | Type | Description | Nullable |
|-------|------|-------------|----------|
| `id` | string | Unique market identifier | No |
| `platform` | string | Platform name (e.g., "polymarket") | No |
| `question` | string | Market question/title | No |
| `description` | string | Detailed market description | No |
| `category` | string | Market category (e.g., "crypto", "stocks") | No |
| `market_type` | string | Type of market (e.g., "binary") | No |
| `outcomes` | array | Possible market outcomes | Yes |
| `current_price` | number | Current market price (0.0-1.0) | No |
| `probability` | number | Market probability (0.0-1.0) | No |
| `volume_24h` | number | 24-hour trading volume | No |
| `total_volume` | number | Total trading volume | No |
| `liquidity` | number | Current liquidity | No |
| `status` | string | Market status ("open", "closed", "resolved") | No |
| `url` | string | Platform URL for the market | Yes |
| `last_updated` | string (ISO 8601) | Last update timestamp | No |
| `open_time` | string (ISO 8601) | Market open time | Yes |
| `close_time` | string (ISO 8601) | Market close time | Yes |
| `resolution_date` | string (ISO 8601) | Expected resolution date | Yes |

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## CORS Configuration

The API allows cross-origin requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8000`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8000`

All HTTP methods and headers are allowed.

---

## Current Implementation Notes

### Mock Data Mode
The backend currently uses **mock data** via the `MockClient` class. This is intentional for the MVP/demo phase:
- Returns simulated market data
- Generates predictable responses for testing
- No external API calls required
- No API keys needed

### Real API Integration
To enable real API integration, update `/home/billy/projects/probability exchange/backend/app/api/v1/api.py`:

```python
# Replace MockClient with real clients:
polymarket_client = PolymarketClient(api_key="your_key", base_url="https://gamma-api.polymarket.com")
kalshi_client = KalshiClient(api_key="your_key", base_url="https://trading-api.kalshi.com/v2")
manifold_client = ManifoldClient(api_key="your_key", base_url="https://api.manifold.markets/v0")

market_aggregator.add_client("polymarket", polymarket_client)
market_aggregator.add_client("kalshi", kalshi_client)
market_aggregator.add_client("manifold", manifold_client)
```

---

## Testing the API

### Quick Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Get all markets
curl http://localhost:8000/api/v1/markets

# Get crypto markets only
curl "http://localhost:8000/api/v1/markets?category=crypto&limit=10"

# Get specific market
curl http://localhost:8000/api/v1/markets/market_1

# Check API status
curl http://localhost:8000/api/v1/status

# Access interactive docs
open http://localhost:8000/docs
```

### Python Test Example

```python
import requests

# Get markets
response = requests.get('http://localhost:8000/api/v1/markets', params={'limit': 10})
markets = response.json()

print(f"Found {markets['total']} markets")
for market in markets['markets']:
    print(f"{market['question']}: {market['probability']:.2%}")
```

### JavaScript/TypeScript Test Example

```typescript
// Fetch markets
const response = await fetch('http://localhost:8000/api/v1/markets?limit=10');
const data = await response.json();

console.log(`Found ${data.total} markets`);
data.markets.forEach(market => {
  console.log(`${market.question}: ${(market.probability * 100).toFixed(1)}%`);
});

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/markets');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'market_update') {
    console.log('Market update:', update.data);
  }
};
```

---

## Logs

Backend logs are available at: `/tmp/backend.log`

```bash
tail -f /tmp/backend.log
```

---

## Stopping the Backend

```bash
# Find the process
ps aux | grep uvicorn

# Kill by process name
pkill -f "uvicorn app.main_simple"
```

---

## Next Steps for Production

1. **Replace Mock Data**: Integrate real Polymarket, Kalshi, and Manifold API clients
2. **Add Authentication**: Implement JWT authentication for protected endpoints
3. **Database Integration**: Connect to PostgreSQL/MongoDB for data persistence
4. **Rate Limiting**: Add rate limiting middleware
5. **Caching**: Implement Redis caching for market data
6. **Error Tracking**: Add Sentry or similar error tracking
7. **Monitoring**: Add Prometheus metrics and Grafana dashboards
8. **Testing**: Add comprehensive unit and integration tests
9. **CI/CD**: Set up automated testing and deployment
10. **Documentation**: Auto-generate API documentation from OpenAPI schema

---

**Last Updated:** 2025-11-30
**API Version:** 1.0.0
**Backend Status:** ✅ Running and operational
