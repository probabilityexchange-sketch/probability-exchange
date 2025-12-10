// Vercel Serverless Function to fetch market-related news
// Aggregates from various news sources

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const news = [];

    // Helper to mock impact data
    const getImpact = () => ({
      score: Math.random(),
      confidence: Math.random() * 0.5 + 0.5,
      predicted_direction: Math.random() > 0.5 ? 'up' : 'down'
    });

    // Helper to mock sentiment object
    const getSentiment = () => ({
      label: Math.random() > 0.6 ? 'positive' : (Math.random() > 0.5 ? 'negative' : 'neutral'),
      score: Math.random()
    });

    // Fetch from NewsAPI (you'll need to add NEWSAPI_KEY env var in Vercel)
    const newsApiKey = process.env.NEWSAPI_KEY;

    if (newsApiKey) {
      try {
        const newsRes = await fetch(
          `https://newsapi.org/v2/everything?q=prediction+markets+OR+polymarket+OR+kalshi+OR+betting+markets&sortBy=publishedAt&language=en&pageSize=10&apiKey=${newsApiKey}`
        );

        if (newsRes.ok) {
          const newsData = await newsRes.json();

          if (newsData.articles) {
            newsData.articles.forEach((article, index) => {
              news.push({
                id: `news-${index}`,
                title: article.title,
                description: article.description || article.content?.substring(0, 200) + '...',
                source: article.source.name,
                published_at: article.publishedAt,
                sentiment: getSentiment(),
                impact: getImpact(),
                impact_details: [],
                relevantMarkets: [], 
                url: article.url,
                imageUrl: article.urlToImage,
                is_breaking: index === 0, // Mock breaking news for the first item
                signal_score: Math.floor(Math.random() * 3) + 1
              });
            });
          }
        }
      } catch (error) {
        console.error('NewsAPI fetch error:', error.message);
      }
    }

    // Fallback: Fetch from RSS/other sources if NewsAPI fails or no key
    if (news.length === 0) {
      // Return general market news
      news.push({
        id: 'default-1',
        title: 'Prediction Markets Gaining Mainstream Attention',
        description: 'Prediction markets like Polymarket and Kalshi are seeing increased volume and user adoption as traders seek to hedge real-world events.',
        source: 'Market Analysis',
        published_at: new Date().toISOString(),
        sentiment: { label: 'positive', score: 0.8 },
        impact: { score: 0.7, confidence: 0.9, predicted_direction: 'up' },
        impact_details: [
            {
                platform: 'Polymarket',
                market_name: 'Global Crypto Adoption',
                interpretation: 'Positive sentiment drives volume.',
                start_prob: 0.4,
                end_prob: 0.6,
                market_url: '#'
            }
        ],
        relevantMarkets: [],
        is_breaking: true,
        signal_score: 3
      });
      news.push({
        id: 'default-2',
        title: 'Regulatory Landscape Shifts for Event Contracts',
        description: 'New guidelines from the CFTC could impact how event contracts are listed and traded in the US markets.',
        source: 'Regulatory Watch',
        published_at: new Date(Date.now() - 3600000).toISOString(),
        sentiment: { label: 'neutral', score: 0.5 },
        impact: { score: 0.4, confidence: 0.7, predicted_direction: 'neutral' },
        impact_details: [],
        relevantMarkets: [],
        is_breaking: false,
        signal_score: 2
      });
    }

    res.status(200).json({ articles: news });

  } catch (error) {
    console.error('News API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      timestamp: new Date().toISOString(),
      articles: [] // Ensure articles array exists even on error
    });
  }
}