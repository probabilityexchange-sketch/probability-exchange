#!/bin/bash
# probex.markets Dashboard Launcher - Linux/macOS
# Launches the new probex.markets terminal-style dashboard

echo ""
echo "============================================"
echo "   probex.markets Terminal Dashboard"
echo "   Dark Mode Prediction Markets Analysis"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Install/update dependencies if needed
pip install streamlit plotly pandas numpy aiohttp python-dateutil --quiet

# Launch the new probex dashboard
echo "Launching probex.markets dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
echo ""

streamlit run probex_dashboard.py --server.port 8501