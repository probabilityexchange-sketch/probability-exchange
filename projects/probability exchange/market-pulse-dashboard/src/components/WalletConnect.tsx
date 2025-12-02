import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wallet, X, AlertCircle, CheckCircle, ExternalLink } from 'lucide-react';
import { WalletType, WalletInfo, WalletError } from '../types/wallet';
import { handleWalletError, formatAddress, isWalletInstalled } from '../lib/walletErrors';

interface WalletConnectProps {
  onConnect: (wallet: WalletInfo) => void;
  onDisconnect: () => void;
  connectedWallet?: WalletInfo;
}

const walletOptions = [
  {
    type: 'phantom' as WalletType,
    name: 'Phantom',
    icon: '👻',
    description: 'Solana wallet',
    installUrl: 'https://phantom.app',
    network: 'solana',
  },
  {
    type: 'solflare' as WalletType,
    name: 'Solflare',
    icon: '🔥',
    description: 'Solana wallet',
    installUrl: 'https://solflare.com',
    network: 'solana',
  },
  {
    type: 'metamask' as WalletType,
    name: 'MetaMask',
    icon: '🦊',
    description: 'Ethereum wallet',
    installUrl: 'https://metamask.io',
    network: 'ethereum',
  },
];

export default function WalletConnect({ onConnect, onDisconnect, connectedWallet }: WalletConnectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [connecting, setConnecting] = useState<WalletType | null>(null);
  const [error, setError] = useState<WalletError | null>(null);

  const connectWallet = async (walletType: WalletType) => {
    setConnecting(walletType);
    setError(null);

    try {
      // Check if wallet is installed
      if (!isWalletInstalled(walletType)) {
        throw new Error(`${walletType} is not installed`);
      }

      let address: string;
      let network: string;

      // Connect based on wallet type
      if (walletType === 'phantom') {
        const phantom = (window as any).phantom?.solana;
        const response = await phantom.connect();
        address = response.publicKey.toString();
        network = 'solana';
      } else if (walletType === 'solflare') {
        const solflare = (window as any).solflare;
        await solflare.connect();
        address = solflare.publicKey.toString();
        network = 'solana';
      } else if (walletType === 'metamask') {
        const ethereum = (window as any).ethereum;
        const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
        address = accounts[0];
        network = 'ethereum';
      } else {
        throw new Error('Unsupported wallet type');
      }

      // Create wallet info
      const walletInfo: WalletInfo = {
        type: walletType,
        address,
        network,
        connected: true,
      };

      onConnect(walletInfo);
      setIsOpen(false);
      setConnecting(null);
    } catch (err: any) {
      const walletError = handleWalletError(err, walletType);
      setError(walletError);
      setConnecting(null);
    }
  };

  const handleDisconnect = () => {
    onDisconnect();
    setIsOpen(false);
  };

  return (
    <>
      {/* Connect Button */}
      {!connectedWallet ? (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
        >
          <Wallet className="w-4 h-4" />
          <span>Connect Wallet</span>
        </motion.button>
      ) : (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsOpen(true)}
          className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
        >
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="font-mono">{formatAddress(connectedWallet.address)}</span>
        </motion.button>
      )}

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            />

            {/* Modal Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl z-50 p-6"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Wallet className="w-5 h-5" />
                  {connectedWallet ? 'Wallet Connected' : 'Connect Wallet'}
                </h2>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-zinc-400" />
                </button>
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3"
                >
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-red-400 text-sm font-medium">{error.message}</p>
                    {error.code === 'WALLET_NOT_INSTALLED' && (
                      <a
                        href={walletOptions.find(w => w.type === error.type)?.installUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-red-300 text-xs underline mt-1 inline-flex items-center gap-1 hover:text-red-200"
                      >
                        Install Wallet
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Connected Wallet Info */}
              {connectedWallet ? (
                <div className="space-y-4">
                  <div className="p-4 bg-zinc-800/50 rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-zinc-400">Wallet</span>
                      <span className="text-white font-medium capitalize">
                        {walletOptions.find(w => w.type === connectedWallet.type)?.icon}{' '}
                        {connectedWallet.type}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-zinc-400">Address</span>
                      <span className="text-white font-mono text-sm">
                        {formatAddress(connectedWallet.address, 6)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-zinc-400">Network</span>
                      <span className="text-white font-medium capitalize">
                        {connectedWallet.network}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={handleDisconnect}
                    className="w-full px-4 py-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg font-medium transition-colors"
                  >
                    Disconnect Wallet
                  </button>
                </div>
              ) : (
                /* Wallet Options */
                <div className="space-y-3">
                  {walletOptions.map((wallet) => {
                    const installed = isWalletInstalled(wallet.type);
                    const isConnecting = connecting === wallet.type;

                    return (
                      <motion.button
                        key={wallet.type}
                        whileHover={{ scale: installed ? 1.02 : 1 }}
                        whileTap={{ scale: installed ? 0.98 : 1 }}
                        onClick={() => installed && connectWallet(wallet.type)}
                        disabled={!installed || isConnecting}
                        className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                          installed
                            ? 'bg-zinc-800/50 border-zinc-700 hover:border-blue-500/50 hover:bg-zinc-800'
                            : 'bg-zinc-900 border-zinc-800 opacity-50 cursor-not-allowed'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <span className="text-3xl">{wallet.icon}</span>
                            <div>
                              <div className="text-white font-semibold">{wallet.name}</div>
                              <div className="text-xs text-zinc-500">{wallet.description}</div>
                            </div>
                          </div>

                          {isConnecting ? (
                            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                          ) : !installed ? (
                            <a
                              href={wallet.installUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="text-xs text-blue-400 hover:text-blue-300 underline flex items-center gap-1"
                            >
                              Install
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ) : (
                            <CheckCircle className="w-5 h-5 text-green-400" />
                          )}
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
