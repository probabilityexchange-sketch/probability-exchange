# Prediction Markets Dashboard - Production Deployment Guide

## 🚀 Quick Start

### Option 1: Direct Launch (Fastest)
```bash
# Linux/macOS
./launch_dashboard.sh

# Windows
launch_dashboard.bat

# Manual
pip install -r requirements.txt
streamlit run standalone_prediction_dashboard.py
```

### Option 2: Docker (Recommended for Production)
```bash
# Build and run
docker-compose up --build

# Or with Docker directly
docker build -t prediction-dashboard .
docker run -p 8501:8501 prediction-dashboard
```

### Option 3: Virtual Environment (Development)
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
streamlit run standalone_prediction_dashboard.py --server.port 8501
```

## 📋 Production Deployment Options

### 1. Local Development Server
- **Use case**: Development, testing, demos
- **Command**: `./launch_dashboard.sh`
- **URL**: http://localhost:8501
- **Pros**: Quick setup, full features
- **Cons**: Single user, not scalable

### 2. Docker Container
- **Use case**: Production, cloud deployment
- **Command**: `docker-compose up -d`
- **URL**: http://localhost:8501
- **Pros**: Isolated, scalable, reproducible
- **Cons**: Requires Docker

### 3. Cloud Deployment (Streamlit Cloud)
1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy `standalone_prediction_dashboard.py`
4. **URL**: `https://your-app.streamlit.app`

### 4. VPS/Server Deployment
```bash
# Install system dependencies
sudo apt update && sudo apt install python3 python3-pip

# Clone and deploy
git clone <your-repo>
cd prediction-markets-dashboard
pip install -r requirements.txt

# Run with process manager (pm2/systemd)
pm2 start "streamlit run standalone_prediction_dashboard.py --server.port 8501" --name dashboard

# Or with systemd service
sudo cp dashboard.service /etc/systemd/system/
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

## ⚙️ Configuration

### Environment Variables
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Streamlit Configuration (~/.streamlit/config.toml)
```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 🔒 Security & Production Considerations

### 1. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2. HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. API Keys & Secrets
- Store API keys in environment variables
- Use `.env` file for development
- Never commit secrets to version control

```bash
# .env (development only)
POLYMARKET_API_KEY=your_key_here
KALSHI_API_KEY=your_key_here
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
- **URL**: `http://localhost:8501/_stcore/health`
- **Response**: HTTP 200 if healthy

### Log Monitoring
```bash
# Docker logs
docker-compose logs -f dashboard

# Local logs
tail -f ~/.streamlit/logs/streamlit.log
```

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -ti:8501 | xargs kill -9
```

**Dependencies issues:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Permission denied (Linux):**
```bash
chmod +x launch_dashboard.sh
```

**Docker build fails:**
```bash
docker system prune -a
docker-compose build --no-cache
```

## 📈 Performance Optimization

### 1. Caching
- Dashboard uses `@st.cache_data` for API calls
- Default TTL: 300 seconds (5 minutes)
- Adjust in code if needed

### 2. Resource Limits (Docker)
```yaml
services:
  dashboard:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### 3. Load Balancing
For high traffic, use multiple instances with a load balancer:
```bash
docker-compose up --scale dashboard=3
```

## 🚦 CI/CD Pipeline

### GitHub Actions (Optional)
```yaml
name: Deploy Dashboard
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Push
        run: |
          docker build -t prediction-dashboard .
          docker push your-registry/prediction-dashboard
```

## 📱 Mobile & Responsive
- Dashboard is mobile-responsive by default
- Optimized for tablets and phones
- Charts adapt to screen size

## 🎯 Validation
Before deployment, always run:
```bash
python validate_dashboard.py
```

This validates all core functionality without requiring Streamlit.

## 📞 Support
- Check logs for errors
- Validate with `validate_dashboard.py`
- Ensure all dependencies are installed
- Test with minimal configuration first