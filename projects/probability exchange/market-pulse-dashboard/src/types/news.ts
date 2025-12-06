export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  source: string;
  published_at: string;
  url: string;
  sentiment: {
    score: number;  // -1 to 1
    label: 'positive' | 'negative' | 'neutral';
  };
  impact: {
    score: number;  // 0 to 1
    confidence: number;  // 0 to 1
    predicted_direction: 'up' | 'down' | 'neutral';
  };
  related_markets: string[];
  category: string;
  is_breaking: boolean;
  signal_score?: number;
  impact_details?: {
    market_name: string;
    platform: string;
    start_prob: number;
    end_prob: number;
    interpretation: string;
    market_url: string;
  }[];
}

export interface SentimentSummary {
  overall_sentiment: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  high_impact_count: number;
  breaking_count: number;
  total_articles: number;
}

export interface MarketImpact {
  market_id: string;
  overall_sentiment: number;
  impact_score: number;
  article_count: number;
  predicted_direction: 'up' | 'down' | 'neutral';
  confidence: number;
  key_articles: {
    title: string;
    source: string;
    sentiment: string;
    impact: number;
    url: string;
  }[];
}
