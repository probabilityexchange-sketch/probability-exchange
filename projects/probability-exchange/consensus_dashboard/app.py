#!/usr/bin/env python3
"""
Probex Consensus Dashboard MVP

Cross-platform prediction market consensus analysis dashboard
Focus on aggregating and analyzing consensus across Polymarket, Kalshi, and Manifold
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
import time

# Import existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use simulated data modules only for MVP deployment
# from enhanced_prediction_markets import EnhancedPredictionMarketsIntegration, EnhancedPredictionSignal
# from real_api_integration import RealAPIManager

# Standalone implementations for MVP deployment
from simulated_data import SimulatedDataManager, generate_sample_signals

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Consensus Dashboard Configuration
class ConsensusDashboardConfig:
    """Configuration for the consensus dashboard"""
    
    # Color scheme (matching probex branding)
    COLORS = {
        'primary': '#00B3FF',
        'secondary': '#2EFFFA', 
        'accent': '#FF3366',
        'success': '#22C55E',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'dark_bg': '#0a0f16',
        'surface': '#141b26',
        'text': '#ffffff',
        'text_secondary': '#7a8a99'
    }
    
    # Consensus thresholds
    CONSENSUS_THRESHOLDS = {
        'high': 0.85,
        'medium': 0.70,
        'low': 0.50
    }
    
    # Confidence levels
    CONFIDENCE_LEVELS = {
        'very_high': 0.90,
        'high': 0.75,
        'medium': 0.60,
        'low': 0.40
    }

def load_consensus_styles():
    """Load custom CSS for consensus dashboard"""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        :root {{
            --bg-dark: {ConsensusDashboardConfig.COLORS['dark_bg']};
            --bg-surface: {ConsensusDashboardConfig.COLORS['surface']};
            --brand-primary: {ConsensusDashboardConfig.COLORS['primary']};
            --brand-secondary: {ConsensusDashboardConfig.COLORS['secondary']};
            --accent: {ConsensusDashboardConfig.COLORS['accent']};
            --success: {ConsensusDashboardConfig.COLORS['success']};
            --warning: {ConsensusDashboardConfig.COLORS['warning']};
            --danger: {ConsensusDashboardConfig.COLORS['danger']};
            --text-primary: {ConsensusDashboardConfig.COLORS['text']};
            --text-secondary: {ConsensusDashboardConfig.COLORS['text_secondary']};
        }}
        
        .stApp {{
            background-color: var(--bg-dark);
            background-image: 
                linear-gradient(rgba(0, 179, 255, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 179, 255, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            font-family: 'Inter', sans-serif;
        }}
        
        .consensus-header {{
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 36px;
            margin-bottom: 0.5rem;
            text-align: center;
        }}
        
        .consensus-subheader {{
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            font-size: 16px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .consensus-logo {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 2rem;
        }}
        
        .logo-symbol {{
            background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
            color: var(--bg-dark);
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 24px;
        }}
        
        .logo-text {{
            color: var(--text-primary);
            font-size: 24px;
            font-weight: 700;
        }}
        
        .consensus-card {{
            background: var(--bg-surface);
            border: 1px solid rgba(0, 179, 255, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        
        .consensus-high {{
            border-color: var(--success);
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
        }}
        
        .consensus-medium {{
            border-color: var(--warning);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
        }}
        
        .consensus-low {{
            border-color: var(--danger);
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
        }}
        
        .consensus-score {{
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            margin: 1rem 0;
        }}
        
        .consensus-label {{
            text-align: center;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.875rem;
        }}
        
        .platform-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.25rem;
        }}
        
        .platform-polymarket {{
            background: rgba(0, 179, 255, 0.2);
            color: var(--brand-primary);
        }}
        
        .platform-kalshi {{
            background: rgba(46, 255, 250, 0.2);
            color: var(--brand-secondary);
        }}
        
        .platform-manifold {{
            background: rgba(255, 51, 102, 0.2);
            color: var(--accent);
        }}
        
        .signal-strong {{
            color: var(--success);
            font-weight: 600;
        }}
        
        .signal-moderate {{
            color: var(--warning);
            font-weight: 600;
        }}
        
        .signal-weak {{
            color: var(--danger);
            font-weight: 600;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: var(--bg-surface);
            border: 1px solid rgba(0, 179, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--brand-primary);
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        /* Streamlit overrides */
        .stSelectbox > div > div {{
            background-color: var(--bg-surface);
            border: 2px solid rgba(0, 179, 255, 0.2);
            border-radius: 8px;
        }}
        
        .stSelectbox > div > div:focus-within {{
            border-color: var(--brand-primary);
            box-shadow: 0 0 0 1px var(--brand-primary);
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
            color: var(--bg-dark);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            height: 48px;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 179, 255, 0.3);
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--bg-surface);
            border-radius: 8px 8px 0 0;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--bg-dark) !important;
            color: var(--brand-primary) !important;
        }}
        
        .plotly-graph-div {{
            background-color: var(--bg-surface);
            border-radius: 8px;
            padding: 1rem;
        }}
    </style>
    """, unsafe_allow_html=True)

