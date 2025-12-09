#!/bin/bash

echo "==========================================="
echo "Installing DFlow Solana Dependencies"
echo "==========================================="
echo ""

# Navigate to the dashboard directory
cd "$(dirname "$0")"

echo "Installing Solana Wallet Adapter packages..."
npm install --save \
  @solana/wallet-adapter-base \
  @solana/wallet-adapter-react \
  @solana/wallet-adapter-react-ui \
  @solana/wallet-adapter-wallets \
  @solana/web3.js \
  bs58

echo ""
echo "Installing additional dependencies..."
npm install --save \
  @solana/wallet-adapter-phantom \
  @solana/wallet-adapter-solflare

echo ""
echo "✓ Dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd ../backend && uvicorn app.main:app --reload"
echo "2. Start the dashboard: npm run dev"
echo "3. Open http://localhost:5173"
