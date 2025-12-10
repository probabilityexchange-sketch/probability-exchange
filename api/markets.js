// Vercel Serverless Function to fetch live market data
// Aggregates data from Polymarket, Kalshi, and Manifold

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const markets = [];

    // Fetch from Polymarket
    try {
      const polymarketRes = await fetch('https://clob.polymarket.com/markets', {
        headers: {
          'Accept': 'application/json'
        }
      });

      if (polymarketRes.ok) {
        const polymarketData = await polymarketRes.json();

        // Take top 10 markets by volume
        const topMarkets = polymarketData
          .filter(m => m.active && !m.closed)
          .sort((a, b) => parseFloat(b.volume || 0) - parseFloat(a.volume || 0))
          .slice(0, 10);

        topMarkets.forEach(market => {
          markets.push({
            id: `polymarket-${market.condition_id}`,
            title: market.question,
            description: market.description || market.question,
            probability: parseFloat(market.outcome_prices?.[0] || 0),
            volume: parseFloat(market.volume || 0),
            liquidity: parseFloat(market.liquidity || 0),
            source: 'Polymarket',
            category: market.category || 'Politics',
            endDate: market.end_date_iso || market.end_date,
            lastUpdate: new Date().toISOString(),
            url: `https://polymarket.com/event/${market.slug}`,
            priceHistory: [] // Would need historical API for this
          });
        });
      }
    } catch (error) {
      console.error('Polymarket fetch error:', error.message);
    }

    // Fetch from Kalshi (public API)
    try {
      const kalshiRes = await fetch('https://trading-api.kalshi.com/trade-api/v2/markets', {
        headers: {
          'Accept': 'application/json'
        }
      });

      if (kalshiRes.ok) {
        const kalshiData = await kalshiRes.json();

        if (kalshiData.markets) {
          // Take top 5 Kalshi markets
          kalshiData.markets.slice(0, 5).forEach(market => {
            if (market.status === 'active') {
              const yesPrice = market.yes_sub_title ? parseFloat(market.last_price) / 100 : 0.5;

              markets.push({
                id: `kalshi-${market.ticker}`,
                title: market.title,
                description: market.subtitle || market.title,
                probability: yesPrice,
                volume: market.volume || 0,
                liquidity: market.open_interest || 0,
                source: 'Kalshi',
                category: market.category || 'Finance',
                endDate: market.expiration_time,
                lastUpdate: new Date().toISOString(),
                url: `https://kalshi.com/markets/${market.ticker}`,
                priceHistory: []
              });
            }
          });
        }
      }
    } catch (error) {
      console.error('Kalshi fetch error:', error.message);
    }

    // If no markets fetched, return error
    if (markets.length === 0) {
      return res.status(503).json({
        error: 'Unable to fetch market data from any source',
        timestamp: new Date().toISOString()
      });
    }

    // Return aggregated markets
    res.status(200).json({ markets: markets });

  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
