# Complete Deployment Guide - DFlow Solana Integration

Step-by-step guide to deploy your MarketPulse Pro dashboard with DFlow Solana prediction markets.

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 18+ and npm installed
- Git installed
- A code editor (VS Code recommended)
- Phantom or Solflare wallet (for testing)

## 🚀 Quick Start (5 Minutes)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install base58 pynacl aiohttp structlog pydantic-settings fastapi uvicorn

# Or use requirements file
pip install -r requirements_dflow.txt

# Create .env file
cat > .env << 'EOF'
# DFlow API Configuration
DFLOW_API_KEY=
DFLOW_BASE_URL=https://pond.dflow.net/api
DFLOW_RATE_LIMIT=100

# Solana Wallet Configuration
SOLANA_WALLET_SECRET_KEY=$(openssl rand -hex 32)

# Database (if needed)
DATABASE_URL=sqlite:///./marketpulse.db

# API Settings
DEBUG=True
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF

# Test DFlow client
python dflow_client.py

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to dashboard directory
cd market-pulse-dashboard

# Install dependencies (including DFlow)
./install-dflow-deps.sh

# Or manually:
npm install --save \
  @solana/wallet-adapter-base \
  @solana/wallet-adapter-react \
  @solana/wallet-adapter-react-ui \
  @solana/wallet-adapter-wallets \
  @solana/wallet-adapter-phantom \
  @solana/wallet-adapter-solflare \
  @solana/web3.js \
  bs58

# Create .env file
cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
EOF

# Update main.tsx to use DFlow-enabled app
```

**Update `src/main.tsx`:**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import AppWithDFlow from './AppWithDFlow.tsx'  // Changed from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWithDFlow />
  </React.StrictMode>,
)
```

```bash
# Start the development server
npm run dev
```

Dashboard will be running at: `http://localhost:5173`

## 🧪 Testing the Integration

### 1. Test Backend Health

```bash
# Check main API
curl http://localhost:8000/health

# Check DFlow integration
curl http://localhost:8000/api/v1/dflow/health

# Get DFlow markets
curl http://localhost:8000/api/v1/dflow/markets?limit=5

# Get available tokens
curl http://localhost:8000/api/v1/dflow/tokens
```

### 2. Test Frontend

1. Open `http://localhost:5173` in your browser
2. Click "Solana Trading" tab
3. Click "Connect Wallet"
4. Approve connection in Phantom/Solflare
5. Browse markets
6. Try a test trade (use small amounts on devnet!)

### 3. Wallet Authentication Flow

```bash
# Test authentication (replace with your wallet address)
WALLET_ADDRESS="YourSolanaAddressHere"

# 1. Get challenge
curl -X POST http://localhost:8000/api/v1/dflow/auth/solana/challenge \
  -H "Content-Type: application/json" \
  -d "{\"wallet_address\": \"$WALLET_ADDRESS\"}"

# 2. Sign challenge in wallet
# 3. Verify signature (use signed message)
curl -X POST http://localhost:8000/api/v1/dflow/auth/solana/verify \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "'$WALLET_ADDRESS'",
    "challenge": "Challenge message from step 1",
    "signature": "Signed message from wallet"
  }'
```

## 📦 Production Deployment

### Backend Deployment (Railway/Render/DigitalOcean)

**Option 1: Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Add environment variables in Railway dashboard:
# - DFLOW_API_KEY
# - SOLANA_WALLET_SECRET_KEY
# - DATABASE_URL
# - CORS_ORIGINS

# Deploy
railway up
```

**Option 2: Docker**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_dflow.txt .
RUN pip install --no-cache-dir -r requirements_dflow.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t marketpulse-backend .
docker run -p 8000:8000 --env-file .env marketpulse-backend
```

### Frontend Deployment (Vercel/Netlify)

**Option 1: Vercel**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd market-pulse-dashboard
vercel

