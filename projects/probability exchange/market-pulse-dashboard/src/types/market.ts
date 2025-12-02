/**
 * Market Types - TypeScript interfaces for Market Pulse Dashboard
 * Aligned with backend API schema
 */

export type Platform = 'kalshi' | 'polymarket' | 'manifold';
export type MarketStatus = 'active' | 'open' | 'closed' | 'resolved';
export type Category = 'politics' | 'sports' | 'economics' | 'crypto' | 'stocks' | 'other';

export interface Market {
  id: string;

  // Backend uses 'question' as primary field
  question: string;

  // Keep title for backward compatibility (map from question)
  title?: string;

  description?: string;
  category: Category;
  platform: Platform;
  status: MarketStatus;

  // Pricing
  current_price: number;
  probability?: number;

  // Volume & Trading
  volume_24h?: number;
  change_24h?: number;
  total_volume?: number;
  liquidity?: number;

  // Market Type
  market_type?: string;
  outcomes?: string[] | null;

  // Timestamps
  open_time?: string;
  close_time?: string;
  resolution_date?: string;
  created_at?: string;
  updated_at?: string;
  last_updated?: string;

  // Additional fields
  url?: string;
}

export interface APIStatus {
  status: 'healthy' | 'degraded' | 'error' | 'operational';
  timestamp?: string;
  platforms?: {
    [key: string]: {
      connected: boolean;
      last_check: string;
      status: string;
    };
  };
  aggregator?: {
    clients_count: number;
    initialized: boolean;
  };
  websocket?: {
    active_connections: number;
    status: string;
  };
}

export interface MarketsResponse {
  markets: Market[];
  total: number;
  timestamp?: string;
  error?: string;
}

export interface WebSocketMessage {
  type: 'market_update' | 'ack' | 'error' | 'connection';
  data?: Market | { connected: boolean; error?: boolean };
  timestamp?: string;
}

export interface MarketFilters {
  category?: Category;
  platform?: Platform;
  status?: MarketStatus;
  searchTerm?: string;
  limit?: number;
}

export interface PriceChange {
  value: number;
  percentage: number;
  timestamp: string;
}
