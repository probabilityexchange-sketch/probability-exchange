#!/usr/bin/env python3
"""
News Integration for probex.markets

Real-time news feed with AI analysis for prediction market correlation
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import re
import hashlib
from collections import Counter

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """News article data structure"""
    id: str
    title: str
    content: str
    summary: str
    source: str
    author: str
    published_at: datetime
    url: str
    category: str
    tags: List[str]
    sentiment_score: float
    sentiment_magnitude: float
    relevance_score: float
    impact_prediction: float
    market_correlations: List[str]
    credibility_score: float

@dataclass
class NewsImpact:
    """News impact on prediction markets"""
    article_id: str
    market_id: str
    predicted_direction: str  # 'up', 'down', 'neutral'
    confidence: float
    time_horizon: str  # '1h', '6h', '24h', '7d'
    impact_magnitude: float
    reasoning: str

class NewsAPIClient:
    """NewsAPI client for fetching financial news"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = None
        
        # Source credibility weights
        self.source_weights = {
            'reuters.com': 1.0,
            'bloomberg.com': 0.95,
            'cnbc.com': 0.9,
            'wsj.com': 0.9,
            'marketwatch.com': 0.85,
            'finance.yahoo.com': 0.8,
            'thestreet.com': 0.75,
            'coindesk.com': 0.8,
            'decrypt.co': 0.75,
            'cointelegraph.com': 0.7
        }
    
    async def initialize(self):
        """Initialize the API client"""
        self.session = aiohttp.ClientSession()
        logger.info("NewsAPI client initialized")
    
    async def fetch_financial_news(self, 
                                   categories: List[str] = None,
                                   sources: List[str] = None,
                                   limit: int = 50) -> List[NewsArticle]:
        """Fetch financial news articles"""
        try:
            if not categories:
                categories = ['business', 'technology']
            
            articles = []
            
            # Fetch from NewsAPI
            if self.api_key:
                async with self.session.get(
                    f"{self.base_url}/everything",
                    params={
                        'apiKey': self.api_key,
                        'q': ' OR '.join(categories),
                        'language': 'en',
                        'sortBy': 'publishedAt',
                        'pageSize': limit,
                        'domains': ','.join(sources) if sources else None
                    }
                ) as response:
                    data = await response.json()
                    if data.get('status') == 'ok':
                        articles.extend(await self._parse_newsapi_articles(data.get('articles', [])))
            
            # Add sample articles if no API key or no results
            if not articles:
                articles = await self._generate_sample_news(categories, limit // 2)
            
            logger.info(f"Fetched {len(articles)} news articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return await self._generate_sample_news(categories, limit)
    
    async def _parse_newsapi_articles(self, raw_articles: List[Dict]) -> List[NewsArticle]:
        """Parse NewsAPI response into NewsArticle objects"""
        articles = []
        
        for article in raw_articles:
            try:
                # Generate article ID
                article_id = hashlib.md5(
                    (article.get('title', '') + article.get('url', '')).encode()
                ).hexdigest()
                
                # Extract domain for credibility scoring
                domain = self._extract_domain(article.get('url', ''))
                credibility = self.source_weights.get(domain, 0.5)
                
                # Create NewsArticle object
                news_article = NewsArticle(
                    id=article_id,
                    title=article.get('title', ''),
                    content=article.get('content', ''),
                    summary=article.get('description', ''),
                    source=article.get('source', {}).get('name', domain),
                    author=article.get('author', 'Unknown'),
                    published_at=datetime.fromisoformat(
                        article.get('publishedAt', '').replace('Z', '+00:00')
                    ) if article.get('publishedAt') else datetime.now(),
                    url=article.get('url', ''),
                    category=self._categorize_article(article.get('title', '')),
                    tags=[],
                    sentiment_score=0.0,
                    sentiment_magnitude=0.0,
                    relevance_score=0.0,
                    impact_prediction=0.0,
                    market_correlations=[],
                    credibility_score=credibility
                )
                
                articles.append(news_article)
                
            except Exception as e:
                logger.error(f"Error parsing article: {e}")
                continue
        
        return articles
    
    async def _generate_sample_news(self, categories: List[str], limit: int) -> List[NewsArticle]:
        """Generate sample news articles for testing"""
        sample_articles = [
            {
                'title': 'Federal Reserve Signals Potential Interest Rate Cut in Q4',
                'content': 'Federal Reserve officials hinted at a potential interest rate cut in the fourth quarter, citing cooling inflation and labor market concerns...',
                'source': 'Reuters',
                'category': 'economy',
                'published_at': datetime.now() - timedelta(hours=2),
                'url': 'https://reuters.com/markets/fed-rate-cut-q4',
                'author': 'Financial Team'
            },
            {
                'title': 'Bitcoin Surges Above $95,000 on Institutional Adoption',
                'content': 'Bitcoin price jumped 8% in early trading as major institutional investors announced significant Bitcoin allocations...',
                'source': 'CoinDesk',
                'category': 'crypto',
                'published_at': datetime.now() - timedelta(hours=1),
                'url': 'https://coindesk.com/bitcoin-surge-institutional',
                'author': 'Crypto Reporter'
            },
            {
                'title': 'Tesla Reports Strong Q3 Earnings, Stock Hits Record High',
                'content': 'Tesla exceeded Q3 earnings expectations with record vehicle deliveries and improved margins...',
                'source': 'Bloomberg',
                'category': 'technology',
                'published_at': datetime.now() - timedelta(hours=3),
                'url': 'https://bloomberg.com/tesla-earnings-record',
                'author': 'Tech Analyst'
            },
            {
                'title': 'Apple Announces AI-Powered iPhone Features for 2025',
                'content': 'Apple unveiled new AI capabilities for iPhone 17, including advanced Siri improvements and autonomous features...',
                'source': 'CNBC',
                'category': 'technology',
                'published_at': datetime.now() - timedelta(hours=4),
                'url': 'https://cnbc.com/apple-ai-features-2025',
                'author': 'Consumer Tech'
            },
            {
                'title': 'Oil Prices Drop on Increased US Production',
                'content': 'Crude oil futures fell 3% as US production reached new highs and OPEC+ production cuts show signs of weakening...',
                'source': 'MarketWatch',
                'category': 'economy',
                'published_at': datetime.now() - timedelta(hours=5),
                'url': 'https://marketwatch.com/oil-prices-drop-us-production',
                'author': 'Energy Reporter'
            }
        ]
        
        articles = []
        for i, sample in enumerate(sample_articles[:limit]):
            article_id = hashlib.md5((sample['title'] + sample['url']).encode()).hexdigest()
            domain = self._extract_domain(sample['url'])
            
            article = NewsArticle(
                id=article_id,
                title=sample['title'],
                content=sample['content'],
                summary=sample['content'][:100] + '...',
                source=sample['source'],
                author=sample['author'],
                published_at=sample['published_at'],
                url=sample['url'],
                category=sample['category'],
                tags=[],
                sentiment_score=0.0,
                sentiment_magnitude=0.0,
                relevance_score=0.0,
                impact_prediction=0.0,
                market_correlations=[],
                credibility_score=self.source_weights.get(domain, 0.5)
            )
            articles.append(article)
        
        return articles
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return 'unknown.com'
    
    def _categorize_article(self, title: str) -> str:
        """Categorize article based on title/content"""
        title_lower = title.lower()
        
        categories = {
            'politics': ['election', 'president', 'congress', 'senate', 'government', 'policy'],
            'economy': ['fed', 'inflation', 'gdp', 'recession', 'interest rate', 'economy'],
            'technology': ['apple', 'tesla', 'microsoft', 'google', 'ai', 'tech', 'bitcoin'],
            'crypto': ['bitcoin', 'crypto', 'ethereum', 'blockchain', 'defi'],
            'stocks': ['stock', 'earnings', 'revenue', 'profit', 'share price']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logger.info("NewsAPI client cleaned up")

class SentimentAnalyzer:
    """AI-powered sentiment analysis for news articles"""
    
    def __init__(self):
        self.sentiment_keywords = {
            'positive': ['surge', 'rally', 'gain', 'rise', 'boost', 'record', 'strong', 'beat', 'exceed', 'growth'],
            'negative': ['fall', 'drop', 'decline', 'crash', 'loss', 'weak', 'miss', 'disappoint', 'concern', 'risk'],
            'market_moving': ['fed', 'rate', 'cut', 'raise', 'policy', 'announcement', 'breakthrough', 'scandal', 'merger', 'acquisition']
        }
    
    async def analyze_sentiment(self, article: NewsArticle) -> NewsArticle:
        """Analyze sentiment of a news article"""
        try:
            # Combine title and content for analysis
            text = f"{article.title} {article.content}"
            
            # Simple keyword-based sentiment analysis
            sentiment_score = self._keyword_sentiment(text)
            sentiment_magnitude = self._calculate_magnitude(text)
            
            # Enhanced keyword-based scoring
            text_lower = text.lower()
            positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
            negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
            
            # Market-moving indicator
            market_moving_indicators = sum(1 for word in self.sentiment_keywords['market_moving'] if word in text_lower)
            
            # Adjust sentiment based on keywords
            keyword_adjustment = (positive_count - negative_count) * 0.1
            sentiment_score += keyword_adjustment
            
            # Market moving articles get enhanced magnitude
            if market_moving_indicators > 0:
                sentiment_magnitude = min(1.0, sentiment_magnitude + 0.2)
            
            # Store results
            article.sentiment_score = max(-1.0, min(1.0, sentiment_score))
            article.sentiment_magnitude = sentiment_magnitude
            
            return article
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return article
    
    def _keyword_sentiment(self, text: str) -> float:
        """Simple keyword-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = self.sentiment_keywords['positive']
        negative_words = self.sentiment_keywords['negative']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_magnitude(self, text: str) -> float:
        """Calculate sentiment magnitude based on emotion words"""
        emotion_words = ['very', 'extremely', 'highly', 'significantly', 'dramatically', 'sharply', 'strongly']
        text_lower = text.lower()
        
        emotion_count = sum(1 for word in emotion_words if word in text_lower)
        return min(1.0, 0.3 + emotion_count * 0.2)

class MarketNewsCorrelator:
    """Correlate news articles with prediction markets"""
    
    def __init__(self):
        self.keyword_mappings = {
            'fed': ['will fed cut interest rates', 'will fed raise rates', 'will interest rates change'],
            'bitcoin': ['will bitcoin reach', 'will bitcoin exceed', 'will crypto reach'],
            'tesla': ['will tesla stock', 'will tesla price', 'will tesla reach'],
            'apple': ['will apple stock', 'will apple reach', 'will iphone'],
            'election': ['will trump win', 'will biden win', 'will election'],
            'recession': ['will recession', 'will gdp', 'will economy']
        }
        
        self.category_mappings = {
            'politics': ['election', 'government', 'policy', 'president'],
            'economy': ['fed', 'interest', 'inflation', 'gdp', 'recession'],
            'technology': ['tesla', 'apple', 'microsoft', 'google', 'ai', 'tech'],
            'crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain'],
            'sports': ['olympics', 'super bowl', 'world cup', 'championship'],
            'entertainment': ['oscar', 'grammy', 'movie', 'celebrity']
        }
    
    def correlate_article_with_markets(self, article: NewsArticle, markets_data: List[Dict]) -> List[str]:
        """Find prediction markets that might be affected by this article"""
        try:
            correlations = []
            text = f"{article.title} {article.content}".lower()
            
            # Check keyword correlations
            for keyword, market_patterns in self.keyword_mappings.items():
                if keyword in text:
                    for market in markets_data:
                        market_text = market.get('question', '').lower()
                        if any(pattern in market_text for pattern in market_patterns):
                            correlations.append(market.get('id'))
            
            # Check category correlations
            for market in markets_data:
                market_category = market.get('category', '').lower()
                if market_category in self.category_mappings.get(article.category, []):
                    if market.get('id') not in correlations:
                        correlations.append(market.get('id'))
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error correlating article with markets: {e}")
            return []

class ImpactPredictor:
    """AI model to predict market impact of news"""
    
    def __init__(self):
        self.impact_thresholds = {
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    async def predict_impact(self, article: NewsArticle, market_correlations: List[str]) -> List[NewsImpact]:
        """Predict the impact of news on correlated markets"""
        try:
            impacts = []
            
            for market_id in market_correlations:
                # Calculate impact based on multiple factors
                sentiment_impact = abs(article.sentiment_score) * article.sentiment_magnitude
                credibility_impact = article.credibility_score
                time_factor = self._calculate_time_factor(article.published_at)
                relevance_boost = 0.1 if len(article.market_correlations) > 1 else 0
                
                # Combined impact score
                impact_score = (sentiment_impact * 0.4 + credibility_impact * 0.3 + time_factor * 0.2 + relevance_boost)
                
                # Determine direction
                if article.sentiment_score > 0.1:
                    direction = 'up'
                elif article.sentiment_score < -0.1:
                    direction = 'down'
                else:
                    direction = 'neutral'
                
                # Calculate confidence
                confidence = min(1.0, impact_score * article.credibility_score)
                
                # Determine time horizon based on impact magnitude
                if impact_score > 0.7:
                    time_horizon = '1h'
                elif impact_score > 0.5:
                    time_horizon = '6h'
                elif impact_score > 0.3:
                    time_horizon = '24h'
                else:
                    time_horizon = '7d'
                
                impact = NewsImpact(
                    article_id=article.id,
                    market_id=market_id,
                    predicted_direction=direction,
                    confidence=confidence,
                    time_horizon=time_horizon,
                    impact_magnitude=impact_score,
                    reasoning=self._generate_reasoning(article, direction, impact_score)
                )
                
                impacts.append(impact)
            
            return impacts
            
        except Exception as e:
            logger.error(f"Error predicting impact: {e}")
            return []
    
    def _calculate_time_factor(self, published_at: datetime) -> float:
        """Calculate time-based impact factor"""
        hours_ago = (datetime.now() - published_at).total_seconds() / 3600
        
        if hours_ago < 1:
            return 1.0  # Very recent news
        elif hours_ago < 6:
            return 0.8  # Recent news
        elif hours_ago < 24:
            return 0.6  # News from today
        elif hours_ago < 72:
            return 0.4  # News from last few days
        else:
            return 0.2  # Older news
    
    def _generate_reasoning(self, article: NewsArticle, direction: str, impact: float) -> str:
        """Generate reasoning for the impact prediction"""
        reasons = []
        
        if abs(article.sentiment_score) > 0.3:
            if article.sentiment_score > 0:
                reasons.append("positive sentiment detected")
            else:
                reasons.append("negative sentiment detected")
        
        if article.credibility_score > 0.8:
            reasons.append("high credibility source")
        elif article.credibility_score < 0.5:
            reasons.append("lower credibility source")
        
        if len(article.market_correlations) > 2:
            reasons.append("multiple market correlations")
        
        if impact > 0.7:
            reasons.append("high impact potential")
        elif impact < 0.3:
            reasons.append("low impact potential")
        
        return "; ".join(reasons) if reasons else "baseline analysis"

class NewsIntegrationEngine:
    """Main news integration engine"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.news_client = NewsAPIClient(self.config.get('newsapi_key'))
        self.sentiment_analyzer = SentimentAnalyzer()
        self.correlator = MarketNewsCorrelator()
        self.impact_predictor = ImpactPredictor()
        
        # Cache for processed articles
        self.article_cache = {}
        self.impact_cache = {}
    
    async def initialize(self):
        """Initialize the news integration engine"""
        await self.news_client.initialize()
        logger.info("News integration engine initialized")
    
    async def process_news_for_markets(self, markets_data: List[Dict]) -> Tuple[List[NewsArticle], List[NewsImpact]]:
        """Process news and predict market impacts"""
        try:
            # Fetch latest news
            articles = await self.news_client.fetch_financial_news()
            
            # Analyze sentiment for each article
            processed_articles = []
            all_impacts = []
            
            for article in articles:
                # Analyze sentiment
                article = await self.sentiment_analyzer.analyze_sentiment(article)
                
                # Find market correlations
                article.market_correlations = self.correlator.correlate_article_with_markets(article, markets_data)
                
                # Predict impacts
                if article.market_correlations:
                    impacts = await self.impact_predictor.predict_impact(article, article.market_correlations)
                    all_impacts.extend(impacts)
                
                # Filter for relevant articles only
                if article.market_correlations or abs(article.sentiment_score) > 0.2:
                    processed_articles.append(article)
            
            # Sort by impact and recency
            processed_articles.sort(key=lambda x: (x.credibility_score * abs(x.sentiment_score)), reverse=True)
            
            logger.info(f"Processed {len(processed_articles)} relevant articles with {len(all_impacts)} impact predictions")
            return processed_articles, all_impacts
            
        except Exception as e:
            logger.error(f"Error processing news for markets: {e}")
            return [], []
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.news_client.cleanup()
        logger.info("News integration engine cleaned up")

# Utility functions for news analysis
def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple frequency analysis"""
    # Simple word frequency approach
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    return list(Counter(filtered_words).most_common(max_keywords))

if __name__ == "__main__":
    # Example usage
    async def main():
        engine = NewsIntegrationEngine()
        await engine.initialize()
        
        # Sample markets data
        sample_markets = [
            {
                'id': 'bitcoin_100k',
                'question': 'Will Bitcoin reach $100,000 by end of 2024?',
                'category': 'crypto'
            },
            {
                'id': 'fed_rate_cut',
                'question': 'Will the Fed cut interest rates in 2024?',
                'category': 'economy'
            }
        ]
        
        articles, impacts = await engine.process_news_for_markets(sample_markets)
        
        print(f"Found {len(articles)} relevant articles")
        print(f"Generated {len(impacts)} impact predictions")
        
        await engine.cleanup()
    
    asyncio.run(main())
