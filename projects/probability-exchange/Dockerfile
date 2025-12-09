# Prediction Markets Dashboard - Container Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dashboard files
COPY standalone_prediction_dashboard.py .
COPY prediction_markets_dashboard.py .
COPY validate_dashboard.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command - run standalone dashboard
CMD ["streamlit", "run", "standalone_prediction_dashboard.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]