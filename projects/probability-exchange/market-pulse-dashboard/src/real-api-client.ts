import { Market } from './types/market';

// Use relative paths for API calls - nginx proxy handles routing to backend
const API_BASE_URL = '/api/v1';

export class ApiClient {
    async getMarkets(category?: string | null, limit: number = 50): Promise<{ markets: Market[], total: number }> {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        params.append('limit', limit.toString());

        const response = await fetch(`${API_BASE_URL}/markets?${params}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch markets: ${response.statusText}`);
        }
        return response.json();
    }

    async getMarketDetails(marketId: string): Promise<Market> {
        const response = await fetch(`${API_BASE_URL}/markets/${marketId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch market details: ${response.statusText}`);
        }
        return response.json();
    }

    async getNews(category?: string, limit: number = 20) {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        params.append('limit', limit.toString());

        const response = await fetch(`${API_BASE_URL}/news?${params}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch news: ${response.statusText}`);
        }
        return response.json();
    }
}

export const apiClient = new ApiClient();
