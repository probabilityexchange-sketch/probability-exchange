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

const getWebSocketUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    // Replace http/https with ws/wss
    const wsUrl = envUrl.replace(/^http/, 'ws');
    return `${wsUrl}/ws`;
  }
  return 'ws://localhost:8000/ws';
};

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
    // Pass onMessage callback to constructor as per our mock implementation
    const targetUrl = url || getWebSocketUrl();
    const manager = new WebSocketManager(targetUrl, (data) => {
         setLastMessage(data);
         if (onMessage) onMessage(data);
    });

    manager.connect();
    wsManager.current = manager;
    setConnected(true);

    // Cleanup on unmount
    return () => {
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
