export type WalletType = 'phantom' | 'solflare' | 'metamask';

export interface WalletInfo {
  type: WalletType;
  address: string;
  balance?: number;
  network?: string;
  connected: boolean;
}

export interface WalletError {
  code: string;
  message: string;
  type: WalletType;
}

export interface Transaction {
  id: string;
  type: 'deposit' | 'withdrawal' | 'trade' | 'transfer';
  amount: number;
  currency: string;
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: string;
  from?: string;
  to?: string;
  hash?: string;
  fee?: number;
}

export interface WalletAdapter {
  connect: () => Promise<string>;
  disconnect: () => Promise<void>;
  getBalance: (address: string) => Promise<number>;
  signMessage: (message: string) => Promise<string>;
  signTransaction: (transaction: any) => Promise<any>;
}
