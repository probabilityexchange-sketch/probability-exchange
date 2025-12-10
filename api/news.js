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
                summary: article.description || article.content?.substring(0, 200) + '...',
                source: article.source.name,
                timestamp: article.publishedAt,
                sentiment: 'neutral', // Would need sentiment analysis API
                relevantMarkets: [], // Would need to match against markets
                url: article.url,
                imageUrl: article.urlToImage
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
        summary: 'Prediction markets like Polymarket and Kalshi are seeing increased volume and user adoption.',
        source: 'Market Analysis',
        timestamp: new Date().toISOString(),
        sentiment: 'positive',
        relevantMarkets: []
      });
    }

    res.status(200).json(news);

  } catch (error) {
    console.error('News API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
