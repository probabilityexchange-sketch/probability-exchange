/**
 * useMarkets Hook - Market data management with React Query
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Market, MarketsResponse } from '@/types/market';

export function useMarkets(category?: string | null, limit: number = 50) {
  const queryClient = useQueryClient();

  const query = useQuery<MarketsResponse>({
    queryKey: ['markets', category, limit],
    queryFn: () => apiClient.getMarkets({ category, limit }),
    staleTime: 30000, // Consider data stale after 30 seconds
    refetchInterval: 60000, // Refetch every 60 seconds
  });

  const updateMarket = (updatedMarket: Market) => {
    queryClient.setQueryData<MarketsResponse>(
      ['markets', category, limit],
      (oldData) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          markets: oldData.markets.map((market) =>
            market.id === updatedMarket.id
              ? { ...market, ...updatedMarket }
              : market
          ),
        };
      }
    );
  };

  return {
    ...query,
    updateMarket,
  };
}

// Remove useMarketDetails as getMarketDetails is not implemented in generic client