# Set environment variables in Vercel dashboard:
# - VITE_API_BASE_URL (your backend URL)
# - VITE_SOLANA_RPC_URL
```

**Option 2: Netlify**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist

# Set environment variables in Netlify dashboard
```

**vercel.json** (if using Vercel):

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,POST,PUT,DELETE,OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization" }
      ]
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

**Backend (`.env`):**

```bash
# Required
SOLANA_WALLET_SECRET_KEY=your_secure_random_key

# Optional
DFLOW_API_KEY=your_dflow_api_key
DFLOW_BASE_URL=https://pond.dflow.net/api
DFLOW_RATE_LIMIT=100

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# API Settings
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com"]

# Logging
LOG_LEVEL=INFO
```

**Frontend (`.env`):**

```bash
# Required
VITE_API_BASE_URL=https://your-backend-api.com/api/v1

# Optional
VITE_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
VITE_ENABLE_ANALYTICS=true
```

### Solana Network Configuration

For testing, use devnet:

```typescript
// src/components/SolanaWalletProvider.tsx
const network: WalletAdapterNetwork = 'devnet'; // Change to 'mainnet-beta' for production
```

Get devnet SOL from: https://faucet.solana.com/

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found: @solana/wallet-adapter-react"**

```bash
cd market-pulse-dashboard
npm install --save @solana/wallet-adapter-react @solana/wallet-adapter-react-ui @solana/wallet-adapter-wallets @solana/web3.js bs58
```

**2. "Failed to connect to backend API"**

- Check backend is running: `curl http://localhost:8000/health`
- Verify CORS settings in backend `.env`
- Check frontend `.env` has correct `VITE_API_BASE_URL`

**3. "Authentication failed"**

- Ensure wallet is connected
- Check signature encoding (should be base58)
- Verify challenge message matches exactly

**4. Backend import errors**

```bash
cd backend
pip install base58 pynacl aiohttp
```

**5. Wallet not connecting**

- Clear browser cache
- Try different wallet (Phantom vs Solflare)
- Check browser console for errors
- Ensure wallet extension is up to date

### Debug Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Environment variables set correctly
- [ ] DFlow health check passes
- [ ] Wallet extension installed
- [ ] Network matches (devnet/mainnet)

## 📊 Monitoring

### Backend Logs

```bash
# View logs
tail -f backend/logs/app.log

# Check DFlow API calls
grep "DFlow" backend/logs/app.log
```

### Frontend Console

Open browser DevTools (F12) and check:
- Network tab for API calls
- Console tab for errors
- Application tab for wallet connection

## 🔐 Security Best Practices

1. **Never commit `.env` files**
2. **Use strong random keys** for `SOLANA_WALLET_SECRET_KEY`
3. **Enable HTTPS** in production
4. **Set proper CORS origins**
5. **Use environment-specific RPC endpoints**
6. **Implement rate limiting**
7. **Monitor API usage**
8. **Keep dependencies updated**

## 📚 Additional Resources

- **DFlow Documentation**: https://pond.dflow.net/introduction
- **Solana Wallet Adapter**: https://github.com/solana-labs/wallet-adapter
- **Phantom Wallet**: https://phantom.app/
- **Solana Explorer**: https://explorer.solana.com/

## 🆘 Support

- Backend issues: Check `backend/logs/`
- Frontend issues: Browser DevTools console
- DFlow API: https://discord.gg/dflow
- Project issues: See integration guides

## 🎉 Success Checklist

- [ ] Backend running and healthy
- [ ] Frontend loads without errors
- [ ] Wallet connects successfully
- [ ] Markets display correctly
- [ ] Authentication works
- [ ] Can view quote
- [ ] Portfolio loads
- [ ] All tests pass

## Next Steps

1. Customize the UI colors/branding
2. Add more market filters
3. Implement advanced trading features
4. Add portfolio analytics
5. Set up monitoring and alerts
6. Apply for DFlow grants ($2M available)

---

**🚀 You're now ready to trade prediction markets on Solana!**

For detailed API documentation, see `DFLOW_INTEGRATION_GUIDE.md`
