
import { motion } from 'framer-motion';
import { Shield, Lock } from 'lucide-react';

interface BiteVaultProps {
    status: 'IDLE' | 'ENCRYPTED' | 'EXECUTING';
    txHash?: string;
    condition?: string;
}

export function BiteVault({ status, txHash, condition }: BiteVaultProps) {
    if (status === 'IDLE') return null;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-8 p-1 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-blue-500/20 rounded-2xl"
        >
            <div className="bg-slate-900/90 backdrop-blur-xl rounded-xl p-6 border border-slate-700/50">
                <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                        <Shield className="w-8 h-8 text-blue-400" />
                    </div>

                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-bold text-white">Zero-Knowledge Vault</h3>
                            <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 rounded-full border border-blue-500/20">
                                <Lock className="w-3 h-3 text-blue-400" />
                                <span className="text-xs font-bold text-blue-400">BITE v2 ENCRYPTED</span>
                            </div>
                        </div>

                        <p className="text-slate-400 leading-relaxed">
                            Strategy has been generated and encrypted. It is currently sitting in the mempool, waiting for the
                            condition <span className="text-white font-mono bg-slate-800 px-1 rounded">{condition || 'CONFIDENCE > 0.8'}</span> to be met.
                        </p>

                        {txHash && (
                            <div className="mt-4 pt-4 border-t border-slate-800">
                                <div className="flex items-center justify-between text-xs font-mono">
                                    <span className="text-slate-500">TX ID</span>
                                    <span className="text-blue-400">{txHash}</span>
                                </div>
                                <div className="mt-2 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-blue-500"
                                        animate={{
                                            x: ["-100%", "100%"]
                                        }}
                                        transition={{
                                            repeat: Infinity,
                                            duration: 1.5,
                                            ease: "linear"
                                        }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
