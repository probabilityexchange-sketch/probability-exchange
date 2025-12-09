/**
 * useToast Hook - Toast notification management
 */

import { useState, useCallback } from 'react';

export interface ToastData {
  id: string;
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error' | 'breaking';
  duration?: number;
  onClick?: () => void;
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  const addToast = useCallback((toast: Omit<ToastData, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast: ToastData = { ...toast, id };

    setToasts((prev) => [...prev, newToast]);

    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // Convenience methods
  const showInfo = useCallback(
    (title: string, message: string, onClick?: () => void) => {
      return addToast({ title, message, type: 'info', onClick });
    },
    [addToast]
  );

  const showSuccess = useCallback(
    (title: string, message: string, onClick?: () => void) => {
      return addToast({ title, message, type: 'success', onClick });
    },
    [addToast]
  );

  const showWarning = useCallback(
    (title: string, message: string, onClick?: () => void) => {
      return addToast({ title, message, type: 'warning', onClick });
    },
    [addToast]
  );

  const showError = useCallback(
    (title: string, message: string, onClick?: () => void) => {
      return addToast({ title, message, type: 'error', onClick });
    },
    [addToast]
  );

  const showBreaking = useCallback(
    (title: string, message: string, onClick?: () => void) => {
      return addToast({ title, message, type: 'breaking', duration: 8000, onClick });
    },
    [addToast]
  );

  return {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    showInfo,
    showSuccess,
    showWarning,
    showError,
    showBreaking,
  };
}
