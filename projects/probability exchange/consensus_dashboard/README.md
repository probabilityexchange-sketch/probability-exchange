# Probex Consensus Dashboard

🎯 **Cross-Platform Prediction Market Consensus Intelligence**

Real-time aggregation and analysis of prediction markets across Polymarket, Kalshi, and Manifold to provide actionable consensus insights.

## 🚀 Key Features

### 📊 Real-time Consensus Analysis
- **Multi-platform aggregation** from Polymarket, Kalshi, and Manifold
- **Consensus scoring** with confidence levels and risk assessment
- **Signal detection** for high-confidence trading opportunities
- **Cross-platform comparison** to identify market inefficiencies

### 🎯 Signal Detection
- **Enhanced prediction signals** with volume-weighted scoring
- **Momentum tracking** to identify trending markets
- **Volatility analysis** for risk assessment
- **Risk-adjusted returns** for informed decision making

### ⚠️ Risk Assessment
- **Overall risk level** evaluation across all signals
- **Risk factor identification** with mitigation suggestions
- **Concentration risk** analysis for platform diversification
- **Volatility monitoring** for market stability

### 📈 Historical Analysis
- **Consensus trends** over time
- **Accuracy tracking** for signal performance
- **Performance metrics** for strategy evaluation
- **Export capabilities** for further analysis

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip or conda package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd consensus_dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   export POLYMARKET_API_KEY="your_polymarket_api_key"
   export KALSHI_API_KEY="your_kalshi_api_key"
   export MANIFOLD_API_KEY="your_manifold_api_key"
   export ENVIRONMENT="development"  # or "production"
   ```

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

### Docker Setup (Optional)

```bash
# Build the image
docker build -t probex-consensus-dashboard .

# Run the container
docker run -p 8501:8501 \
  -e POLYMARKET_API_KEY="your_key" \
  -e KALSHI_API_KEY="your_key" \
  -e MANIFOLD_API_KEY="your_key" \
  probex-consensus-dashboard
```

## 📋 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POLYMARKET_API_KEY` | Polymarket API key | `""` |
| `KALSHI_API_KEY` | Kalshi API key | `""` |
| `MANIFOLD_API_KEY` | Manifold API key | `""` |
| `ENVIRONMENT` | Environment (development/production) | `development` |

### Configuration Options

The dashboard can be configured through:

- **Sidebar controls**: Real-time adjustment of filters and thresholds
- **Configuration file**: `config.py` for advanced settings
- **Environment variables**: For deployment and API keys

## 🎮 Using the Dashboard

### Main Views

1. **Real-time Consensus**: Live consensus analysis with top signals
2. **Historical Analysis**: Trends and performance over time
3. **Signal Detection**: Detailed signal breakdown and filtering
4. **Risk Assessment**: Comprehensive risk evaluation

### Key Metrics

- **Consensus Score**: Agreement level across platforms (0-100%)
- **Confidence Score**: Signal reliability (0-100%)
- **Signal Strength**: Strong/Moderate/Weak classification
- **Risk-Adjusted Return**: Expected return adjusted for risk

### Filtering Options

- **Data Sources**: Select platforms to include
- **Consensus Threshold**: Minimum consensus score (50-100%)
- **Minimum Confidence**: Filter by confidence level (0-100%)
- **Categories**: Focus on specific market categories

## 🔧 Development

### Project Structure

```
consensus_dashboard/
├── app.py                 # Main dashboard application
├── config.py              # Configuration management
├── requirements.txt         # Python dependencies
├── README.md              # This file
├── Dockerfile             # Docker configuration (optional)
└── tests/                 # Test suite (optional)
```

### Adding New Features

1. **New Data Sources**: Extend `RealAPIManager` class
2. **Custom Metrics**: Add to `EnhancedPredictionMarketsIntegration`
3. **UI Components**: Modify `ConsensusDashboard` class
4. **Configuration**: Update `config.py` settings

### Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=consensus_dashboard tests/
```

## 📊 Data Sources

### Supported Platforms

1. **Polymarket**
   - Binary prediction markets
   - Political and economic events
   - High liquidity markets

2. **Kalshi**
   - Regulated prediction markets
   - Economic and financial events
   - US-focused markets

3. **Manifold**
   - Community-driven predictions
   - Technology and culture events
   - Diverse market types

### Data Processing

- **Real-time fetching** with rate limiting
- **Cross-platform matching** using similarity algorithms
- **Consensus calculation** with volume weighting
- **Risk assessment** using multiple factors

## 🚀 Deployment

### Streamlit Cloud

```bash
# Install Streamlit CLI
pip install streamlit

# Deploy
streamlit run app.py
streamlit deploy
```

### Docker Deployment

```bash
# Build and run
docker build -t probex-consensus .
docker run -p 8501:8501 probex-consensus
```

### Cloud Platforms

- **Heroku**: Easy deployment with PostgreSQL
- **AWS**: Scalable deployment with ECS
- **Google Cloud**: Container deployment on GKE
- **Azure**: App Service with container support

## 🔒 Security & Privacy

- **API Key Protection**: Environment variables for sensitive data
- **Rate Limiting**: Respect platform API limits
- **Data Encryption**: Secure data transmission
- **No Personal Data**: Only public market information

## 📈 Performance

### Optimization Features

- **Caching**: Reduce API calls with intelligent caching
- **Async Processing**: Non-blocking data fetching
- **Rate Limiting**: Respect platform constraints
- **Lazy Loading**: Load data on demand

### Monitoring

- **Response Times**: Track API performance
- **Error Rates**: Monitor failure rates
- **Cache Hit Rates**: Optimize caching strategy
- **User Metrics**: Track dashboard usage

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes**: Add tests for new features
4. **Run tests**: Ensure all tests pass
5. **Submit PR**: Describe changes and benefits

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Type Hints**: Use type annotations
- **Documentation**: Include docstrings
- **Testing**: Maintain test coverage >80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact support@probex.markets

### Common Issues

1. **API Keys**: Ensure environment variables are set
2. **Rate Limits**: Check platform API documentation
3. **Dependencies**: Verify all requirements are installed
4. **Network**: Check internet connection for API calls

---

**🎯 Probex Consensus Dashboard** - Your intelligent cross-platform prediction market analysis tool.

*Built with ❤️ for the prediction markets community*