#!/usr/bin/env python3
"""
Probex Consensus Dashboard Launcher

Simple script to launch the consensus dashboard with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Set up environment variables"""
    # Check for API keys
    api_keys = {
        'POLYMARKET_API_KEY': os.getenv('POLYMARKET_API_KEY'),
        'KALSHI_API_KEY': os.getenv('KALSHI_API_KEY'),
        'MANIFOLD_API_KEY': os.getenv('MANIFOLD_API_KEY')
    }
    
    print("🔑 API Key Status:")
    for key, value in api_keys.items():
        if value:
            print(f"   ✅ {key}: Set")
        else:
            print(f"   ⚠️  {key}: Not set (using simulated data)")
    
    # Set environment
    environment = os.getenv('ENVIRONMENT', 'development')
    print(f"🌍 Environment: {environment}")
    
    return environment

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'cache', 
        'exports',
        'data'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Directory: {directory} (ready)")

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n🚀 Launching Probex Consensus Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("\n" + "="*50)
    
    try:
        # Launch streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: Streamlit not found")
        print("💡 Install with: pip install streamlit")
        sys.exit(1)

def main():
    """Main launcher function"""
    print("🎯 Probex Consensus Dashboard Launcher")
    print("="*50)
    
    # Check requirements
    check_python_version()
    
    if not check_dependencies():
        sys.exit(1)
    
    # Setup
    environment = setup_environment()
    create_directories()
    
    # Development mode specific checks
    if environment == 'development':
        print("🛠️  Development mode detected")
        print("   - Using simulated data for missing API keys")
        print("   - Faster refresh intervals enabled")
        print("   - Debug logging enabled")
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()