
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Unlock, TrendingUp, Twitter, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnalystData {
    score: number;
    insight: string;
    [key: string]: any;
}

interface AnalystCardProps {
    type: 'technical' | 'sentiment' | 'onchain';
    price: number;
    status: 'LOCKED' | 'UNLOCKING' | 'UNLOCKED';
    data?: AnalystData;
}

const CONFIG = {
    technical: {
        icon: TrendingUp,
        title: "Technical Analysis",
        color: "text-cyan-400",
        bg: "bg-cyan-500/10",
        border: "border-cyan-500/20"
    },
    sentiment: {
        icon: Twitter,
        title: "Sentiment Analysis",
        color: "text-purple-400",
        bg: "bg-purple-500/10",
        border: "border-purple-500/20"
    },
    onchain: {
        icon: Activity,
        title: "On-Chain Analysis",
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/20"
    }
};

export function AnalystCard({ type, price, status, data }: AnalystCardProps) {
    const config = CONFIG[type];
    const Icon = config.icon;

    return (
        <div className={cn(
            "relative overflow-hidden rounded-xl border p-6 transition-all duration-300",
            "bg-slate-900/50 backdrop-blur-sm",
            config.border,
            status === 'UNLOCKED' ? 'shadow-lg shadow-blue-500/5' : ''
        )}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={cn("p-2 rounded-lg", config.bg)}>
                        <Icon className={cn("w-5 h-5", config.color)} />
                    </div>
                    <h3 className="font-semibold text-slate-200">{config.title}</h3>
                </div>
                {status === 'UNLOCKED' ? (
                    <Unlock className="w-4 h-4 text-slate-500" />
                ) : (
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-800 border border-slate-700">
                        <span className="text-xs font-mono text-slate-400">${price.toFixed(2)}</span>
                    </div>
                )}
            </div>

            {/* Content Area */}
            <div className="relative min-h-[120px]">
                <AnimatePresence mode="wait">
                    {status === 'LOCKED' || status === 'UNLOCKING' ? (
                        <motion.div
                            key="locked"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 flex flex-col items-center justify-center space-y-3"
                        >
                            <div className="p-3 bg-slate-800/50 rounded-full border border-slate-700 backdrop-blur-sm">
                                {status === 'UNLOCKING' ? (
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    >
                                        <Unlock className="w-6 h-6 text-blue-400" />
                                    </motion.div>
                                ) : (
                                    <Lock className="w-6 h-6 text-slate-500" />
                                )}
                            </div>
                            <p className="text-sm text-slate-500 font-mono">
                                {status === 'UNLOCKING' ? 'Processing Payment...' : 'Payment Required (402)'}
                            </p>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="unlocked"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-4"
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-400">Score</span>
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-24 bg-slate-800 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${(data?.score || 0) * 100}%` }}
                                            className={cn("h-full", config.bg.replace('/10', ''))}
                                        />
                                    </div>
                                    <span className={cn("text-sm font-bold", config.color)}>
                                        {((data?.score || 0) * 100).toFixed(0)}%
                                    </span>
                                </div>
                            </div>
                            <p className="text-sm text-slate-300 leading-relaxed">
                                {data?.insight}
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
