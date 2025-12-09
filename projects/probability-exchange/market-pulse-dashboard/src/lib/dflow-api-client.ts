/**
 * DFlow API Client - Solana Prediction Markets
 * Extension of the main API client for DFlow-specific endpoints
 */

const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }
  return 'http://localhost:8000/api/v1';
};

export interface DFlowMarket {
  id: string;
  platform: string;
  chain: string;
  question: string;
  description?: string;
  category?: string;
  yes_token_mint: string;
  no_token_mint: string;
  yes_price: number;
  no_price: number;
  probability: number;
  volume_24h: number;
  total_volume: number;
  liquidity: number;
  status: string;
  url?: string;
  last_updated: string;
}

export interface SwapQuote {
  in_token: string;
  out_token: string;
  in_amount: string;
  out_amount: string;
  price_impact: number;
  estimated_slippage: number;
  route: any[];
  expires_at: string;
}

export interface Position {
  market_id: string;
  token_mint: string;
  outcome: string;
  shares: string;
  average_price: string;
  current_value: string;
  pnl: string;
  platform: string;
}

export class DFlowAPIClient {
  private apiBase: string;

  constructor(baseUrl?: string) {
    this.apiBase = `${baseUrl || getApiBaseUrl()}/dflow`;
    console.log('DFlow API Client initialized with base URL:', this.apiBase);
  }

  /**
   * Create authentication challenge for Solana wallet
   */
  async createAuthChallenge(walletAddress: string): Promise<{
    challenge: string;
    nonce: string;
    expires_at: string;
    wallet_address: string;
  }> {
    const response = await fetch(`${this.apiBase}/auth/solana/challenge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallet_address: walletAddress }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create challenge: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Verify Solana wallet signature
   */
  async verifySignature(
    walletAddress: string,
    challenge: string,
    signature: string
  ): Promise<{
    success: boolean;
    session_id: string;
    wallet_address: string;
    wallet_type: string;
  }> {
    const response = await fetch(`${this.apiBase}/auth/solana/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_address: walletAddress,
        challenge,
        signature,
      }),
    });

    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get available DFlow prediction markets
   */
  async getMarkets(category?: string, limit: number = 100): Promise<{
    markets: DFlowMarket[];
    total: number;
    platform: string;
    chain: string;
    timestamp: string;
  }> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (category) {
      params.append('category', category);
    }

    const response = await fetch(`${this.apiBase}/markets?${params}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get detailed market information
   */
  async getMarketDetail(marketId: string): Promise<{
    market: DFlowMarket;
    timestamp: string;
  }> {
    const response = await fetch(`${this.apiBase}/markets/${marketId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch market: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get swap quote
   */
  async getSwapQuote(
    inputToken: string,
    outputToken: string,
    amount: string,
    slippageTolerance: number = 0.01
  ): Promise<{ quote: SwapQuote; timestamp: string }> {
    const response = await fetch(`${this.apiBase}/trading/quote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_token: inputToken,
        output_token: outputToken,
        amount,
        slippage_tolerance: slippageTolerance,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get quote: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Execute swap
   */
  async executeSwap(
    inputToken: string,
    outputToken: string,
    amount: string,
    walletAddress: string,
    sessionId: string,
    mode: 'imperative' | 'declarative' = 'declarative',
    slippageTolerance: number = 0.01
  ): Promise<{
    success: boolean;
    mode: string;
    result: any;
    wallet_address: string;
    timestamp: string;
  }> {
    const response = await fetch(`${this.apiBase}/trading/swap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_token: inputToken,
        output_token: outputToken,
        amount,
        wallet_address: walletAddress,
        session_id: sessionId,
        mode,
        slippage_tolerance: slippageTolerance,
      }),
    });

    if (!response.ok) {
      throw new Error(`Swap failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get order status
   */
  async getOrderStatus(orderId: string): Promise<{
    order: any;
    timestamp: string;
  }> {
    const response = await fetch(`${this.apiBase}/trading/order/${orderId}`);

    if (!response.ok) {
      throw new Error(`Failed to get order status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get user positions
   */
  async getUserPositions(
    walletAddress: string,
    sessionId: string
  ): Promise<{
    wallet_address: string;
    positions: Position[];
    total: number;
    timestamp: string;
  }> {
    const response = await fetch(
      `${this.apiBase}/portfolio/positions/${walletAddress}?session_id=${sessionId}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get positions: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get wallet balance
   */
  async getWalletBalance(
    walletAddress: string,
    sessionId: string,
    tokenMint?: string
  ): Promise<{
    wallet_address: string;
    balance: any;
    timestamp: string;
  }> {
    const params = new URLSearchParams({ session_id: sessionId });
    if (tokenMint) {
      params.append('token_mint', tokenMint);
    }

    const response = await fetch(
      `${this.apiBase}/portfolio/balance/${walletAddress}?${params}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get balance: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get available tokens
   */
  async getAvailableTokens(includeDecimals: boolean = true): Promise<{
    tokens: any[];
    total: number;
    timestamp: string;
  }> {
    const response = await fetch(
      `${this.apiBase}/tokens?include_decimals=${includeDecimals}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get tokens: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get trading venues
   */
  async getTradingVenues(): Promise<{
    venues: any[];
    total: number;
    timestamp: string;
  }> {
    const response = await fetch(`${this.apiBase}/venues`);

    if (!response.ok) {
      throw new Error(`Failed to get venues: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: string;
    service: string;
    chain: string;
    version: string;
    api_accessible: boolean;
    timestamp: string;
  }> {
    const response = await fetch(`${this.apiBase}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Export singleton instance
export const dflowClient = new DFlowAPIClient();
