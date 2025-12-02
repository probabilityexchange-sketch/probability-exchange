#!/bin/bash

###############################################################################
# DFlow Solana Integration Setup Script
###############################################################################

echo "========================================="
echo "DFlow Solana Integration Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "DFLOW_INTEGRATION_GUIDE.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo "Step 1: Installing Python dependencies..."
echo "----------------------------------------"

cd backend

# Install required Python packages
pip3 install base58 pynacl aiohttp structlog pydantic-settings || {
    echo -e "${RED}Failed to install Python dependencies${NC}"
    exit 1
}

echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo "Step 2: Setting up environment variables..."
echo "--------------------------------------------"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# DFlow API Configuration
DFLOW_API_KEY=
DFLOW_BASE_URL=https://pond.dflow.net/api
DFLOW_RATE_LIMIT=100

# Solana Wallet Configuration
SOLANA_WALLET_SECRET_KEY=your_secure_secret_key_here

# Other API Keys (if needed)
POLYMARKET_API_KEY=
KALSHI_API_KEY=
KALSHI_SECRET_KEY=
MANIFOLD_API_KEY=
NEWS_API_KEY=
EOF
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your API keys${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists. Checking for DFlow variables...${NC}"

    # Check if DFlow variables exist
    if ! grep -q "DFLOW_API_KEY" .env; then
        echo "" >> .env
        echo "# DFlow API Configuration" >> .env
        echo "DFLOW_API_KEY=" >> .env
        echo "DFLOW_BASE_URL=https://pond.dflow.net/api" >> .env
        echo "DFLOW_RATE_LIMIT=100" >> .env
        echo "" >> .env
        echo "# Solana Wallet Configuration" >> .env
        echo "SOLANA_WALLET_SECRET_KEY=your_secure_secret_key_here" >> .env
        echo -e "${GREEN}✓ Added DFlow variables to .env${NC}"
    else
        echo -e "${GREEN}✓ DFlow variables already present in .env${NC}"
    fi
fi

echo ""

echo "Step 3: Testing DFlow client..."
echo "--------------------------------"

# Test DFlow client
python3 dflow_client.py || {
    echo -e "${YELLOW}⚠ DFlow client test completed (may show warnings if API key not configured)${NC}"
}

echo ""

echo "Step 4: Testing Solana wallet manager..."
echo "------------------------------------------"

# Test Solana wallet
python3 solana_wallet.py || {
    echo -e "${YELLOW}⚠ Solana wallet test completed${NC}"
}

echo ""

cd ..

echo "Step 5: Frontend setup (optional)..."
echo "--------------------------------------"

read -p "Do you want to set up the frontend with Solana wallet support? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing frontend dependencies..."

    # Check if package.json exists
    if [ -f "market-pulse-dashboard/package.json" ]; then
        cd market-pulse-dashboard

        # Install Solana wallet adapter packages
        npm install --save \
            @solana/wallet-adapter-react \
            @solana/wallet-adapter-react-ui \
            @solana/wallet-adapter-wallets \
            @solana/wallet-adapter-phantom \
            @solana/wallet-adapter-solflare \
            @solana/web3.js \
            bs58 || {
            echo -e "${RED}Failed to install frontend dependencies${NC}"
            exit 1
        }

        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

        cd ..
    else
        echo -e "${YELLOW}⚠ Frontend directory not found. Skipping...${NC}"
    fi
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Edit backend/.env and add your API keys"
echo "2. Review DFLOW_INTEGRATION_GUIDE.md for detailed instructions"
echo "3. Check DFLOW_FRONTEND_EXAMPLE.jsx for frontend integration"
echo "4. Start your backend: cd backend && uvicorn app.main:app --reload"
echo "5. Test the integration: curl http://localhost:8000/api/v1/dflow/health"
echo ""
echo "Resources:"
echo "- DFlow Documentation: https://pond.dflow.net/introduction"
echo "- Integration Guide: ./DFLOW_INTEGRATION_GUIDE.md"
echo "- Frontend Example: ./DFLOW_FRONTEND_EXAMPLE.jsx"
echo ""
echo -e "${GREEN}Happy trading on Solana! 🚀${NC}"
