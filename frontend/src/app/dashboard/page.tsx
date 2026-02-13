'use client';

import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/lib/websocket';

type AnalystStatus = 'LOCKED' | 'UNLOCKING' | 'UNLOCKED';

interface AnalystState {
  status: AnalystStatus;
  price: number;
  data?: any;
}

interface AuditEntry {
  timestamp: string;
  tool: string;
  amount: number;
  tx_hash: string;
  justification: string;
}

interface TraceStep {
  icon: string;
  label: string;
  detail: string;
  time: string;
  status: 'pending' | 'active' | 'completed';
}

// SVG Gauge component
function Gauge({ value, max, color, label }: { value: number; max: number; color: string; label: string }) {
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct);

  return (
    <div className="risk-gauge">
      <div className="gauge-circle">
        <svg viewBox="0 0 56 56">
          <circle className="gauge-bg" cx="28" cy="28" r={radius} />
          <circle
            className="gauge-fill"
            cx="28" cy="28" r={radius}
            stroke={color}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <span className="gauge-value">{Math.round(pct * 100)}%</span>
      </div>
      <span className="gauge-label">{label}</span>
    </div>
  );
}

// Sparkline component
function Sparkline({ data, color }: { data: number[]; color: string }) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 400;
  const h = 60;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * (h - 6) - 3}`).join(' ');
  const areaPoints = `0,${h} ${points} ${w},${h}`;

  return (
    <div className="sparkline-container">
      <svg className="sparkline-svg" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={areaPoints} fill="url(#sparkGrad)" />
        <polyline points={points} fill="none" stroke={color} strokeWidth="2" />
      </svg>
    </div>
  );
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const WS_URL = BACKEND_URL.replace(/^http/, 'ws') + '/ws/debate';

export default function Dashboard() {
  const { status: wsStatus, messages } = useWebSocket(WS_URL);
  const [agentState, setAgentState] = useState('IDLE');
  const [wallet, setWallet] = useState({ address: '0xMockAddress123456789', balance: 100.00 });
  const [analysts, setAnalysts] = useState<Record<string, AnalystState>>({
    technical: { status: 'LOCKED', price: 0.10 },
    sentiment: { status: 'LOCKED', price: 0.20 },
    onchain: { status: 'LOCKED', price: 0.50 },
  });
  const [biteTx, setBiteTx] = useState<any>(null);
  const [auditTrail, setAuditTrail] = useState<AuditEntry[]>([]);
  const [totalSpend, setTotalSpend] = useState(0);
  const [traceSteps, setTraceSteps] = useState<TraceStep[]>([
    { icon: '🔍', label: 'Market Scan', detail: 'Awaiting trigger...', time: '', status: 'pending' },
    { icon: '💰', label: 'x402 Payments', detail: 'Pay 3 analysts via HTTP 402', time: '', status: 'pending' },
    { icon: '🧠', label: 'LLM Reasoning', detail: 'Multi-source fusion', time: '', status: 'pending' },
    { icon: '🤝', label: 'Consensus', detail: 'Aggregate scores → verdict', time: '', status: 'pending' },
    { icon: '🔐', label: 'BITE Encrypt', detail: 'Threshold encrypt intent', time: '', status: 'pending' },
    { icon: '✅', label: 'Execute', detail: 'Conditional execution', time: '', status: 'pending' },
  ]);

  const logRef = useRef<HTMLDivElement>(null);

  // Simulated market data — generated client-side to avoid hydration mismatch
  const [priceHistory, setPriceHistory] = useState<number[]>(() => {
    const base = 65000;
    return Array.from({ length: 48 }, (_, i) => base + Math.sin(i * 0.3) * 800);
  });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const base = 65000;
    setPriceHistory(Array.from({ length: 48 }, (_, i) => base + Math.sin(i * 0.3) * 800 + Math.random() * 400 - 200));
    setMounted(true);
  }, []);

  const currentPrice = priceHistory[priceHistory.length - 1];
  const prevPrice = priceHistory[priceHistory.length - 2];
  const priceChange = currentPrice - prevPrice;
  const pricePct = (priceChange / prevPrice) * 100;

  // Fetch wallet on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/api/zk/wallet`)
      .then(r => r.json())
      .then(d => setWallet({ address: d.address, balance: d.balance }))
      .catch(() => { });
  }, []);

  // Process WebSocket messages
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    const now = new Date().toLocaleTimeString();

    if (lastMsg.type === 'agent_status') {
      const statusText = lastMsg.status || lastMsg.data?.status || '';
      if (statusText.includes('Scanning')) {
        setAgentState('🔍 Scanning Market...');
        updateTrace(0, 'active', 'Scanning BTC/USDT...', now);
      }
      if (statusText.includes('Complete')) {
        setAgentState('✅ Workflow Complete');
        updateTrace(5, 'completed', 'Strategy submitted', now);
      }
    }
    if (lastMsg.type === 'wallet_update') {
      setWallet(lastMsg.data);
    }
    if (lastMsg.type === 'payment_update') {
      const { analyst } = lastMsg.data;
      setAnalysts(prev => ({ ...prev, [analyst]: { ...prev[analyst], status: 'UNLOCKING' } }));
      setAgentState(`💰 Paying ${analyst}...`);
      updateTrace(0, 'completed', 'Market scanned', now);
      updateTrace(1, 'active', `Paying ${analyst}...`, now);
    }
    if (lastMsg.type === 'analyst_result') {
      const { type, data } = lastMsg.data;
      setAnalysts(prev => ({ ...prev, [type]: { ...prev[type], status: 'UNLOCKED', data } }));
      fetchAudit();
      // Check if all 3 done
      setAnalysts(prev => {
        const unlocked = Object.values(prev).filter(a => a.status === 'UNLOCKED').length;
        if (unlocked >= 2) {
          updateTrace(1, 'completed', '3 analysts paid & received', now);
          updateTrace(2, 'active', 'Fusing analyst signals...', now);
          updateTrace(3, 'active', 'Computing weighted consensus', now);
        }
        return prev;
      });
    }
    if (lastMsg.type === 'bite_encrypted') {
      setBiteTx(lastMsg.data);
      setAgentState('🔐 Strategy Encrypted');
      updateTrace(2, 'completed', 'Reasoning complete', now);
      updateTrace(3, 'completed', 'Consensus: HIGH confidence', now);
      updateTrace(4, 'completed', 'BITE v2 encrypted on SKALE', now);
      updateTrace(5, 'active', 'Awaiting condition...', now);
      fetchAudit();
    }
    if (lastMsg.type === 'wallet_update') {
      setWallet(lastMsg.data);
    }
  }, [messages]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  const updateTrace = (idx: number, status: TraceStep['status'], detail: string, time: string) => {
    setTraceSteps(prev => prev.map((s, i) => i === idx ? { ...s, status, detail, time } : s));
  };

  const fetchAudit = () => {
    fetch(`${BACKEND_URL}/api/zk/audit`)
      .then(r => r.json())
      .then(d => {
        setAuditTrail(d.purchases || []);
        setTotalSpend(d.total_spend || 0);
      })
      .catch(() => { });
  };

  const startAnalysis = async () => {
    setAgentState('🔍 Scanning Market...');
    setAnalysts({
      technical: { status: 'LOCKED', price: 0.10 },
      sentiment: { status: 'LOCKED', price: 0.20 },
      onchain: { status: 'LOCKED', price: 0.50 },
    });
    setBiteTx(null);
    setTraceSteps(prev => prev.map(s => ({ ...s, status: 'pending' as const, time: '' })));
    updateTrace(0, 'active', 'Scanning BTC/USDT...', new Date().toLocaleTimeString());
    try {
      await fetch(`${BACKEND_URL}/api/zk/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'BTC/USDT' }),
      });
    } catch (e) {
      setAgentState('❌ Error - Backend Offline');
    }
  };

  const analystConfig: Record<string, { icon: string; title: string; color: string }> = {
    technical: { icon: '📈', title: 'Technical', color: 'technical' },
    sentiment: { icon: '🐦', title: 'Sentiment', color: 'sentiment' },
    onchain: { icon: '⛓️', title: 'On-Chain', color: 'onchain' },
  };

  // Consensus scores
  const getScore = (type: string) => {
    const a = analysts[type];
    if (a.status !== 'UNLOCKED' || !a.data) return 0;
    return (a.data.score || a.data.confidence || 0.75) * 100;
  };
  const getSignal = (type: string) => {
    const a = analysts[type];
    if (a.status !== 'UNLOCKED' || !a.data) return 'HOLD';
    return a.data.signal || a.data.recommendation || 'BUY';
  };
  const avgScore = Object.keys(analysts).reduce((sum, k) => sum + getScore(k), 0) / 3;
  const anyUnlocked = Object.values(analysts).some(a => a.status === 'UNLOCKED');

  return (
    <div className="dashboard">

      {/* ===== HEADER ===== */}
      <header className="header">
        <div className="header-left">
          <h1>🛡️ Zero-Knowledge Alpha Predator</h1>
          <p>Autonomous DeFi Agent • x402 Payments • BITE v2 Encrypted Execution • SKALE Network</p>
        </div>
        <div className="header-right">
          <div className={`status-badge ${wsStatus === 'OPEN' ? 'online' : 'offline'}`}>
            <span className={`status-dot ${wsStatus === 'OPEN' ? 'online' : 'offline'}`} />
            {wsStatus === 'OPEN' ? 'LIVE' : 'OFFLINE'}
          </div>
          <div className="wallet-card">
            <div className="wallet-icon">💳</div>
            <div className="wallet-info">
              <label>CDP Wallet</label>
              <div className="address">{wallet.address || '...'}</div>
            </div>
            <div className="wallet-balance">
              <div className="amount">${wallet.balance.toFixed(2)}</div>
              <div className="label">USDC</div>
            </div>
          </div>
        </div>
      </header>

      {/* ===== CONTROL BAR ===== */}
      <div className="control-bar">
        <button
          className="scan-button"
          onClick={startAnalysis}
          disabled={agentState !== 'IDLE' && !agentState.includes('Complete') && !agentState.includes('Encrypted') && !agentState.includes('Error')}
        >
          ▶ Run Alpha Scan
        </button>
        <div className="status-display">
          <span className="label">STATUS: </span>
          <span className="value">{agentState}</span>
        </div>
      </div>

      {/* ===== PIPELINE ===== */}
      <div className="pipeline">
        {[
          { icon: '🔍', label: 'Scan', active: agentState !== 'IDLE' },
          { icon: '💰', label: 'Pay (x402)', active: Object.values(analysts).some(a => a.status !== 'LOCKED') },
          { icon: '🧠', label: 'Reason', active: Object.values(analysts).filter(a => a.status === 'UNLOCKED').length >= 2 },
          { icon: '🤝', label: 'Consensus', active: anyUnlocked },
          { icon: '🔐', label: 'Encrypt', active: !!biteTx },
          { icon: '✅', label: 'Execute', active: agentState.includes('Complete') || agentState.includes('Encrypted') },
        ].map((step, i, arr) => (
          <span key={i} style={{ display: 'contents' }}>
            <div className={`pipeline-step ${step.active ? 'active' : ''}`}>
              <span className="pipeline-icon">{step.icon}</span>
              <span>{step.label}</span>
            </div>
            {i < arr.length - 1 && <div className="pipeline-arrow">→</div>}
          </span>
        ))}
      </div>

      {/* ===== ROW 1: Market Intelligence + Agent Decision Trace ===== */}
      <div className="grid-2-1">
        {/* Market Intelligence */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title"><span className="icon">📊</span> Market Intelligence</div>
            <span className="card-badge badge-live">● LIVE</span>
          </div>
          <div className="market-stats">
            <div className="market-stat">
              <div className="stat-label">BTC/USDT</div>
              <div className={`stat-value ${priceChange >= 0 ? 'positive' : 'negative'}`}>
                ${currentPrice.toFixed(0)}
              </div>
            </div>
            <div className="market-stat">
              <div className="stat-label">24h Change</div>
              <div className={`stat-value ${pricePct >= 0 ? 'positive' : 'negative'}`}>
                {pricePct >= 0 ? '+' : ''}{pricePct.toFixed(2)}%
              </div>
            </div>
            <div className="market-stat">
              <div className="stat-label">Volume</div>
              <div className="stat-value">$5.2B</div>
            </div>
            <div className="market-stat">
              <div className="stat-label">Funding</div>
              <div className="stat-value positive">0.01%</div>
            </div>
          </div>
          <Sparkline data={priceHistory} color="#3b82f6" />
        </div>

        {/* Agent Decision Trace */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title"><span className="icon">🧠</span> Agent Trace</div>
            <span className="card-badge badge-blue">AI</span>
          </div>
          <div className="trace-timeline">
            {traceSteps.map((step, i) => (
              <div key={i} className="trace-step">
                <div className={`trace-dot ${step.status}`}>{step.icon}</div>
                <div className="trace-content">
                  <div className="trace-label">{step.label}</div>
                  <div className="trace-detail">{step.detail}</div>
                </div>
                {step.time && <div className="trace-time">{step.time}</div>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ===== ROW 2: Analyst Cards ===== */}
      <div className="section-label">ANALYST NETWORK — x402 Paid Tool Calls</div>
      <div className="analyst-grid">
        {Object.entries(analysts).map(([type, analyst]) => {
          const config = analystConfig[type];
          return (
            <div key={type} className={`analyst-card ${analyst.status === 'UNLOCKED' ? 'unlocked' : ''}`}>
              <div className="analyst-card-header">
                <div className="analyst-card-header-left">
                  <div className={`analyst-icon ${config.color}`}>{config.icon}</div>
                  <h3>{config.title}</h3>
                </div>
                <span className="price-badge">
                  {analyst.status === 'UNLOCKED' ? '✅ PAID' : `$${analyst.price.toFixed(2)}`}
                </span>
              </div>
              <div className="analyst-card-body">
                {analyst.status === 'LOCKED' && (
                  <div className="locked-state">
                    <div className="lock-icon-container">🔒</div>
                    <p>HTTP 402 — Payment Required</p>
                  </div>
                )}
                {analyst.status === 'UNLOCKING' && (
                  <div className="locked-state unlocking-state">
                    <div className="lock-icon-container">⏳</div>
                    <p>Processing x402 Payment...</p>
                  </div>
                )}
                {analyst.status === 'UNLOCKED' && (
                  <div className="unlocked-state">
                    <div className="score-row">
                      <span className="label">Confidence</span>
                      <div className="score-bar-container">
                        <div className="score-bar">
                          <div className={`score-bar-fill ${config.color}`} style={{ width: `${getScore(type)}%` }} />
                        </div>
                        <span className={`score-value ${config.color}`}>{getScore(type).toFixed(0)}%</span>
                      </div>
                    </div>
                    <p className="insight-text">
                      {analyst.data?.insight || analyst.data?.signal || analyst.data?.recommendation || 'Data received'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* ===== ROW 3: Consensus + Risk Metrics ===== */}
      <div className="grid-2-1">
        {/* Consensus Radar */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title"><span className="icon">🤝</span> Multi-Source Consensus</div>
            <span className={`card-badge ${anyUnlocked ? 'badge-live' : 'badge-pending'}`}>
              {anyUnlocked ? '● COMPUTED' : 'AWAITING'}
            </span>
          </div>
          <div className="consensus-bars">
            {(['technical', 'sentiment', 'onchain'] as const).map(type => (
              <div key={type} className="consensus-row">
                <span className="consensus-label">{analystConfig[type].title}</span>
                <div className="consensus-bar-track">
                  <div className={`consensus-bar-fill ${type}`} style={{ width: `${getScore(type)}%` }}>
                    {getScore(type) > 0 && <span className="consensus-bar-value">{getScore(type).toFixed(0)}%</span>}
                  </div>
                </div>
                <span className={`consensus-signal ${getSignal(type).toUpperCase().includes('BUY') ? 'signal-buy' :
                  getSignal(type).toUpperCase().includes('SELL') ? 'signal-sell' : 'signal-hold'
                  }`}>
                  {getScore(type) > 0 ? getSignal(type).toUpperCase() : '—'}
                </span>
              </div>
            ))}
          </div>
          <div className="consensus-summary">
            <div>
              <div style={{ fontSize: '0.5625rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' as const, letterSpacing: '0.05em' }}>
                Weighted Score
              </div>
              <div className="consensus-score-big">{anyUnlocked ? avgScore.toFixed(0) : '—'}%</div>
            </div>
            <div style={{ textAlign: 'right' as const }}>
              <div style={{ fontSize: '0.5625rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' as const, letterSpacing: '0.05em' }}>
                Verdict
              </div>
              <div className="consensus-verdict">
                {anyUnlocked ? (avgScore > 60 ? '🟢 EXECUTE' : avgScore > 40 ? '🟡 HOLD' : '🔴 SKIP') : 'PENDING'}
              </div>
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title"><span className="icon">⚠️</span> Risk Controls</div>
          </div>
          <div className="risk-grid">
            <Gauge value={totalSpend} max={10} color="#f59e0b" label="Budget Used" />
            <Gauge value={anyUnlocked ? avgScore : 0} max={100} color="#10b981" label="Confidence" />
            <Gauge value={0.5} max={2} color="#3b82f6" label="Slippage" />
            <Gauge value={anyUnlocked ? 85 : 0} max={100} color="#a855f7" label="Safety" />
          </div>
        </div>
      </div>

      {/* ===== BITE VAULT ===== */}
      <div className="section-label">BITE v2 ENCRYPTED EXECUTION — SKALE BITE V2 Sandbox 2 (Chain 103698795)</div>
      <div className={`bite-vault ${biteTx ? 'active' : ''}`}>
        <div className="bite-vault-inner">
          <div className="bite-shield">{biteTx ? '🛡️' : '🔓'}</div>
          <div className="bite-content">
            <div className="bite-header">
              <h3>Zero-Knowledge Vault</h3>
              <span className="bite-badge badge-encrypted">
                {biteTx ? '🔐 BITE v2 ENCRYPTED' : '⏸ AWAITING'}
              </span>
            </div>
            {biteTx ? (
              <>
                <p>
                  Strategy encrypted using <strong>@skalenetwork/bite SDK</strong> on{' '}
                  <strong>{biteTx.chain || 'BITE V2 Sandbox 2'}</strong>.
                  Trade intent is threshold-encrypted and hidden until condition is met.
                  Condition: <code>{biteTx.condition || 'CONFIDENCE > 0.8'}</code>
                </p>
                <div className="bite-lifecycle">
                  {[
                    { icon: '📝', label: 'Intent', status: 'completed' },
                    { icon: '🔐', label: 'Encrypt', status: 'completed' },
                    { icon: '⏳', label: 'Condition', status: 'active' },
                    { icon: '🔓', label: 'Decrypt', status: 'pending' },
                    { icon: '✅', label: 'Execute', status: 'pending' },
                  ].map((stage, i) => (
                    <div key={i} className="bite-stage">
                      <div className={`bite-stage-icon ${stage.status}`}>{stage.icon}</div>
                      <span className="bite-stage-label">{stage.label}</span>
                    </div>
                  ))}
                </div>
                <div className="bite-tx-info">
                  <div className="bite-tx-row">
                    <span className="label">BITE TX</span>
                    <span className="value">
                      {biteTx.explorerUrl ? (
                        <a href={biteTx.explorerUrl} target="_blank" rel="noopener noreferrer" className="tx-link">
                          {biteTx.bite_tx_id.substring(0, 12)}... ↗
                        </a>
                      ) : (
                        biteTx.bite_tx_id
                      )}
                    </span>
                  </div>
                  <div className="bite-tx-row">
                    <span className="label">SDK</span>
                    <span className="value">{biteTx.sdk || '@skalenetwork/bite'}</span>
                  </div>
                  <div className="bite-tx-row">
                    <span className="label">CHAIN</span>
                    <span className="value">{biteTx.chain || 'BITE V2 Sandbox 2'} (ID: {biteTx.chainId || '103698795'})</span>
                  </div>
                  {biteTx.encryptedLength && (
                    <div className="bite-tx-row">
                      <span className="label">ENCRYPTED SIZE</span>
                      <span className="value">{biteTx.encryptedLength} bytes</span>
                    </div>
                  )}
                  {biteTx.committee && (
                    <>
                      <div className="bite-tx-row">
                        <span className="label">EPOCH</span>
                        <span className="value">{biteTx.committee.epochId}</span>
                      </div>
                      <div className="bite-tx-row">
                        <span className="label">BLS KEY</span>
                        <span className="value">{biteTx.committee.publicKeyPreview}</span>
                      </div>
                    </>
                  )}
                  <div className="bite-tx-row">
                    <span className="label">STATUS</span>
                    <span className="value">Threshold Encrypted → Awaiting Condition</span>
                  </div>
                  <div className="progress-bar"><div className="progress-bar-fill" /></div>
                </div>
              </>
            ) : (
              <p>No strategy yet. Run an Alpha Scan to generate and encrypt a trading strategy via the SKALE BITE V2 Sandbox.</p>
            )}
          </div>
        </div>
      </div>

      {/* ===== AUDIT TRAIL ===== */}
      <div className="section-label">AUDIT TRAIL — Spend Receipts & Budget Tracking</div>
      <div className="audit-panel">
        <div className="audit-header">
          {[
            { label: 'Total Spend', value: `$${totalSpend.toFixed(2)}` },
            { label: 'Transactions', value: `${auditTrail.length}` },
            { label: 'Budget Cap', value: '$10.00' },
            { label: 'Remaining', value: `$${(10 - totalSpend).toFixed(2)}`, color: (10 - totalSpend) < 2 ? '#ef4444' : '#10b981' },
          ].map((stat, i) => (
            <div key={i} className="audit-stat">
              <span className="audit-stat-label">{stat.label}</span>
              <span className="audit-stat-value" style={stat.color ? { color: stat.color } : {}}>{stat.value}</span>
            </div>
          ))}
        </div>
        {auditTrail.length > 0 ? (
          <table className="audit-table">
            <thead>
              <tr><th>Time</th><th>Tool</th><th>Amount</th><th>TX Hash</th><th>Justification</th></tr>
            </thead>
            <tbody>
              {auditTrail.map((entry, i) => (
                <tr key={i}>
                  <td className="mono">{new Date(entry.timestamp).toLocaleTimeString()}</td>
                  <td>{entry.tool}</td>
                  <td className="mono amount">${entry.amount.toFixed(2)}</td>
                  <td className="mono hash">{entry.tx_hash}</td>
                  <td className="justification">{entry.justification}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="audit-empty">No transactions yet. Run an Alpha Scan to see the payment flow.</div>
        )}
      </div>

      {/* ===== EVENT LOG ===== */}
      <div className="log-panel">
        <div className="log-panel-header">📡 WebSocket Event Log</div>
        <div className="log-panel-body" ref={logRef}>
          {messages.length === 0 && <div className="log-line">Waiting for events...</div>}
          {messages.map((m, i) => (
            <div key={i} className="log-line">
              <span className="time">[{new Date().toLocaleTimeString()}]</span>{' '}
              <span className="type">{m.type}</span>{' '}
              <span className="data">{JSON.stringify(m.data || m).slice(0, 120)}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
