#!/bin/bash
# MarketPulse Pro - Full Stack Launcher
# Starts Backend (FastAPI) and Frontend (React/Vite)

# Get the directory where the script is located
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/market-pulse-dashboard"

# Log files
BACKEND_LOG="/tmp/probex_backend.log"
FRONTEND_LOG="/tmp/probex_frontend.log"

echo "==========================================="
echo "   MarketPulse Pro - Launch System"
echo "==========================================="
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."

    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi

    # Also ensure we kill by port/search just in case
    pkill -f "uvicorn app.main:app"

    echo "✅ Shutdown complete."
    exit 0
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# ---------------------------------------------------------
# Backend Setup & Launch
# ---------------------------------------------------------
echo "🔧 Setting up Backend..."

cd "$BACKEND_DIR" || { echo "❌ Backend directory not found!"; exit 1; }

# Create/Activate venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
fi

# Start Backend
echo "🚀 Starting Backend Service..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "   Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# ---------------------------------------------------------
# Frontend Setup & Launch
# ---------------------------------------------------------
echo ""
echo "🔧 Setting up Frontend..."

cd "$FRONTEND_DIR" || { echo "❌ Frontend directory not found!"; exit 1; }

# Install dependencies if node_modules is missing
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

# Start Frontend
echo "🚀 Starting Frontend Dashboard..."
npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend running (PID: $FRONTEND_PID)"

# ---------------------------------------------------------
# Monitoring
# ---------------------------------------------------------
echo ""
echo "✅ System Operational!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173 (usually)"
echo ""
echo "📝 Logs available at:"
echo "   $BACKEND_LOG"
echo "   $FRONTEND_LOG"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait indefinitely
wait
