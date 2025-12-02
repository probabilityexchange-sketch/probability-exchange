# DFlow Solana Integration Guide

Complete guide for integrating DFlow's tokenized prediction markets (Kalshi on Solana) into your MarketPulse Pro platform.

## Overview

DFlow provides access to tokenized Kalshi prediction markets on Solana as SPL tokens. This integration enables:

- **On-chain Trading**: True Solana token ownership (not synthetic)
- **Deep Liquidity**: Access to Kalshi markets with institutional-grade execution
- **DeFi Composability**: Use prediction market positions in lending, borrowing, and other DeFi protocols
- **Concurrent Liquidity Programs (CLPs)**: Bridge offchain liquidity with onchain users

## Architecture

```
Frontend (Phantom/Solflare Wallet)
        ↓
FastAPI Backend (DFlow Trading Router)
        ↓
DFlow API Client (pond.dflow.net)
        ↓
Solana Blockchain (SPL Tokens)
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install base58 pynacl solders aiohttp
```

### 2. Environment Configuration

Create or update your `.env` file:

```bash
# DFlow API Configuration
DFLOW_API_KEY=your_dflow_api_key_here  # Optional for public endpoints
DFLOW_BASE_URL=https://pond.dflow.net/api

# Solana Wallet Configuration
SOLANA_WALLET_SECRET_KEY=your_secure_secret_key_here

# Rate Limiting
DFLOW_RATE_LIMIT=100
```

### 3. Update Main API Router

Edit `backend/app/api/v1/api.py` to include DFlow router:

```python
from app.api.v1.dflow_trading import dflow_router

# Include DFlow trading routes
router.include_router(
    dflow_router,
    prefix="/dflow",
    tags=["dflow-solana-trading"]
)
```

### 4. Test the Integration

Run the test scripts:

```bash
# Test DFlow API client
python backend/dflow_client.py

# Test Solana wallet manager
python backend/solana_wallet.py
```

### 5. Start Your Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

#### Create Challenge
```http
POST /api/v1/dflow/auth/solana/challenge
Content-Type: application/json

{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
```

#### Verify Signature
```http
POST /api/v1/dflow/auth/solana/verify
Content-Type: application/json

{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "challenge": "Sign this message...",
  "signature": "base58_encoded_signature"
}
```

### Market Discovery

#### Get Markets
```http
GET /api/v1/dflow/markets?category=politics&limit=50
```

Response:
```json
{
  "markets": [
    {
      "id": "market_123",
      "platform": "dflow",
      "chain": "solana",
      "question": "Will Bitcoin reach $100K by end of 2025?",
      "yes_token_mint": "YESTokenMintAddress...",
      "no_token_mint": "NOTokenMintAddress...",
      "yes_price": 0.65,
      "no_price": 0.35,
      "volume_24h": 125000,
      "liquidity": 500000
    }
  ],
  "total": 50
}
```

#### Get Market Detail
```http
GET /api/v1/dflow/markets/{market_id}
```

### Trading

#### Get Swap Quote
```http
POST /api/v1/dflow/trading/quote
Content-Type: application/json

{
  "input_token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
  "output_token": "YESTokenMintAddress...",
  "amount": "10000000",  # 10 USDC (6 decimals)
  "slippage_tolerance": 0.01
}
```

Response:
```json
{
  "quote": {
    "in_token": "USDC",
    "out_token": "YES",
    "in_amount": "10000000",
    "out_amount": "15384615",
    "price_impact": 0.002,
    "estimated_slippage": 0.005,
    "route": [...],
    "expires_at": "2025-12-02T12:30:00Z"
  }
}
```

#### Execute Swap
```http
POST /api/v1/dflow/trading/swap
Content-Type: application/json

{
  "input_token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "output_token": "YESTokenMintAddress...",
  "amount": "10000000",
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "session_id": "your_session_id",
  "mode": "declarative",
  "slippage_tolerance": 0.01
}
```

Response:
```json
{
  "success": true,
  "mode": "declarative",
  "result": {
    "intent_id": "intent_abc123",
    "status": "pending",
    "estimated_completion": "2025-12-02T12:35:00Z"
  }
}
```

#### Check Order Status
```http
GET /api/v1/dflow/trading/order/{order_id}
```

### Portfolio

#### Get Positions
```http
GET /api/v1/dflow/portfolio/positions/{wallet_address}?session_id=your_session_id
```

Response:
```json
{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "positions": [
    {
      "market_id": "market_123",
      "token_mint": "YESTokenMintAddress...",
      "outcome": "YES",
      "shares": "15.5",
      "average_price": "0.65",
      "current_value": "10.075",
      "pnl": "-0.425",
      "platform": "dflow"
    }
  ],
  "total": 1
}
```

#### Get Balance
```http
GET /api/v1/dflow/portfolio/balance/{wallet_address}?session_id=your_session_id
```

### Information

#### Available Tokens
```http
GET /api/v1/dflow/tokens?include_decimals=true
```

#### Trading Venues
```http
GET /api/v1/dflow/venues
```

### Health Check
```http
GET /api/v1/dflow/health
```

## Swap Modes

### Imperative Mode
- Full control over transaction
- Review route before signing
- Higher precision for large trades
- User signs one transaction

### Declarative Mode (Recommended)
- Deferred route calculation
- Better slippage protection
- Sandwich attack resistance
- Multi-transaction execution
- Optimal for most use cases

## Security Considerations

1. **Wallet Signature Verification**: All transactions require user signature
2. **Session Management**: Sessions expire after 24 hours
3. **Challenge-Response Auth**: Prevents replay attacks
4. **Rate Limiting**: API calls are rate-limited
5. **No Private Key Storage**: Backend never stores private keys

## Frontend Integration

See `DFLOW_FRONTEND_EXAMPLE.jsx` for complete React implementation with:
- Phantom/Solflare wallet connection
- Market browsing and search
- Trading interface
- Portfolio tracking
- Transaction history

## Testing

### Unit Tests
```bash
pytest backend/tests/test_dflow_client.py
```

### Integration Tests
```bash
pytest backend/tests/test_dflow_integration.py
```

### Manual Testing
1. Connect Phantom wallet to devnet
2. Get devnet SOL from faucet
3. Authenticate via challenge-response
4. Browse markets
5. Execute test swap
6. Check position in portfolio

## Troubleshooting

### Common Issues

**"Invalid Solana address"**
- Ensure wallet address is base58-encoded 32-byte public key
- Check for typos or incorrect format

**"Failed to verify signature"**
- Signature must be from the correct wallet
- Ensure challenge message wasn't modified
- Try base58 or base64 encoding

**"Session expired"**
- Re-authenticate with wallet
- Sessions last 24 hours by default

**"Insufficient liquidity"**
- Try smaller trade size
- Check market liquidity
- Use declarative mode for better routing

**"Slippage exceeded"**
- Increase slippage tolerance
- Trade smaller amounts
- Wait for better market conditions

## Resources

- **DFlow Documentation**: https://pond.dflow.net/introduction
- **Solana Web3.js**: https://solana-labs.github.io/solana-web3.js/
- **Phantom Wallet**: https://phantom.app/
- **Solflare Wallet**: https://solflare.com/

## Support

For integration issues:
1. Check API logs: `backend/logs/dflow.log`
2. Test connectivity: `GET /api/v1/dflow/health`
3. Review Solana transaction: Solana Explorer
4. DFlow Discord: https://discord.gg/dflow

## DFlow Grants Program

Kalshi is supporting builders with a $2M grants program. Apply at:
https://www.dflow.net/grants

## Next Steps

1. ✅ Backend integration complete
2. ⬜ Implement frontend wallet connection
3. ⬜ Add market browsing UI
4. ⬜ Build trading interface
5. ⬜ Deploy to testnet
6. ⬜ Security audit
7. ⬜ Production deployment

## License

Integration code is provided under MIT license. DFlow API usage subject to DFlow terms of service.
