@echo off
REM probex.markets Dashboard Launcher - Windows
REM Launches the new probex.markets terminal-style dashboard

echo.
echo ============================================
echo   probex.markets Terminal Dashboard
echo   Dark Mode Prediction Markets Analysis
echo ============================================
echo.

REM Check if virtual environment exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Installing dependencies...
    pip install -r requirements.txt
)

REM Install/update dependencies if needed
pip install streamlit plotly pandas numpy aiohttp python-dateutil --quiet

REM Launch the new probex dashboard
echo Launching probex.markets dashboard...
echo Dashboard will be available at: http://localhost:8501
echo.

streamlit run probex_dashboard.py --server.port 8501

pause