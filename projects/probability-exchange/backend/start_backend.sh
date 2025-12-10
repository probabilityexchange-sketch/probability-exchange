#!/bin/bash

# Market Pulse Pro Backend Startup Script

# Get the directory where the script is located
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/backend.log"

echo "==========================================="
echo "Market Pulse Pro Backend Startup"
echo "==========================================="
echo ""

# Check if backend is already running
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Backend is already running!"
    echo ""
    echo "Process info:"
    ps aux | grep "uvicorn app.main:app" | grep -v grep
    echo ""
    echo "To stop: pkill -f 'uvicorn app.main:app'"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR" || exit 1

# Start backend
echo "Starting backend on http://localhost:8000..."
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_FILE" 2>&1 &

# Wait for startup
echo "Waiting for backend to start..."
sleep 5

# Check if started successfully
if curl -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "✅ Backend started successfully!"
    echo ""
    echo "==========================================="
    echo "Backend Information"
    echo "==========================================="
    echo "URL: http://localhost:8000"
    echo "API: http://localhost:8000/api/v1"
    echo "Docs: http://localhost:8000/docs"
    echo "Logs: $LOG_FILE"
    echo ""
    echo "Health: $(curl -s http://localhost:8000/health)"
    echo ""
    echo "==========================================="
    echo "Useful Commands"
    echo "==========================================="
    echo "View logs: tail -f $LOG_FILE"
    echo "Stop backend: pkill -f 'uvicorn app.main:app'"
    echo "API docs: open http://localhost:8000/docs"
    echo ""
else
    echo ""
    echo "❌ Backend failed to start!"
    echo ""
    echo "Check logs for errors:"
    echo "tail -50 $LOG_FILE"
    exit 1
fi
