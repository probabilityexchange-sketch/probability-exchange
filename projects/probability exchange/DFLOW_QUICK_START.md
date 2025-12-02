# DFlow Integration Quick Start

Get up and running with DFlow Solana prediction markets in 5 minutes.

## What You're Getting

✅ **Backend API** - Complete FastAPI integration with DFlow
✅ **Solana Wallets** - Phantom & Solflare wallet support
✅ **Trading Engine** - Buy/sell prediction market tokens
✅ **Portfolio Tracking** - Real-time position monitoring
✅ **Frontend Example** - React components ready to use

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup_dflow.sh
```

### Option 2: Manual Setup

```bash
# 1. Install Python dependencies
cd backend
pip install -r requirements_dflow.txt

# 2. Create .env file
cp .env.example .env

# 3. Add DFlow configuration to .env
echo "DFLOW_API_KEY=" >> .env
echo "DFLOW_BASE_URL=https://pond.dflow.net/api" >> .env
echo "SOLANA_WALLET_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 4. Test the integration
python dflow_client.py
python solana_wallet.py
```

## Configuration

Edit `backend/.env`:

```bash
# Required
SOLANA_WALLET_SECRET_KEY=your_secure_random_key

# Optional (DFlow works without API key for public endpoints)
DFLOW_API_KEY=your_dflow_api_key
```

## Start Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test API

```bash
# Health check
curl http://localhost:8000/api/v1/dflow/health

# Get markets
curl http://localhost:8000/api/v1/dflow/markets?limit=10

# Get tokens
curl http://localhost:8000/api/v1/dflow/tokens
```

## Connect Your Frontend

### Install Solana Wallet Adapters

```bash
npm install --save \
  @solana/wallet-adapter-react \
  @solana/wallet-adapter-react-ui \
  @solana/wallet-adapter-wallets \
  @solana/web3.js \
  bs58
```

### Add Wallet Provider

```jsx
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { clusterApiUrl } from '@solana/web3.js';

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

function App() {
  const network = WalletAdapterNetwork.Mainnet;
  const endpoint = clusterApiUrl(network);

  const wallets = [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter({ network })
  ];

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <DFlowTradingDashboard />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}
```

### Use the Example Component

Copy `DFLOW_FRONTEND_EXAMPLE.jsx` into your project:

```jsx
import DFlowTradingDashboard from './components/DFlowTradingDashboard';

// Use in your app
<DFlowTradingDashboard />
```

## API Endpoints Reference

### Authentication
- `POST /api/v1/dflow/auth/solana/challenge` - Get challenge
- `POST /api/v1/dflow/auth/solana/verify` - Verify signature

### Markets
- `GET /api/v1/dflow/markets` - List markets
- `GET /api/v1/dflow/markets/{id}` - Market details

### Trading
- `POST /api/v1/dflow/trading/quote` - Get quote
- `POST /api/v1/dflow/trading/swap` - Execute swap
- `GET /api/v1/dflow/trading/order/{id}` - Order status

### Portfolio
- `GET /api/v1/dflow/portfolio/positions/{wallet}` - Get positions
- `GET /api/v1/dflow/portfolio/balance/{wallet}` - Get balance

## Example: Buy Prediction Market Shares

```javascript
// 1. Connect wallet
const { publicKey, signMessage } = useWallet();

// 2. Authenticate
const challengeResponse = await fetch('/api/v1/dflow/auth/solana/challenge', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ wallet_address: publicKey.toString() })
});

const { challenge } = await challengeResponse.json();
const signature = await signMessage(new TextEncoder().encode(challenge));

const authResponse = await fetch('/api/v1/dflow/auth/solana/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    wallet_address: publicKey.toString(),
    challenge,
    signature: bs58.encode(signature)
  })
});

const { session_id } = await authResponse.json();

// 3. Get quote
const quoteResponse = await fetch('/api/v1/dflow/trading/quote', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input_token: 'USDC_MINT',
    output_token: 'YES_TOKEN_MINT',
    amount: '10000000', // 10 USDC
    slippage_tolerance: 0.01
  })
});

const { quote } = await quoteResponse.json();

// 4. Execute swap
const swapResponse = await fetch('/api/v1/dflow/trading/swap', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input_token: quote.in_token,
    output_token: quote.out_token,
    amount: quote.in_amount,
    wallet_address: publicKey.toString(),
    session_id,
    mode: 'declarative'
  })
});

const { result } = await swapResponse.json();
console.log('Trade executed:', result);
```

## Common Issues

**"Module not found: base58"**
```bash
pip install base58
```

**"Invalid Solana address"**
- Ensure wallet is connected
- Check address format (base58, 32 bytes)

**"Authentication failed"**
- Make sure wallet signs the exact challenge message
- Check signature encoding (base58 or base64)

**"No markets returned"**
- DFlow API might be down - check health endpoint
- Try without API key first (public endpoints)

## What's Next?

1. ✅ Test on devnet first
2. ✅ Get test SOL from faucet
3. ✅ Execute small test trades
4. ✅ Monitor transactions on Solana Explorer
5. ✅ Apply for DFlow grants ($2M available)

## Resources

- **Documentation**: `DFLOW_INTEGRATION_GUIDE.md`
- **Frontend Example**: `DFLOW_FRONTEND_EXAMPLE.jsx`
- **DFlow API**: https://pond.dflow.net/introduction
- **DFlow Grants**: https://www.dflow.net/grants
- **Solana Explorer**: https://explorer.solana.com/

## Support

Need help? Check:
1. Health endpoint: `GET /api/v1/dflow/health`
2. API logs: `backend/logs/`
3. DFlow Discord: https://discord.gg/dflow
4. Integration Guide: `DFLOW_INTEGRATION_GUIDE.md`

---

**Built with ❤️ using DFlow's Prediction Markets API**

Launch date: December 1, 2025