class ConsensusDashboard:
    """Main consensus dashboard application"""
    
    def __init__(self):
        self.config = ConsensusDashboardConfig()
        # Mock initialization for MVP deployment
        # self.enhanced_integration = EnhancedPredictionMarketsIntegration()
        # self.api_manager = None
        self.enhanced_integration = None
        self.api_manager = None
        self.data_manager = SimulatedDataManager()
        self.consensus_data = {}
        self.signals_data = []
        
    def create_dashboard(self):
        """Create the main consensus dashboard"""
        # Load custom styles
        load_consensus_styles()
        
        # Page configuration
        st.set_page_config(
            page_title="Probex Consensus Dashboard",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header
        self._render_header()
        
        # Sidebar controls
        self._render_sidebar()
        
        # Main content
        self._render_main_content()
    
    def _render_header(self):
        """Render dashboard header"""
        header_html = f"""
        <div class="consensus-logo">
            <div class="logo-symbol">P(E)</div>
            <div class="logo-text">probex.consensus</div>
        </div>
        <h1 class="consensus-header">Cross-Platform Consensus Intelligence</h1>
        <p class="consensus-subheader">Real-time aggregation and analysis of prediction markets across Polymarket, Kalshi, and Manifold</p>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.header("🎛️ Consensus Controls")
        
        # Data source selection
        self.data_sources = st.sidebar.multiselect(
            "Data Sources",
            ["Polymarket", "Kalshi", "Manifold"],
            default=["Polymarket", "Kalshi", "Manifold"],
            help="Select prediction market platforms to analyze"
        )
        
        # Consensus threshold
        self.consensus_threshold = st.sidebar.slider(
            "Consensus Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Minimum consensus score required for strong signals"
        )
        
        # Minimum confidence
        self.min_confidence = st.sidebar.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.60,
            step=0.05,
            help="Filter signals by minimum confidence score"
        )
        
        # Categories
        self.categories = st.sidebar.multiselect(
            "Categories",
            ["politics", "economy", "technology", "sports", "entertainment", "health"],
            default=["economy", "technology", "politics"],
            help="Filter by market categories"
        )
        
        # Analysis mode
        self.analysis_mode = st.sidebar.selectbox(
            "Analysis Mode",
            ["Real-time Consensus", "Historical Analysis", "Signal Detection", "Risk Assessment"],
            help="Choose analysis focus"
        )
        
        # Refresh controls
        st.sidebar.markdown("---")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", type="primary", help="Fetch latest data"):
                self._refresh_data()
        
        with col2:
            if st.button("💾 Save", help="Save current analysis"):
                self._save_analysis()
        
        # Auto-refresh
        self.auto_refresh = st.sidebar.checkbox(
            "Auto-refresh (30s)",
            value=False,
            help="Automatically refresh data every 30 seconds"
        )
    
    def _render_main_content(self):
        """Render main dashboard content"""
        # Initialize session state
        if 'consensus_data' not in st.session_state:
            st.session_state.consensus_data = None
            st.session_state.last_refresh = None
        
        # Data status
        self._render_data_status()
        
        # Main content based on analysis mode
        if st.session_state.consensus_data:
            if self.analysis_mode == "Real-time Consensus":
                self._render_consensus_overview()
            elif self.analysis_mode == "Historical Analysis":
                self._render_historical_analysis()
            elif self.analysis_mode == "Signal Detection":
                self._render_signal_detection()
            elif self.analysis_mode == "Risk Assessment":
                self._render_risk_assessment()
        else:
            self._render_welcome_screen()
    
    def _render_data_status(self):
        """Render data status information"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.consensus_data:
                total_signals = len(st.session_state.consensus_data.get('signals', []))
                st.metric("Active Signals", total_signals)
            else:
                st.metric("Active Signals", "0")
        
        with col2:
            if st.session_state.consensus_data:
                high_consensus = len([
                    s for s in st.session_state.consensus_data.get('signals', [])
                    if s.get('cross_platform_consensus', 0) > self.config.CONSENSUS_THRESHOLDS['high']
                ])
                st.metric("High Consensus", high_consensus)
            else:
                st.metric("High Consensus", "0")
        
        with col3:
            if st.session_state.consensus_data:
                avg_confidence = np.mean([
                    s.get('confidence_score', 0) 
                    for s in st.session_state.consensus_data.get('signals', [])
                ])
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            else:
                st.metric("Avg Confidence", "0%")
        
        with col4:
            if st.session_state.last_refresh:
                st.metric("Last Update", st.session_state.last_refresh.strftime("%H:%M:%S"))
            else:
                st.metric("Last Update", "Never")
    
    def _render_consensus_overview(self):
        """Render real-time consensus overview"""
        st.markdown("### 🎯 Real-time Consensus Analysis")
        
        signals = st.session_state.consensus_data.get('signals', [])
        
        if not signals:
            st.warning("No consensus signals available. Click 'Refresh' to fetch data.")
            return
        
        # Top consensus signals
        st.markdown("#### 🔥 Top Consensus Signals")
        
        # Filter signals based on sidebar settings
        filtered_signals = self._filter_signals(signals)
        
        if not filtered_signals:
            st.info("No signals match current filters.")
            return
        
        # Display top signals
        for i, signal in enumerate(filtered_signals[:5]):  # Top 5 signals
            self._render_consensus_card(signal, i + 1)
        
        # Consensus distribution chart
        st.markdown("#### 📊 Consensus Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Consensus score distribution
            consensus_scores = [s.get('cross_platform_consensus', 0) for s in filtered_signals]
            fig_consensus = px.histogram(
                x=consensus_scores,
                title="Consensus Score Distribution",
                labels={'x': 'Consensus Score', 'y': 'Number of Signals'},
                nbins=20,
                color_discrete_sequence=[self.config.COLORS['primary']]
            )
            fig_consensus.update_layout(
                plot_bgcolor=self.config.COLORS['surface'],
                paper_bgcolor=self.config.COLORS['surface'],
                font_color=self.config.COLORS['text'],
                title_font_color=self.config.COLORS['text']
            )
            st.plotly_chart(fig_consensus, use_container_width=True)
        
        with col2:
            # Platform coverage
            platform_coverage = self._calculate_platform_coverage(filtered_signals)
            fig_platform = px.pie(
                values=list(platform_coverage.values()),
                names=list(platform_coverage.keys()),
                title="Platform Coverage",
                color_discrete_sequence=[
                    self.config.COLORS['primary'],
                    self.config.COLORS['secondary'], 
                    self.config.COLORS['accent']
                ]
            )
            fig_platform.update_layout(
                plot_bgcolor=self.config.COLORS['surface'],
                paper_bgcolor=self.config.COLORS['surface'],
                font_color=self.config.COLORS['text'],
                title_font_color=self.config.COLORS['text']
            )
            st.plotly_chart(fig_platform, use_container_width=True)
    
    def _render_consensus_card(self, signal: Dict, rank: int):
        """Render individual consensus signal card"""
        consensus_score = signal.get('cross_platform_consensus', 0)
        confidence_score = signal.get('confidence_score', 0)
        prediction_strength = signal.get('prediction_strength', 'unknown')
        
        # Determine consensus level
        if consensus_score >= self.config.CONSENSUS_THRESHOLDS['high']:
            consensus_class = "consensus-high"
            consensus_label = "HIGH CONSENSUS"
            consensus_color = self.config.COLORS['success']
        elif consensus_score >= self.config.CONSENSUS_THRESHOLDS['medium']:
            consensus_class = "consensus-medium"
            consensus_label = "MEDIUM CONSENSUS"
            consensus_color = self.config.COLORS['warning']
        else:
            consensus_class = "consensus-low"
            consensus_label = "LOW CONSENSUS"
            consensus_color = self.config.COLORS['danger']
        
        # Determine signal strength class
        signal_class = f"signal-{prediction_strength.lower()}"
        
        # Platform badges
        market_consensus = signal.get('market_consensus', {})
        platform_badges = ""
        for platform, prob in market_consensus.items():
            badge_class = f"platform-{platform.lower()}"
            platform_badges += f'<span class="platform-badge {badge_class}">{platform.title()}: {prob:.1%}</span> '
        
        card_html = f"""
        <div class="consensus-card {consensus_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">#{rank} SIGNAL</div>
                    <div style="font-weight: 600; font-size: 1.1rem; margin: 0.25rem 0;">
                        {signal.get('question', 'Unknown Question')[:80]}...
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="consensus-score" style="color: {consensus_color}; font-size: 1.8rem;">
                        {consensus_score:.1%}
                    </div>
                    <div class="consensus-label" style="color: {consensus_color};">
                        {consensus_label}
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Confidence</div>
                    <div style="font-weight: 600; font-size: 1.2rem; color: var(--brand-primary);">
                        {confidence_score:.1%}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Signal Strength</div>
                    <div class="{signal_class}">
                        {prediction_strength.upper()}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Platform Breakdown</div>
                <div>
                    {platform_badges}
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.875rem; color: var(--text-secondary);">Category:</span>
                    <span style="font-weight: 600; margin-left: 0.5rem;">{signal.get('category', 'other').title()}</span>
                </div>
                <div>
                    <span style="font-size: 0.875rem; color: var(--text-secondary);">Risk-Adjusted Return:</span>
                    <span style="font-weight: 600; margin-left: 0.5rem; color: var(--success);">
                        {signal.get('risk_adjusted_return', 0):.1%}
                    </span>
                </div>
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def _render_historical_analysis(self):
        """Render historical analysis view"""
        st.markdown("### 📈 Historical Consensus Analysis")
        
        st.info("🔄 Historical analysis feature coming soon! This will show consensus trends over time, accuracy tracking, and performance metrics.")
        
        # Placeholder for historical data visualization
        sample_dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        sample_consensus = np.random.normal(0.7, 0.1, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_dates,
            y=sample_consensus,
            mode='lines+markers',
            name='Consensus Score',
            line=dict(color=self.config.COLORS['primary'], width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Sample Consensus Trends (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Consensus Score",
            plot_bgcolor=self.config.COLORS['surface'],
            paper_bgcolor=self.config.COLORS['surface'],
            font_color=self.config.COLORS['text'],
            title_font_color=self.config.COLORS['text']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_signal_detection(self):
        """Render signal detection view"""
        st.markdown("### 🔍 Signal Detection")
        
        signals = st.session_state.consensus_data.get('signals', [])
        filtered_signals = self._filter_signals(signals)
        
        if not filtered_signals:
            st.warning("No signals detected with current filters.")
            return
        
        # Signal metrics
        st.markdown("#### 📊 Signal Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        strong_signals = len([s for s in filtered_signals if s.get('prediction_strength') == 'strong'])
        moderate_signals = len([s for s in filtered_signals if s.get('prediction_strength') == 'moderate'])
        weak_signals = len([s for s in filtered_signals if s.get('prediction_strength') == 'weak'])
        high_confidence = len([s for s in filtered_signals if s.get('confidence_score', 0) > 0.8])
        
        col1.metric("Strong Signals", strong_signals, delta=f"+{strong_signals//2}")
        col2.metric("Moderate Signals", moderate_signals)
        col3.metric("Weak Signals", weak_signals)
        col4.metric("High Confidence", high_confidence)
        
        # Detailed signals table
        st.markdown("#### 📋 Detailed Signals")
        
        signal_data = []
        for signal in filtered_signals:
            signal_data.append({
                'Question': signal.get('question', '')[:60] + "..." if len(signal.get('question', '')) > 60 else signal.get('question', ''),
                'Category': signal.get('category', 'other').title(),
                'Consensus': f"{signal.get('cross_platform_consensus', 0):.1%}",
                'Confidence': f"{signal.get('confidence_score', 0):.1%}",
                'Strength': signal.get('prediction_strength', 'unknown').title(),
                'Risk-Adjusted Return': f"{signal.get('risk_adjusted_return', 0):.1%}",
                'Volume Score': f"{signal.get('volume_weighted_score', 0):.1%}"
            })
        
        if signal_data:
            df = pd.DataFrame(signal_data)
            st.dataframe(df, use_container_width=True)
    
    def _render_risk_assessment(self):
        """Render risk assessment view"""
        st.markdown("### ⚠️ Risk Assessment")
        
        risk_analysis = st.session_state.consensus_data.get('risk_analysis', {})
        
        if not risk_analysis:
            st.warning("No risk assessment data available.")
            return
        
        # Overall risk level
        overall_risk = risk_analysis.get('overall_risk_level', 'unknown')
        
        risk_color = {
            'low': self.config.COLORS['success'],
            'medium': self.config.COLORS['warning'],
            'high': self.config.COLORS['danger']
        }.get(overall_risk, self.config.COLORS['text_secondary'])
        
        st.markdown(f"""
        <div class="consensus-card" style="text-align: center; border-color: {risk_color};">
            <div style="font-size: 1.5rem; font-weight: 700; color: {risk_color}; margin-bottom: 1rem;">
                OVERALL RISK: {overall_risk.upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk factors
        risk_factors = risk_analysis.get('risk_factors', [])
        if risk_factors:
            st.markdown("#### 🚨 Risk Factors")
            for factor in risk_factors:
                st.error(f"⚠️ {factor}")
        
        # Mitigation suggestions
        suggestions = risk_analysis.get('risk_mitigation_suggestions', [])
        if suggestions:
            st.markdown("#### 💡 Risk Mitigation")
            for suggestion in suggestions:
                st.info(f"💡 {suggestion}")
    
    def _render_welcome_screen(self):
        """Render welcome screen when no data is available"""
        st.markdown("### 🚀 Welcome to Probex Consensus Dashboard")
        
        st.markdown("""
        <div class="consensus-card">
            <h4>🎯 Getting Started</h4>
            <p>This dashboard provides real-time cross-platform consensus analysis for prediction markets.</p>
            
            <h5>📊 Key Features:</h5>
            <ul>
                <li><strong>Real-time Consensus:</strong> Aggregate predictions across Polymarket, Kalshi, and Manifold</li>
                <li><strong>Signal Detection:</strong> Identify high-confidence trading opportunities</li>
                <li><strong>Risk Assessment:</strong> Evaluate potential risks and mitigation strategies</li>
                <li><strong>Historical Analysis:</strong> Track consensus trends over time</li>
            </ul>
            
            <h5>🔄 Next Steps:</h5>
            <ol>
                <li>Click the "Refresh" button to fetch latest data</li>
                <li>Adjust filters in the sidebar to focus on specific markets</li>
                <li>Explore different analysis modes using the dropdown</li>
                <li>Monitor high-consensus signals for opportunities</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start button
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            self._refresh_data()
    
    def _filter_signals(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals based on sidebar settings"""
        filtered = []
        
        for signal in signals:
            # Confidence filter
            if signal.get('confidence_score', 0) < self.min_confidence:
                continue
            
            # Consensus filter
            if signal.get('cross_platform_consensus', 0) < self.consensus_threshold:
                continue
            
            # Category filter
            if self.categories and signal.get('category', 'other') not in self.categories:
                continue
            
            filtered.append(signal)
        
        return filtered
    
    def _calculate_platform_coverage(self, signals: List[Dict]) -> Dict[str, int]:
        """Calculate platform coverage from signals"""
        coverage = {'Polymarket': 0, 'Kalshi': 0, 'Manifold': 0}
        
        for signal in signals:
            market_consensus = signal.get('market_consensus', {})
            for platform in market_consensus.keys():
                if platform in coverage:
                    coverage[platform] += 1
        
        return coverage
    
    def _refresh_data(self):
        """Refresh consensus data using simulated data for MVP"""
        try:
            with st.spinner("Generating consensus data..."):
                # Generate simulated markets
                markets = self.data_manager.generate_markets(n=60)
                
                # Compute consensus signals
                signals = self.data_manager.compute_signals(markets)
                
                # Store in session state
                st.session_state.consensus_data = {
                    'signals': signals,
                    'total_markets': len(markets),
                    'timestamp': datetime.now()
                }
                st.session_state.last_refresh = datetime.now()
                
                st.success(f"✅ Generated {len(markets)} markets with {len(signals)} consensus signals")
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            st.error(f"❌ Failed to refresh data: {str(e)}")
    
    def _save_analysis(self):
        """Save current analysis"""
        try:
            if st.session_state.consensus_data:
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"consensus_analysis_{timestamp}.json"
                
                # Prepare data for export
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'filters': {
                        'data_sources': self.data_sources,
                        'consensus_threshold': self.consensus_threshold,
                        'min_confidence': self.min_confidence,
                        'categories': self.categories
                    },
                    'analysis': st.session_state.consensus_data
                }
                
                # Convert to JSON
                json_data = json.dumps(export_data, indent=2, default=str)
                
                # Provide download button
                st.download_button(
                    label="💾 Download Analysis",
                    data=json_data,
                    file_name=filename,
                    mime="application/json"
                )
                
                st.success(f"✅ Analysis saved as {filename}")
            else:
                st.warning("⚠️ No data available to save")
                
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            st.error(f"❌ Failed to save analysis: {str(e)}")

# Main application
def main():
    """Main entry point for the consensus dashboard"""
    dashboard = ConsensusDashboard()
    dashboard.create_dashboard()

if __name__ == "__main__":
    main()