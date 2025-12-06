/**
 * Solana Wallet Provider
 * Wraps the app with Solana wallet adapter context
 */

import { useMemo } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { PhantomWalletAdapter, SolflareWalletAdapter } from '@solana/wallet-adapter-wallets';
import { clusterApiUrl } from '@solana/web3.js';
import type { WalletAdapterNetwork } from '@solana/wallet-adapter-base';

// Import Solana wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css';

interface SolanaWalletProviderProps {
  children: React.ReactNode;
}

export function SolanaWalletProvider({ children }: SolanaWalletProviderProps) {
  // You can use 'devnet', 'testnet', or 'mainnet-beta'
  const network: WalletAdapterNetwork = 'mainnet-beta' as WalletAdapterNetwork;

  // You can also provide a custom RPC endpoint
  const endpoint = useMemo(() => {
    // Use custom RPC if provided in environment
    const customRPC = import.meta.env.VITE_SOLANA_RPC_URL;
    if (customRPC) {
      return customRPC;
    }
    // Otherwise use public cluster
    return clusterApiUrl(network);
  }, [network]);

  // Configure supported wallets
  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
      new SolflareWalletAdapter({ network }),
    ],
    [network]
  );

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>{children}</WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
}
