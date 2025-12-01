# Real API Integration Setup Guide

This guide explains how to configure and set up real API integrations for MarketPulse Pro prediction markets dashboard.

## Overview

The system now supports real API integrations for multiple prediction market platforms:

- **Polymarket**: Primary prediction market platform
- **Kalshi**: Events and prediction markets  
- **Manifold Markets**: Community-driven prediction markets
- **News API**: Market sentiment analysis

## API Key Setup

### Environment Variables

Set the following environment variables to enable real API integrations:

```bash
# Polymarket API (Primary platform)
export POLYMARKET_API_KEY="your_polymarket_api_key"

# Kalshi API (Events and markets)
export KALSHI_API_KEY="your_kalshi_api_key"
export KALSHI_SECRET_KEY="your_kalshi_secret_key"

# Manifold Markets API (Community markets)
export MANIFOLD_API_KEY="your_manifold_api_key"

# News API (For sentiment analysis)
export NEWS_API_KEY="your_newsapi_key"
```

### Getting API Keys

#### 1. Polymarket API
- Visit: https://docs.polymarket.com/
- Register for API access
- Get your API key from the developer dashboard
- Free tier available with rate limits

#### 2. Kalshi API
- Visit: https://trading-api.kalshi.com/
- Create an account and request API access
- Get both API key and secret key
- Some endpoints require authentication

#### 3. Manifold Markets API
- Visit: https://api.manifold.markets/
- Public API available without authentication for reading
- Authentication required for trading operations
- Free access with reasonable rate limits

#### 4. News API
- Visit: https://newsapi.org/
- Register for free account
- Get API key from dashboard
- Free tier: 1000 requests/day

## Configuration Files

### .env File
Create a `.env` file in your project root:

```bash
# Polymarket Configuration
POLYMARKET_API_KEY=your_polymarket_key_here

# Kalshi Configuration  
KALSHI_API_KEY=your_kalshi_key_here
KALSHI_SECRET_KEY=your_kalshi_secret_here

# Manifold Configuration
MANIFOLD_API_KEY=your_manifold_key_here

# News API Configuration
NEWS_API_KEY=your_newsapi_key_here
```

### Docker Configuration
For Docker deployments, add environment variables to `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - POLYMARKET_API_KEY=${POLYMARKET_API_KEY}
      - KALSHI_API_KEY=${KALSHI_API_KEY}
      - KALSHI_SECRET_KEY=${KALSHI_SECRET_KEY}
      - MANIFOLD_API_KEY=${MANIFOLD_API_KEY}
      - NEWS_API_KEY=${NEWS_API_KEY}
```

## Running with Real APIs

### 1. Start the Backend
```bash
cd backend
python -m app.main
```

The system will automatically detect available API keys and initialize the corresponding clients.

### 2. Check API Status
```bash
curl http://localhost:8000/api/v1/status
```

Response will show which APIs are connected:
```json
{
  "status": "operational",
  "timestamp": "2025-11-27T12:50:41.010Z",
  "platforms": {
    "polymarket": {
      "connected": true,
      "last_check": "2025-11-27T12:50:41.010Z",
      "status": "active"
    },
    "kalshi": {
      "connected": false,
      "last_check": "2025-11-27T12:50:41.010Z",
      "status": "inactive"
    }
  }
}
```

### 3. Test Market Data
```bash
curl http://localhost:8000/api/v1/markets?limit=10
```

## Fallback Behavior

If no API keys are provided, the system automatically falls back to mock data:

- Mock markets with realistic data
- Simulated price movements
- All features remain functional
- Perfect for development and testing

## API Rate Limits

Each platform has different rate limits:

| Platform | Rate Limit | Notes |
|----------|------------|-------|
| Polymarket | 60/min | Public data mostly free |
| Kalshi | 100/min | Requires authentication |
| Manifold | 60/min | Public endpoints free |
| News API | 1000/day | Free tier limit |

## Error Handling

The system includes comprehensive error handling:

- **Rate Limit Exceeded**: Automatic retry with exponential backoff
- **API Errors**: Graceful fallback to other platforms
- **Network Issues**: Automatic reconnection attempts
- **Invalid Keys**: Clear error messages and fallback to mock data

## Testing Real APIs

Run the test script to verify API connectivity:

```bash
python real_api_clients.py
```

Expected output:
```
Testing Real Prediction Market API Clients...
Retrieved 45 markets from real APIs
Sample market: Will Bitcoin reach $100k by 2025? (polymarket) - $0.67
Retrieved 12 news articles
Real API client testing completed!
```

## Monitoring and Logging

### API Health Monitoring
- Endpoint: `/api/v1/health`
- Shows connection status for all platforms
- Real-time WebSocket connection count
- Data source identification (real vs mock)

### Logging
All API interactions are logged with:
- Request/response status
- Rate limit information
- Error details
- Performance metrics

## Security Considerations

### API Key Security
- Store keys in environment variables
- Never commit keys to version control
- Use different keys for development/production
- Rotate keys regularly

### Network Security
- Use HTTPS for all API endpoints
- Validate SSL certificates
- Implement request signing where required
- Monitor for unusual API usage

## Troubleshooting

### Common Issues

1. **"No API keys found"**
   - Check environment variables are set
   - Verify variable names match exactly
   - Restart application after setting variables

2. **"Rate limit exceeded"**
   - Wait for rate limit reset
   - Check API quota in provider dashboard
   - Consider upgrading API plan

3. **"Authentication failed"**
   - Verify API key is correct
   - Check key permissions
   - Ensure account is active

4. **"Network timeout"**
   - Check internet connectivity
   - Verify API endpoint URLs
   - Check firewall settings

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m app.main
```

## Production Deployment

### Environment Setup
```bash
# Production environment variables
export POLYMARKET_API_KEY="prod_key_here"
export KALSHI_API_KEY="prod_key_here"
export KALSHI_SECRET_KEY="prod_secret_here"
export MANIFOLD_API_KEY="prod_key_here"
export NEWS_API_KEY="prod_key_here"

# Start with production config
export ENVIRONMENT=production
python -m app.main
```

### Health Checks
Monitor API health in production:
```bash
# Check every 5 minutes
*/5 * * * * curl -f http://localhost:8000/api/v1/health || alert_ops_team
```

## Support

For issues with specific APIs:
- **Polymarket**: https://discord.gg/polymarket
- **Kalshi**: https://kalshi.com/support  
- **Manifold**: https://discord.gg/manifoldmarkets
- **News API**: https://newsapi.org/support

The system is designed to be robust and handle API failures gracefully while maintaining functionality through fallback mechanisms.