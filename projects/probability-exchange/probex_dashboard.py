#!/usr/bin/env python3
"""
Probex.markets Dashboard

Terminal-style prediction markets dashboard with dark theme
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for probex.markets theme
def load_probex_styles():
    st.markdown("""
    <style>
        /* Import IBM Plex Mono font */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');
        
        /* Root color variables */
        :root {
            --bg-dark: #050505;
            --bg-surface: #0A0A0A;
            --brand-indigo: #6366f1;
            --brand-purple: #9333ea;
            --text-white: #ffffff;
            --text-zinc: #a1a1aa;
            --border-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Main application background */
        .stApp {
            background-color: var(--bg-dark);
            font-family: 'IBM Plex Mono', monospace;
        }
        
        /* Header styling */
        .main-header {
            color: var(--text-white);
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: 48px;
            margin-bottom: 1rem;
            letter-spacing: -0.05em;
        }
        
        .main-subheader {
            color: var(--text-zinc);
            font-family: 'IBM Plex Mono', monospace;
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
        
        .logo-text {
            color: var(--text-white);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.05em;
        }
        
        .logo-text .highlight {
            color: var(--text-zinc);
            font-weight: 600;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-1v3fvcr {
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border-color);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--text-white);
            color: #000000;
            border: none;
            border-radius: 9999px;
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 500;
            height: 40px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #e4e4e7;
            transform: scale(1.02);
        }
        
        /* Secondary button */
        .secondary-btn button {
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-white);
        }
        
        .secondary-btn button:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Input styling */
        .stSelectbox > div > div {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 9999px;
            color: var(--text-white);
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        /* Multi-select styling */
        .stMultiSelect > div > div {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }
        
        /* Slider styling */
        .stSlider > div > div {
            color: var(--text-white);
        }
        
        /* Metric styling */
        .stMetric {
            background-color: var(--bg-surface);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .stMetric label {
            color: var(--text-zinc);
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 400;
        }
        
        .stMetric div {
            color: var(--text-white);
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent;
            border-bottom: 1px solid var(--border-color);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            color: var(--text-zinc);
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            color: var(--text-white) !important;
            border-bottom: 2px solid var(--brand-indigo);
        }
        
        /* Dataframe styling */
        .stDataFrame {
            background-color: var(--bg-surface);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        /* Chart container styling */
        .plotly-graph-div {
            background-color: var(--bg-surface);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            padding: 1rem;
        }
        
        /* Success/Error message styling */
        .stSuccess {
            background-color: rgba(34, 197, 94, 0.1);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.2);
            border-radius: 8px;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
        }
        
        .stWarning {
            background-color: rgba(234, 179, 8, 0.1);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.2);
            border-radius: 8px;
        }
        
        .stInfo {
            background-color: rgba(99, 102, 241, 0.1);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 8px;
        }
        
        /* Custom classes for probability displays */
        .probability-yes {
            color: #4ade80;
            font-weight: 600;
        }
        
        .probability-no {
            color: #f87171;
            font-weight: 600;
        }
        
        .high-confidence {
            color: #818cf8;
            font-weight: 600;
        }
        
        /* Terminal-style container */
        .terminal-container {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
    </style>
    """, unsafe_allow_html=True)

def create_probex_dashboard():
    """Create the probex.markets dashboard with terminal styling"""
    
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
        <div class="logo-text">
            probex<span class="highlight">.markets</span>
        </div>
    </div>
    <h1 class="main-header">
        Unlock the Future <br />
        <span style="background: linear-gradient(to bottom, #ffffff, rgba(255,255,255,0.4)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            of Predictions.
        </span>
    </h1>
    <p class="main-subheader">The next-generation prediction exchange platform.</p>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)
    
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
        ["Basic Analysis", "Enhanced Analysis", "Cross-Platform Consensus", "Risk Assessment"]
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
        if st.button("🔄 Fetch Latest Data", type="primary"):
            with st.spinner("Fetching prediction markets data..."):
                markets_data = generate_sample_markets(data_sources, categories, num_markets)
                
                if markets_data:
                    st.session_state.markets_data = markets_data
                    st.session_state.last_refresh = datetime.now()
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
    
    # Display market data if available
    if 'markets_data' in st.session_state and st.session_state.markets_data:
        markets_data = st.session_state.markets_data
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "📈 Signals Analysis", "🔗 Cross-Platform", "⚠️ Risk Assessment"])
        
        with tab1:
            display_market_overview(markets_data, analysis_type)
        
        with tab2:
            display_signals_analysis(markets_data, analysis_type)
        
        with tab3:
            display_cross_platform_analysis(markets_data, analysis_type)
        
        with tab4:
            display_risk_assessment(markets_data, analysis_type)
        
        # Auto-refresh mechanism (disabled for now due to streamlit limitations)
        # if refresh_interval > 0:
        #     time.sleep(refresh_interval)
        #     st.experimental_rerun()
    else:
        st.info("👆 Click 'Fetch Latest Data' to load prediction markets information")
        
        # Display sample visualization
        display_sample_dashboard()

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
            color_discrete_sequence=['#6366f1']
        )
        fig_prob.update_layout(
            plot_bgcolor='#0A0A0A',
            paper_bgcolor='#0A0A0A',
            font_color='#ffffff',
            title_font_color='#ffffff',
            font_family='IBM Plex Mono'
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
            color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8']
        )
        fig_volume.update_layout(
            plot_bgcolor='#0A0A0A',
            paper_bgcolor='#0A0A0A',
            font_color='#ffffff',
            title_font_color='#ffffff',
            font_family='IBM Plex Mono'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # Top markets table
    st.markdown("#### 🏆 Top Markets by Volume")
    
    top_markets = sorted(markets_data, key=lambda x: x['volume'], reverse=True)[:10]
    display_markets = []
    
    for market in top_markets:
        display_markets.append({
            'Question': market['question'][:50] + "..." if len(market['question']) > 50 else market['question'],
            'Source': market['source'].title(),
            'Category': market['category'],
            'Probability': f'<span class="probability-yes">{market["probabilities"][0]:.1%}</span>',
            'Volume': f"${market['volume']:,.0f}",
            'Close Date': market['close_time'].strftime("%Y-%m-%d")
        })
    
    st.markdown(pd.DataFrame(display_markets).to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Category distribution
    st.markdown("#### 📈 Category Distribution")
    category_counts = pd.DataFrame(markets_data)['category'].value_counts()
    fig_category = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Markets by Category",
        color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe']
    )
    fig_category.update_layout(
        plot_bgcolor='#0A0A0A',
        paper_bgcolor='#0A0A0A',
        font_color='#ffffff',
        title_font_color='#ffffff',
        font_family='IBM Plex Mono'
    )
    st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_signals_analysis(markets_data: list, analysis_type: str):
    """Display signals analysis section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Signals Analysis")
    
    if not markets_data:
        st.warning("No markets data available for signals analysis")
        return
    
    # Generate prediction signals
    signals = generate_prediction_signals(markets_data)
    
    if not signals:
        st.info("No prediction signals generated")
        return
    
    # Signal metrics
    col1, col2, col3 = st.columns(3)
    
    high_conf_signals = len([s for s in signals if s.get('confidence_score', 0) > 0.7])
    strong_predictions = len([s for s in signals if s.get('prediction_strength') == 'strong'])
    avg_confidence = np.mean([s.get('confidence_score', 0) for s in signals])
    
    col1.metric("High Confidence Signals", high_conf_signals)
    col2.metric("Strong Predictions", strong_predictions)
    col3.metric("Avg Confidence", f"{avg_confidence:.1%}")
    
    # Signal details
    st.markdown("#### 🎯 Prediction Signals")
    
    signal_data = []
    for signal in signals:
        confidence_class = "high-confidence" if signal.get('confidence_score', 0) > 0.7 else ""
        signal_data.append({
            'Question': signal.get('question', '')[:50] + "..." if len(signal.get('question', '')) > 50 else signal.get('question', ''),
            'Category': signal.get('category', 'other'),
            'Probability': f'<span class="probability-yes">{signal.get("combined_probability", 0):.1%}</span>',
            'Confidence': f'<span class="{confidence_class}">{signal.get("confidence_score", 0):.1%}</span>',
            'Strength': signal.get('prediction_strength', 'unknown').title(),
            'News Correlation': f"{signal.get('news_sentiment_correlation', 0):.2f}"
        })
    
    if signal_data:
        st.markdown(pd.DataFrame(signal_data).to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Signal strength visualization
    if signals:
        strength_counts = {}
        for signal in signals:
            strength = signal.get('prediction_strength', 'unknown')
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        if strength_counts:
            fig_strength = px.pie(
                values=list(strength_counts.values()),
                names=list(strength_counts.keys()),
                title="Signal Strength Distribution",
                color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8']
            )
            fig_strength.update_layout(
                plot_bgcolor='#0A0A0A',
                paper_bgcolor='#0A0A0A',
                font_color='#ffffff',
                title_font_color='#ffffff',
                font_family='IBM Plex Mono'
            )
            st.plotly_chart(fig_strength, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_cross_platform_analysis(markets_data: list, analysis_type: str):
    """Display cross-platform analysis section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### 🔗 Cross-Platform Analysis")
    
    if not markets_data:
        st.warning("No markets data available for cross-platform analysis")
        return
    
    # Group markets by similarity
    similar_groups = find_similar_markets(markets_data)
    
    st.markdown("#### 📊 Platform Coverage")
    
    # Platform statistics
    platform_stats = {}
    for market in markets_data:
        source = market['source']
        if source not in platform_stats:
            platform_stats[source] = {'count': 0, 'total_volume': 0, 'avg_probability': 0}
        
        platform_stats[source]['count'] += 1
        platform_stats[source]['total_volume'] += market['volume']
        platform_stats[source]['avg_probability'] += market['probabilities'][0]
    
    # Calculate averages
    for stats in platform_stats.values():
        stats['avg_probability'] /= stats['count']
    
    # Display platform comparison
    platform_df = pd.DataFrame.from_dict(platform_stats, orient='index').reset_index()
    platform_df.columns = ['Platform', 'Market Count', 'Total Volume', 'Avg Probability']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_platforms = px.bar(
            platform_df,
            x='Platform',
            y='Market Count',
            title="Markets by Platform",
            color='Platform',
            color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8']
        )
        fig_platforms.update_layout(
            plot_bgcolor='#0A0A0A',
            paper_bgcolor='#0A0A0A',
            font_color='#ffffff',
            title_font_color='#ffffff',
            font_family='IBM Plex Mono'
        )
        st.plotly_chart(fig_platforms, use_container_width=True)
    
    with col2:
        fig_volume = px.bar(
            platform_df,
            x='Platform',
            y='Total Volume',
            title="Volume by Platform",
            color='Platform',
            color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8']
        )
        fig_volume.update_layout(
            plot_bgcolor='#0A0A0A',
            paper_bgcolor='#0A0A0A',
            font_color='#ffffff',
            title_font_color='#ffffff',
            font_family='IBM Plex Mono'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # Similar markets across platforms
    if similar_groups:
        st.markdown("#### 🔍 Cross-Platform Market Groups")
        
        for i, group in enumerate(similar_groups[:3]):  # Show top 3 groups
            if len(group) > 1:
                st.markdown(f"**Group {i+1}:**")
                
                group_data = []
                for market in group:
                    group_data.append({
                        'Question': market['question'][:50] + "...",
                        'Platform': market['source'].title(),
                        'Probability': f'<span class="probability-yes">{market["probabilities"][0]:.1%}</span>',
                        'Volume': f"${market['volume']:,.0f}"
                    })
                
                st.markdown(pd.DataFrame(group_data).to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No similar markets found across platforms")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_risk_assessment(markets_data: list, analysis_type: str):
    """Display risk assessment section"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Risk Assessment")
    
    if not markets_data:
        st.warning("No markets data available for risk assessment")
        return
    
    # Calculate risk metrics
    risk_metrics = calculate_risk_metrics(markets_data)
    
    # Risk overview
    col1, col2, col3 = st.columns(3)
    
    overall_risk = risk_metrics.get('overall_risk_level', 'unknown')
    volatility_score = risk_metrics.get('avg_volatility', 0)
    concentration_risk = risk_metrics.get('concentration_risk', 0)
    
    col1.metric("Overall Risk", overall_risk.title())
    col2.metric("Avg Volatility", f"{volatility_score:.2f}")
    col3.metric("Concentration Risk", f"{concentration_risk:.1%}")
    
    # Risk factors
    st.markdown("#### 🔴 Risk Factors")
    
    risk_factors = risk_metrics.get('risk_factors', [])
    if risk_factors:
        for factor in risk_factors:
            st.warning(f"⚠️ {factor}")
    else:
        st.success("✅ No significant risk factors detected")
    
    # Risk mitigation suggestions
    st.markdown("#### 💡 Risk Mitigation Suggestions")
    
    suggestions = risk_metrics.get('mitigation_suggestions', [])
    if suggestions:
        for suggestion in suggestions:
            st.info(f"💡 {suggestion}")
    else:
        st.info("💡 Continue monitoring market conditions")
    
    # Volatility analysis
    st.markdown("#### 📈 Volatility Analysis")
    
    probabilities = [market['probabilities'][0] for market in markets_data]
    volatility = np.std(probabilities)
    
    if volatility > 0.3:
        st.warning(f"⚠️ High volatility detected (σ = {volatility:.3f})")
    else:
        st.success(f"✅ Low volatility (σ = {volatility:.3f})")
    
    # Volume concentration
    st.markdown("#### 📊 Volume Distribution")
    
    total_volume = sum(market['volume'] for market in markets_data)
    volume_by_source = pd.DataFrame(markets_data).groupby('source')['volume'].sum()
    volume_shares = volume_by_source / total_volume
    
    concentration_threshold = 0.6  # 60% concentration threshold
    max_concentration = volume_shares.max()
    
    if max_concentration > concentration_threshold:
        st.warning(f"⚠️ High concentration risk: {max_concentration:.1%} in one platform")
    else:
        st.success("✅ Well-distributed volume across platforms")
    
    # Create concentration chart
    fig_concentration = px.pie(
        values=volume_shares.values,
        names=volume_shares.index,
        title="Volume Distribution by Platform",
        color_discrete_sequence=['#6366f1', '#9333ea', '#818cf8']
    )
    fig_concentration.update_layout(
        plot_bgcolor='#0A0A0A',
        paper_bgcolor='#0A0A0A',
        font_color='#ffffff',
        title_font_color='#ffffff',
        font_family='IBM Plex Mono'
    )
    st.plotly_chart(fig_concentration, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_sample_dashboard():
    """Display sample dashboard when no data is available"""
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    st.markdown("#### 📋 Sample Market Data")
    
    # Create sample data
    sample_data = {
        'Question': ['Will Bitcoin reach $100K in 2024?', 'Will Tesla stock double in 2024?'],
        'Source': ['Polymarket', 'Kalshi'],
        'Category': ['economy', 'technology'],
        'Probability': ['<span class="probability-yes">35%</span>', '<span class="probability-yes">25%</span>'],
        'Volume': ['$1.2M', '$850K']
    }
    
    st.markdown(pd.DataFrame(sample_data).to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Sample chart
    st.markdown("#### 📊 Sample Visualization")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Polymarket', 'Kalshi', 'Manifold'],
        y=[1200000, 850000, 650000],
        name='Volume ($)',
        marker_color='#6366f1'
    ))
    
    fig.update_layout(
        title="Sample Volume by Platform",
        xaxis_title="Platform",
        yaxis_title="Volume ($)",
        plot_bgcolor='#0A0A0A',
        paper_bgcolor='#0A0A0A',
        font_color='#ffffff',
        title_font_color='#ffffff',
        font_family='IBM Plex Mono'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def generate_prediction_signals(markets_data: list) -> list:
    """Generate prediction signals from markets data"""
    try:
        signals = []
        
        # Group markets by category
        by_category = {}
        for market in markets_data:
            category = market['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(market)
        
        # Generate signals for each category
        for category, markets in by_category.items():
            if len(markets) >= 2:
                # Calculate combined probability
                total_volume = sum(m['volume'] for m in markets)
                weighted_prob = sum(m['probabilities'][0] * m['volume'] for m in markets) / total_volume
                
                # Determine confidence based on volume and consensus
                confidence = min(total_volume / 1000000, 1.0)
                if len(markets) > 1:
                    prob_std = np.std([m['probabilities'][0] for m in markets])
                    consensus = 1 - prob_std
                    confidence *= consensus
                
                # Determine prediction strength
                if confidence > 0.7 and abs(weighted_prob - 0.5) > 0.3:
                    strength = 'strong'
                elif confidence > 0.5 and abs(weighted_prob - 0.5) > 0.2:
                    strength = 'moderate'
                else:
                    strength = 'weak'
                
                signal = {
                    'question': f"{category.title()} markets sentiment",
                    'category': category,
                    'combined_probability': weighted_prob,
                    'confidence_score': confidence,
                    'prediction_strength': strength,
                    'news_sentiment_correlation': np.random.uniform(0.3, 0.9),
                    'market_count': len(markets)
                }
                signals.append(signal)
        
        return signals
        
    except Exception as e:
        logger.error(f"Error generating prediction signals: {e}")
        return []

def find_similar_markets(markets_data: list) -> list:
    """Find similar markets across platforms"""
    try:
        similar_groups = []
        
        for i, market1 in enumerate(markets_data):
            group = [market1]
            words1 = set(market1['question'].lower().split())
            
            for j, market2 in enumerate(markets_data[i+1:], i+1):
                if market1['source'] != market2['source']:  # Different platforms
                    words2 = set(market2['question'].lower().split())
                    
                    # Simple similarity check
                    intersection = words1.intersection(words2)
                    union = words1.union(words2)
                    
                    if union and len(intersection) / len(union) > 0.3:  # 30% similarity threshold
                        group.append(market2)
            
            if len(group) > 1:
                similar_groups.append(group)
        
        return similar_groups
        
    except Exception as e:
        logger.error(f"Error finding similar markets: {e}")
        return []

def calculate_risk_metrics(markets_data: list) -> dict:
    """Calculate risk metrics for markets data"""
    try:
        metrics = {}
        
        # Volatility risk
        probabilities = [market['probabilities'][0] for market in markets_data]
        volatility = np.std(probabilities)
        metrics['avg_volatility'] = volatility
        
        # Concentration risk
        total_volume = sum(market['volume'] for market in markets_data)
        volume_by_source = {}
        for market in markets_data:
            source = market['source']
            volume_by_source[source] = volume_by_source.get(source, 0) + market['volume']
        
        max_concentration = max(volume_by_source.values()) / total_volume
        metrics['concentration_risk'] = max_concentration
        
        # Overall risk level
        if volatility > 0.3 or max_concentration > 0.7:
            metrics['overall_risk_level'] = 'high'
        elif volatility < 0.2 and max_concentration < 0.5:
            metrics['overall_risk_level'] = 'low'
        else:
            metrics['overall_risk_level'] = 'medium'
        
        # Risk factors
        risk_factors = []
        if volatility > 0.3:
            risk_factors.append("High probability volatility")
        if max_concentration > 0.7:
            risk_factors.append("High platform concentration")
        if len(markets_data) < 10:
            risk_factors.append("Limited market coverage")
        
        metrics['risk_factors'] = risk_factors
        
        # Mitigation suggestions
        suggestions = []
        if volatility > 0.3:
            suggestions.append("Wait for probability convergence")
        if max_concentration > 0.7:
            suggestions.append("Diversify across platforms")
        if len(markets_data) < 10:
            suggestions.append("Expand market coverage")
        
        metrics['mitigation_suggestions'] = suggestions
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating risk metrics: {e}")
        return {'overall_risk_level': 'unknown'}

if __name__ == "__main__":
    create_probex_dashboard()