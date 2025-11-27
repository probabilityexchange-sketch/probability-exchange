#!/usr/bin/env python3
"""
Enhanced probex.markets Dashboard with News Integration

Terminal-style prediction markets dashboard with AI-powered news analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import logging
import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import news integration system
from news_integration import NewsIntegrationEngine, NewsArticle, NewsImpact

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for probex.markets theme with news integration enhancements
def load_probex_styles():
    st.markdown("""
    <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Root color variables */
        :root {
            --bg-dark: #0a0f16;
            --bg-surface: #141b26;
            --brand-blue: #00B3FF;
            --neon-cyan: #2EFFFA;
            --terminal-gray: #7a8a99;
            --text-white: #ffffff;
            --ui-red: #FF3366;
            --success-green: #00FF88;
            --warning-yellow: #FFC107;
        }
        
        /* Main application background */
        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                linear-gradient(rgba(46, 255, 250, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(46, 255, 250, 0.08) 1px, transparent 1px);
            background-size: 60px 60px;
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        .main-header {
            color: var(--text-white);
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 48px;
            margin-bottom: 1rem;
        }
        
        .main-subheader {
            color: var(--terminal-gray);
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            font-size: 18px;
            margin-bottom: 2rem;
        }
        
        /* Logo styling */
        .logo-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 2rem;
        }
        
        .logo-symbol {
            background-color: var(--brand-blue);
            color: var(--bg-dark);
            width: 80px;
            height: 80px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 32px;
            transform: skewY(-5deg);
        }
        
        .logo-text {
            color: var(--text-white);
        }
        
        .logo-text .bold {
            font-weight: 600;
        }
        
        .logo-text .light {
            font-weight: 400;
            color: var(--terminal-gray);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--bg-surface);
        }
        
        .css-1v3fvcr {
            background-color: var(--bg-surface);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--brand-blue);
            color: var(--bg-dark);
            border: none;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            height: 48px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: var(--neon-cyan);
            transform: translateY(-1px);
        }
        
        /* News-specific styling */
        .news-impact-positive {
            color: var(--success-green);
            font-weight: 600;
        }
        
        .news-impact-negative {
            color: var(--ui-red);
            font-weight: 600;
        }
        
        .news-impact-neutral {
            color: var(--warning-yellow);
            font-weight: 600;
        }
        
        .news-confidence-high {
            color: var(--neon-cyan);
            font-weight: 700;
        }
        
        .news-confidence-medium {
            color: var(--brand-blue);
            font-weight: 600;
        }
        
        .news-confidence-low {
            color: var(--terminal-gray);
            font-weight: 500;
        }
        
        .breaking-news {
            border-left: 4px solid var(--ui-red);
            padding-left: 12px;
            background-color: rgba(255, 51, 102, 0.1);
        }
        
        .high-impact-news {
            border-left: 4px solid var(--warning-yellow);
            padding-left: 12px;
            background-color: rgba(255, 193, 7, 0.1);
        }
        
        /* Probability displays */
        .probability-yes {
            color: var(--brand-blue);
            font-weight: 600;
        }
        
        .probability-no {
            color: var(--ui-red);
            font-weight: 600;
        }
        
        .high-confidence {
            color: var(--neon-cyan);
            font-weight: 600;
        }
        
        /* Terminal-style container */
        .terminal-container {
            background-color: var(--bg-surface);
            border: 2px solid var(--bg-surface);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        
        /* News feed container */
        .news-feed-container {
            background-color: var(--bg-surface);
            border: 2px solid var(--brand-blue);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            max-height: 600px;
            overflow-y: auto;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--bg-surface);
            border-radius: 8px 8px 0 0;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            color: var(--terminal-gray);
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--bg-dark) !important;
            color: var(--brand-blue) !important;
        }
        
        /* Metric styling */
        .stMetric {
            background-color: var(--bg-surface);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--brand-blue);
            border-opacity: 0.3;
        }
        
        .stMetric label {
            color: var(--terminal-gray);
            font-family: 'Inter', sans-serif;
            font-weight: 400;
        }
        
        .stMetric div {
            color: var(--text-white);
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        
        /* Success/Error message styling */
        .stSuccess {
            background-color: rgba(46, 255, 250, 0.1);
            color: var(--neon-cyan);
            border: 1px solid var(--neon-cyan);
        }
        
        .stError {
            background-color: rgba(255, 51, 102, 0.1);
            color: var(--ui-red);
            border: 1px solid var(--ui-red);
        }
        
        .stWarning {
            background-color: rgba(255, 193, 7, 0.1);
            color: var(--warning-yellow);
            border: 1px solid var(--warning-yellow);
        }
        
        .stInfo {
            background-color: rgba(0, 179, 255, 0.1);
            color: var(--brand-blue);
            border: 1px solid var(--brand-blue);
        }
    </style>
    """, unsafe_allow_html=True)

def create_enhanced_probex_dashboard():
    """Create the enhanced probex.markets dashboard with news integration"""
    
    # Load custom styles
    load_probex_styles()
    
    st.set_page_config(
        page_title="probex.markets",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header with logo
    header_html = """
    <div class="logo-container">
        <div class="logo-symbol">P(E)</div>
        <div class="logo-text">
            <span class="bold">probex</span><span class="light">.markets</span>
        </div>
    </div>
    <h1 class="main-header">AI-Powered Prediction Markets</h1>
    <p class="main-subheader">Real-time intelligence with news analysis • Terminal interface • Dark mode analytics</p>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Initialize session state for news integration
    if 'news_engine' not in st.session_state:
        st.session_state.news_engine = NewsIntegrationEngine()
    if 'news_articles' not in st.session_state:
        st.session_state.news_articles = []
    if 'news_impacts' not in st.session_state:
        st.session_state.news_impacts = []
    if 'news_last_update' not in st.session_state:
        st.session_state.news_last_update = None
    
    # Sidebar controls
    st.sidebar.header("🔧 Terminal Controls")
    
    # Data source selection
    data_sources = st.sidebar.multiselect(
        "Select Data Sources",
        ["Polymarket", "Kalshi", "Manifold"],
        default=["Polymarket", "Kalshi", "Manifold"]
    )
    
    # Categories filter
    categories = st.sidebar.multiselect(
        "Select Categories",
        ["politics", "economy", "technology", "sports", "entertainment", "weather", "health"],
        default=["economy", "technology", "politics"]
    )
    
    # Analysis type
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Basic Analysis", "Enhanced Analysis", "Cross-Platform Consensus", "Risk Assessment", "News Impact Analysis"]
    )
    
    # News-specific controls
    st.sidebar.markdown("### 📰 News Controls")
    news_sources = st.sidebar.multiselect(
        "News Sources",
        ["Reuters", "Bloomberg", "CNBC", "MarketWatch", "CoinDesk", "Yahoo Finance"],
        default=["Reuters", "Bloomberg", "CNBC", "MarketWatch"]
    )
    
    news_categories = st.sidebar.multiselect(
        "News Categories",
        ["economy", "technology", "crypto", "politics", "general"],
        default=["economy", "technology", "crypto"]
    )
    
    # Refresh interval
    refresh_interval = st.sidebar.slider(
        "Auto-refresh (seconds)",
        min_value=30,
        max_value=300,
        value=60,
        step=30
    )
    
    # Number of markets
    num_markets = st.sidebar.slider(
        "Number of Markets",
        min_value=5,
        max_value=50,
        value=15,
        step=5
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Initialize data fetching
        if st.button("🔄 Fetch Latest Data + News", type="primary"):
            with st.spinner("Fetching prediction markets data and news analysis..."):
                markets_data = generate_sample_markets(data_sources, categories, num_markets)
                
                if markets_data:
                    st.session_state.markets_data = markets_data
                    st.session_state.last_refresh = datetime.now()
                    
                    # Process news integration
                    try:
                        asyncio.run(process_news_for_markets(markets_data, news_sources, news_categories))
                        st.success(f"✅ Fetched {len(markets_data)} markets and analyzed {len(st.session_state.news_articles)} news articles!")
                    except Exception as e:
                        st.error(f"❌ Failed to process news: {e}")
                        st.success(f"✅ Fetched {len(markets_data)} markets successfully!")
                else:
                    st.error("❌ Failed to fetch markets data")
    
    with col2:
        # Status information
        if 'last_refresh' in st.session_state:
            st.metric(
                "Last Update",
                st.session_state.last_refresh.strftime("%H:%M:%S")
            )
        
        st.metric(
            "Total Markets",
            len(st.session_state.get('markets_data', []))
        )
        
        # News status
        if st.session_state.news_articles:
            st.metric(
                "News Articles",
                len(st.session_state.news_articles)
            )
            st.metric(
                "Impact Predictions",
                len(st.session_state.news_impacts)
            )
    
    # Display dashboard with news integration
    if 'markets_data' in st.session_state and st.session_state.markets_data:
        markets_data = st.session_state.markets_data
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Market Overview", 
            "📈 Signals Analysis", 
            "🔗 Cross-Platform", 
            "⚠️ Risk Assessment",
            "🗞️ News & Impact"
        ])
        
        with tab1:
            display_market_overview(markets_data, analysis_type)
        
        with tab2:
            display_signals_analysis(markets_data, analysis_type)
        
        with tab3:
            display_cross_platform_analysis(markets_data, analysis_type)
        
        with tab4:
            display_risk_assessment(markets_data, analysis_type)
        
        with tab5:
            display_news_impact_analysis(markets_data)
    else:
        st.info("👆 Click 'Fetch Latest Data + News' to load prediction markets and AI news analysis")
        display_sample_dashboard()

async def process_news_for_markets(markets_data: list, news_sources: list, news_categories: list):
    """Process news integration with markets"""
    try:
        # Initialize news engine
        await st.session_state.news_engine.initialize()
        
        # Process news
        articles, impacts = await st.session_state.news_engine.process_news_for_markets(markets_data)
        
        # Update session state
        st.session_state.news_articles = articles
        st.session_state.news_impacts = impacts
        st.session_state.news_last_update = datetime.now()
        
        # Clean up
        await st.session_state.news_engine.cleanup()
        
    except Exception as e:
        logger.error(f"Error processing news: {e}")
        st.error(f"News processing error: {e}")

def generate_sample_markets(sources: list, categories: list, num_markets: int) -> list:
    """Generate sample prediction markets data"""
    try:
        markets = []
        questions = [
            "Will Bitcoin reach $100,000 by end of 2024?",
            "Will Tesla stock price exceed $1,000 in 2024?",
            "Will the Fed cut interest rates in 2024?",
            "Will OpenAI release GPT-5 before 2025?",
            "Will Apple release a new iPhone model in 2024?",
            "Will Amazon stock price increase by 50% in 2024?",
            "Will Google stock price reach new all-time highs in 2024?",
            "Will the S&P 500 index reach 6,000 points in 2024?",
            "Will crypto market cap exceed $5 trillion in 2024?",
            "Will Microsoft stock price increase by 40% in 2024?"
        ]
        
        descriptions = {
            'economy': ['economic indicator', 'financial forecast', 'market prediction'],
            'technology': ['tech stock analysis', 'AI development', 'product launch'],
            'politics': ['election outcome', 'policy decision', 'government action'],
            'crypto': ['cryptocurrency price', 'blockchain adoption', 'digital asset'],
            'stocks': ['stock price target', 'earnings forecast', 'market performance']
        }
        
        for i in range(num_markets):
            source = sources[i % len(sources)]
            category = categories[i % len(categories)] if categories else 'other'
            
            # Generate market data
            market = {
                'id': f"{source}_{i}",
                'question': questions[i % len(questions)],
                'description': f"{source.title()} prediction market - {category}",
                'category': category,
                'sub_category': random.choice(['crypto', 'stocks', 'ai', 'economy', 'policy']),
                'market_type': 'binary',
                'outcomes': ['Yes', 'No'],
                'probabilities': [random.uniform(0.2, 0.8), 1 - random.uniform(0.2, 0.8)],
                'current_price': random.uniform(0.2, 0.8),
                'volume': random.randint(50000, 2000000),
                'liquidity': random.randint(25000, 1000000),
                'open_time': datetime.now() - timedelta(days=random.randint(1, 60)),
                'close_time': datetime.now() + timedelta(days=random.randint(30, 365)),
                'resolution_date': datetime.now() + timedelta(days=random.randint(90, 400)),
                'url': f"https://{source.lower()}.com/market_{i}",
                'status': 'open',
                'source': source.lower()
            }
            markets.append(market)
        
        logger.info(f"Generated {len(markets)} sample markets")
        return markets
        
    except Exception as e:
        logger.error(f"Error generating sample markets: {e}")
        return []

def display_news_impact_analysis(markets_data: list):
    """Display news impact analysis section"""
    st.markdown('<div class="news-feed-container">', unsafe_allow_html=True)
    st.markdown("### 🗞️ News Impact Analysis")
    
    if not st.session_state.news_articles:
        st.info("No news articles available. Click 'Fetch Latest Data + News' to analyze news impact.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # News metrics
    col1, col2, col3, col4 = st.columns(4)
    
    high_impact_count = len([impact for impact in st.session_state.news_impacts if impact.impact_magnitude > 0.7])
    breaking_news_count = len([article for article in st.session_state.news_articles if 
                              (datetime.now() - article.published_at).total_seconds() < 3600])
    avg_confidence = np.mean([impact.confidence for impact in st.session_state.news_impacts]) if st.session_state.news_impacts else 0
    sentiment_distribution = {
        'positive': len([article for article in st.session_state.news_articles if article.sentiment_score > 0.1]),
        'negative': len([article for article in st.session_state.news_articles if article.sentiment_score < -0.1]),
        'neutral': len([article for article in st.session_state.news_articles if -0.1 <= article.sentiment_score <= 0.1])
    }
    
    col1.metric("High Impact Articles", high_impact_count)
    col2.metric("Breaking News (1h)", breaking_news_count)
    col3.metric("Avg Confidence", f"{avg_confidence:.1%}")
    col4.metric("Total Predictions", len(st.session_state.news_impacts))
    
    # News feed
    st.markdown("#### 📰 Latest News & AI Analysis")
    
    for article in st.session_state.news_articles[:10]:  # Show top 10 articles
        # Determine impact level
        impact_level = "high-impact-news" if article.credibility_score * abs(article.sentiment_score) > 0.5 else ""
        is_breaking = (datetime.now() - article.published_at).total_seconds() < 3600
        
        if is_breaking:
            impact_level += " breaking-news"
        
        # Sentiment styling
        if article.sentiment_score > 0.1:
            sentiment_class = "news-impact-positive"
            sentiment_text = "📈 Positive"
        elif article.sentiment_score < -0.1:
            sentiment_class = "news-impact-negative"
            sentiment_text = "📉 Negative"
        else:
            sentiment_class = "news-impact-neutral"
            sentiment_text = "➡️ Neutral"
        
        # Confidence styling
        confidence_score = article.credibility_score * abs(article.sentiment_score)
        if confidence_score > 0.6:
            confidence_class = "news-confidence-high"
            confidence_text = "High"
        elif confidence_score > 0.3:
            confidence_class = "news-confidence-medium"
            confidence_text = "Medium"
        else:
            confidence_class = "news-confidence-low"
            confidence_text = "Low"
        
        # Display article
        st.markdown(f"""
        <div class="{impact_level}">
            <h4>{article.title}</h4>
            <p><strong>Source:</strong> {article.source} | 
               <strong>Published:</strong> {article.published_at.strftime('%H:%M')} | 
               <strong>Category:</strong> {article.category}</p>
            <p><strong>Sentiment:</strong> <span class="{sentiment_class}">{sentiment_text} ({article.sentiment_score:.2f})</span> | 
               <strong>Confidence:</strong> <span class="{confidence_class}">{confidence_text}</span></p>
            <p><em>{article.summary}</em></p>
            <p><strong>Correlated Markets:</strong> {', '.join(article.market_correlations[:3]) if article.market_correlations else 'None detected'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show impact predictions for this article
        article_impacts = [impact for impact in st.session_state.news_impacts if impact.article_id == article.id]
        if article_impacts:
            st.markdown("<strong>Impact Predictions:</strong>", unsafe_allow_html=True)
            for impact in article_impacts[:2]:  # Show top 2 impacts per article
                direction_emoji = "📈" if impact.predicted_direction == 'up' else "📉" if impact.predicted_direction == 'down' else "➡️"
                st.markdown(f"- {direction_emoji} **{impact.market_id}**: {impact.predicted_direction.upper()} ({impact.confidence:.1%}) in {impact.time_horizon} | {impact.reasoning}")
        
        st.markdown("---")
    
    # Impact visualization
    if st.session_state.news_impacts:
        st.markdown("#### 📊 Impact Distribution")
        
        # Impact magnitude chart
        impact_data = pd.DataFrame([{
            'Market': impact.market_id,
            'Direction': impact.predicted_direction,
            'Confidence': impact.confidence,
            'Magnitude': impact.impact_magnitude,
            'Time Horizon': impact.time_horizon
        } for impact in st.session_state.news_impacts])
        
        if not impact_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_impact = px.scatter(
                    impact_data,
                    x='Magnitude',
                    y='Confidence',
                    color='Direction',
                    size='Magnitude',
                    title="News Impact vs Confidence",
                    color_discrete_map={'up': '#00FF88', 'down': '#FF3366', 'neutral': '#FFC107'}
                )
                fig_impact.update_layout(
                    plot_bgcolor='#141b26',
                    paper_bgcolor='#141b26',
                    font_color='#ffffff',
                    title_font_color='#ffffff'
                )
                st.plotly_chart(fig_impact, use_container_width=True)
            
            with col2:
                direction_counts = impact_data['Direction'].value_counts()
                fig_direction = px.pie(
                    values=direction_counts.values,
                    names=direction_counts.index,
                    title="Predicted Direction Distribution",
                    color_discrete_map={'up': '#00FF88', 'down': '#FF3366', 'neutral': '#FFC107'}
                )
                fig_direction.update_layout(
                    plot_bgcolor='#141b26',
                    paper_bgcolor='#141b26',
                    font_color='#ffffff',
                    title_font_color='#ffffff'
                )
                st.plotly_chart(fig_direction, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ... Include all the existing functions from probex_dashboard.py ...
def display_market_overview(markets_data: list, analysis_type: str):
    """Display market overview section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Market Overview")
    
    if not markets_data:
        st.warning("No markets data available")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_volume = sum(market['volume'] for market in markets_data)
    avg_probability = np.mean([market['probabilities'][0] for market in markets_data])
    categories_count = len(set(market['category'] for market in markets_data))
    sources_count = len(set(market['source'] for market in markets_data))
    
    col1.metric("Total Volume", f"${total_volume:,.0f}")
    col2.metric("Avg Probability", f"{avg_probability:.1%}")
    col3.metric("Categories", categories_count)
    col4.metric("Sources", sources_count)
    
    # Market distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Probability distribution
        probabilities = [market['probabilities'][0] for market in markets_data]
        fig_prob = px.histogram(
            x=probabilities,
            title="Probability Distribution",
            labels={'x': 'Probability', 'y': 'Number of Markets'},
            nbins=20,
            color_discrete_sequence=['#00B3FF']
        )
        fig_prob.update_layout(
            plot_bgcolor='#141b26',
            paper_bgcolor='#141b26',
            font_color='#ffffff',
            title_font_color='#ffffff'
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    
    with col2:
        # Volume by source
        volume_by_source = pd.DataFrame(markets_data).groupby('source')['volume'].sum().reset_index()
        fig_volume = px.bar(
            volume_by_source,
            x='source',
            y='volume',
            title="Volume by Source",
            labels={'volume': 'Volume ($)', 'source': 'Platform'},
            color='source',
            color_discrete_sequence=['#00B3FF', '#2EFFFA', '#FF3366']
        )
        fig_volume.update_layout(
            plot_bgcolor='#141b26',
            paper_bgcolor='#141b26',
            font_color='#ffffff',
            title_font_color='#ffffff'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_signals_analysis(markets_data: list, analysis_type: str):
    """Display signals analysis section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Signals Analysis")
    
    if not markets_data:
        st.warning("No markets data available for signals analysis")
        return
    
    st.info("Signals analysis functionality ready for integration with news data")
    st.markdown('</div>', unsafe_allow_html=True)

def display_cross_platform_analysis(markets_data: list, analysis_type: str):
    """Display cross-platform analysis section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### 🔗 Cross-Platform Analysis")
    
    if not markets_data:
        st.warning("No markets data available for cross-platform analysis")
        return
    
    st.info("Cross-platform analysis functionality ready for integration")
    st.markdown('</div>', unsafe_allow_html=True)

def display_risk_assessment(markets_data: list, analysis_type: str):
    """Display risk assessment section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Risk Assessment")
    
    if not markets_data:
        st.warning("No markets data available for risk assessment")
        return
    
    st.info("Risk assessment functionality ready for integration")
    st.markdown('</div>', unsafe_allow_html=True)

def display_sample_dashboard():
    """Display sample dashboard when no data is available"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("#### 📋 Sample Data Available")
    st.info("Click 'Fetch Latest Data + News' to see the enhanced dashboard with AI news analysis")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    create_enhanced_probex_dashboard()
