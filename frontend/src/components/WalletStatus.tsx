
import { Wallet } from 'lucide-react';

interface WalletStatusProps {
    address: string;
    balance: number;
}

export function WalletStatus({ address, balance }: WalletStatusProps) {
    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/10 rounded-full">
                    <Wallet className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                    <h3 className="text-sm font-medium text-slate-400">CDP Wallet</h3>
                    <p className="text-xs text-slate-500 font-mono">{address ? `${address.slice(0, 6)}...${address.slice(-4)}` : 'Connecting...'}</p>
                </div>
            </div>
            <div className="text-right">
                <p className="text-2xl font-bold text-white">${balance.toFixed(2)}</p>
                <p className="text-xs text-slate-500">USDC Balance</p>
            </div>
        </div>
    );
}
