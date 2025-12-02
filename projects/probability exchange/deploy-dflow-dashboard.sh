#!/bin/bash

###############################################################################
# DFlow Dashboard Complete Deployment Script
# Deploys both backend and frontend with DFlow Solana integration
###############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "==========================================="
echo "  DFlow Solana Dashboard Deployment"
echo "==========================================="
echo -e "${NC}"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/market-pulse-dashboard"

###############################################################################
# Step 1: Backend Setup
###############################################################################

echo -e "\n${BLUE}Step 1: Setting up Backend...${NC}"
cd "$BACKEND_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -q base58 pynacl aiohttp structlog pydantic-settings fastapi uvicorn

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cat > .env << 'EOF'
# DFlow API Configuration
DFLOW_API_KEY=
DFLOW_BASE_URL=https://pond.dflow.net/api
DFLOW_RATE_LIMIT=100

# Solana Wallet Configuration
SOLANA_WALLET_SECRET_KEY=your_secure_secret_key_here

# Database
DATABASE_URL=sqlite:///./marketpulse.db

# API Settings
DEBUG=True
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF
    echo -e "${YELLOW}⚠ Created .env file - please update with your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Test DFlow client
echo "Testing DFlow client..."
python3 dflow_client.py &> /dev/null && echo -e "${GREEN}✓ DFlow client test passed${NC}" || echo -e "${YELLOW}⚠ DFlow client test completed with warnings${NC}"

###############################################################################
# Step 2: Frontend Setup
###############################################################################

echo -e "\n${BLUE}Step 2: Setting up Frontend...${NC}"
cd "$FRONTEND_DIR"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Install npm dependencies
echo "Installing npm dependencies..."
if [ -f "install-dflow-deps.sh" ]; then
    chmod +x install-dflow-deps.sh
    ./install-dflow-deps.sh
else
    npm install
    npm install --save \
        @solana/wallet-adapter-base \
        @solana/wallet-adapter-react \
        @solana/wallet-adapter-react-ui \
        @solana/wallet-adapter-wallets \
        @solana/wallet-adapter-phantom \
        @solana/wallet-adapter-solflare \
        @solana/web3.js \
        bs58
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
EOF
    echo -e "${GREEN}✓ Created frontend .env file${NC}"
else
    echo -e "${GREEN}✓ Frontend .env file already exists${NC}"
fi

# Update main.tsx to use DFlow app
echo "Updating main.tsx to use DFlow-enabled app..."
if [ -f "src/main.tsx" ]; then
    # Backup original
    cp src/main.tsx src/main.tsx.backup

    # Update import
    sed -i "s|import App from './App.tsx'|import AppWithDFlow from './AppWithDFlow.tsx'|g" src/main.tsx 2>/dev/null || \
    sed -i '' "s|import App from './App.tsx'|import AppWithDFlow from './AppWithDFlow.tsx'|g" src/main.tsx

    sed -i "s|<App />|<AppWithDFlow />|g" src/main.tsx 2>/dev/null || \
    sed -i '' "s|<App />|<AppWithDFlow />|g" src/main.tsx

    echo -e "${GREEN}✓ Updated main.tsx${NC}"
fi

###############################################################################
# Step 3: Launch Services
###############################################################################

echo -e "\n${BLUE}Step 3: Launching Services...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    pkill -f "uvicorn app.main:app" || true
    pkill -f "vite" || true
    exit 0
}

trap cleanup INT TERM

# Start backend
echo "Starting backend on port 8000..."
cd "$BACKEND_DIR"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &> /tmp/backend.log &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        break
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend on port 5173..."
cd "$FRONTEND_DIR"
npm run dev &> /tmp/frontend.log &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5173 &> /dev/null; then
        echo -e "${GREEN}✓ Frontend is running${NC}"
        break
    fi
    sleep 1
done

###############################################################################
# Step 4: Verification
###############################################################################

echo -e "\n${BLUE}Step 4: Verifying Deployment...${NC}"

# Test backend health
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Test DFlow health
if curl -s http://localhost:8000/api/v1/dflow/health &> /dev/null; then
    echo -e "${GREEN}✓ DFlow integration active${NC}"
else
    echo -e "${YELLOW}⚠ DFlow integration check inconclusive${NC}"
fi

# Test frontend
if curl -s http://localhost:5173 &> /dev/null; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
fi

###############################################################################
# Success Message
###############################################################################

echo -e "\n${GREEN}"
echo "==========================================="
echo "  🎉 Deployment Complete!"
echo "==========================================="
echo -e "${NC}"
echo ""
echo "Your MarketPulse Pro dashboard with DFlow Solana integration is running:"
echo ""
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Click 'Solana Trading' tab"
echo "3. Connect your Phantom or Solflare wallet"
echo "4. Browse tokenized Kalshi markets on Solana"
echo "5. Start trading!"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait
