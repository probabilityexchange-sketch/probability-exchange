/**
 * useWebSocket Hook - Real-time WebSocket connection management
 */

import { useEffect, useState, useRef } from 'react';
import { WebSocketManager } from '@/lib/websocket';
import type { Market } from '@/types/market';

interface UseWebSocketReturn {
  connected: boolean;
  error: boolean;
  lastMessage: Market | null;
}

export function useWebSocket(
  onMessage?: (market: Market) => void,
  url?: string
): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(false);
  const [lastMessage, setLastMessage] = useState<Market | null>(null);
  const wsManager = useRef<WebSocketManager | null>(null);

  useEffect(() => {
    // Initialize WebSocket manager
    wsManager.current = new WebSocketManager(url);

    // Set up connection handler
    const cleanupConnection = wsManager.current.onConnection(
      (isConnected, hasError) => {
        setConnected(isConnected);
        setError(hasError || false);
      }
    );

    // Set up message handler
    const cleanupMessage = wsManager.current.onMessage((market) => {
      setLastMessage(market);
      if (onMessage) {
        onMessage(market);
      }
    });

    // Connect
    wsManager.current.connect();

    // Cleanup on unmount
    return () => {
      cleanupConnection();
      cleanupMessage();
      if (wsManager.current) {
        wsManager.current.disconnect();
      }
    };
  }, [url, onMessage]);

  return {
    connected,
    error,
    lastMessage,
  };
}
