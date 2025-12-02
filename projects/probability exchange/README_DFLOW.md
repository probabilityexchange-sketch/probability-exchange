# 🚀 MarketPulse Pro + DFlow Solana Integration

Your prediction markets dashboard now supports **tokenized Kalshi markets on Solana** via DFlow!

## ✨ What's New

- **Solana Trading**: Trade tokenized prediction markets on Solana blockchain
- **Wallet Integration**: Connect Phantom or Solflare wallets
- **Real-time Positions**: Track your portfolio with live P&L
- **Dual Swap Modes**: Choose imperative (precise) or declarative (optimized) trading
- **Deep Liquidity**: Access Kalshi's institutional-grade markets

## 🎯 Quick Start (< 2 Minutes)

### Option 1: Automated Deploy (Recommended)

```bash
./deploy-dflow-dashboard.sh
```

This script will:
- ✅ Install all dependencies
- ✅ Configure environment variables
- ✅ Start backend on port 8000
- ✅ Start frontend on port 5173
- ✅ Verify everything works

### Option 2: Manual Setup

```bash
# 1. Backend
cd backend
pip install base58 pynacl aiohttp
uvicorn app.main:app --reload

# 2. Frontend
cd market-pulse-dashboard
./install-dflow-deps.sh
npm run dev

# 3. Update main.tsx import:
# Change: import App from './App.tsx'
# To: import AppWithDFlow from './AppWithDFlow.tsx'
```

## 📖 Documentation

- **`DEPLOYMENT_GUIDE.md`** - Complete deployment instructions
- **`DFLOW_INTEGRATION_GUIDE.md`** - Detailed API integration guide
- **`DFLOW_QUICK_START.md`** - 5-minute quick start guide

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  React Dashboard (Port 5173)        │
│  • Tailwind CSS                     │
│  • TypeScript                       │
│  • Solana Wallet Adapter            │
└─────────────┬───────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│  FastAPI Backend (Port 8000)        │
│  • DFlow API Client                 │
│  • Solana Authentication            │
│  • Real-time WebSockets             │
└─────────────┬───────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│  DFlow API (pond.dflow.net)         │
│  • Tokenized Kalshi Markets         │
│  • Solana SPL Tokens                │
│  • Concurrent Liquidity Programs    │
└─────────────────────────────────────┘
```

## 📁 New Files Created

### Backend
- `backend/dflow_client.py` - DFlow API client
- `backend/solana_wallet.py` - Solana wallet manager
- `backend/app/api/v1/dflow_trading.py` - Trading API routes
- `backend/requirements_dflow.txt` - Dependencies

### Frontend
- `src/lib/dflow-api-client.ts` - Frontend API client
- `src/components/DFlowTradingPanel.tsx` - Main trading UI
- `src/components/SolanaWalletProvider.tsx` - Wallet provider
- `src/AppWithDFlow.tsx` - Enhanced app with DFlow

### Scripts & Docs
- `deploy-dflow-dashboard.sh` - One-command deployment
- `setup_dflow.sh` - Backend setup script
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `DFLOW_INTEGRATION_GUIDE.md` - API integration docs
- `DFLOW_QUICK_START.md` - Quick reference

## 🎮 How to Use

1. **Open Dashboard**: http://localhost:5173
2. **Switch to Solana Trading**: Click "Solana Trading" tab
3. **Connect Wallet**: Click "Connect Wallet" button
4. **Authenticate**: Sign the challenge message in your wallet
5. **Browse Markets**: Explore tokenized Kalshi markets
6. **Trade**: Select a market, choose YES/NO, enter amount, execute
7. **Track Portfolio**: View your positions and P&L

## 🔧 Configuration

### Backend `.env`
```bash
DFLOW_API_KEY=              # Optional
DFLOW_BASE_URL=https://pond.dflow.net/api
SOLANA_WALLET_SECRET_KEY=your_random_key
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend `.env`
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

## 🧪 Testing

```bash
# Backend health
curl http://localhost:8000/api/v1/dflow/health

# Get markets
curl http://localhost:8000/api/v1/dflow/markets?limit=5

# Get tokens
curl http://localhost:8000/api/v1/dflow/tokens
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
cd market-pulse-dashboard
npm install
```

### Backend won't start
```bash
cd backend
pip install -r requirements_dflow.txt
```

### Wallet won't connect
1. Install Phantom or Solflare extension
2. Check network (mainnet vs devnet)
3. Clear browser cache
4. Check console for errors

### API connection fails
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend `.env`
3. Verify frontend `.env` has correct API URL

## 📊 Features

### Markets
- ✅ Browse tokenized Kalshi markets
- ✅ Search and filter by category
- ✅ Real-time price updates
- ✅ 24h volume and liquidity data

### Trading
- ✅ Get instant swap quotes
- ✅ Imperative mode (precise control)
- ✅ Declarative mode (optimized execution)
- ✅ Slippage protection
- ✅ Transaction signing via wallet

### Portfolio
- ✅ View all positions
- ✅ Real-time P&L tracking
- ✅ Position details and history
- ✅ Wallet balance display

## 🌟 What Makes This Special?

1. **True Onchain Ownership**: Your positions are actual Solana SPL tokens
2. **DeFi Compatible**: Use positions as collateral in other protocols
3. **Deep Liquidity**: Access Kalshi's institutional markets
4. **Modern UX**: Beautiful, fast React dashboard with Tailwind
5. **Production Ready**: Built with TypeScript, FastAPI, proper error handling

## 💡 Tips

- Start with small amounts on devnet first
- Use declarative mode for better slippage protection
- Keep some SOL for transaction fees
- Check positions regularly in portfolio view
- Monitor gas fees during network congestion

## 🆘 Support

- **Backend Issues**: Check `/tmp/backend.log`
- **Frontend Issues**: Browser DevTools console (F12)
- **DFlow API**: https://discord.gg/dflow
- **Solana**: https://solana.com/developers

## 🎓 Learn More

- **DFlow Docs**: https://pond.dflow.net/introduction
- **DFlow Grants**: $2M available - https://www.dflow.net/grants
- **Solana Wallets**: https://github.com/solana-labs/wallet-adapter
- **Kalshi**: https://kalshi.com/

## 📈 Roadmap

- [ ] Advanced charting for market prices
- [ ] Limit orders and order book
- [ ] Portfolio analytics dashboard
- [ ] Mobile responsive improvements
- [ ] Transaction history export
- [ ] Multi-wallet support
- [ ] Social features (leaderboards, sharing)

## 🤝 Contributing

This integration is open for improvements:
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using:**
- [DFlow](https://dflow.net/) - Prediction Markets on Solana
- [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Solana](https://solana.com/)

**Integration Date**: December 2, 2025
**DFlow Launch**: December 1, 2025

🚀 **Happy Trading on Solana!**
