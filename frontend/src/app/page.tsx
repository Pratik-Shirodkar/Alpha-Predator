'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function LandingPage() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    return (
        <div className="landing-container">
            {/* ===== HERO SECTION ===== */}
            <section className="hero">
                <div className="hero-content">
                    <div className="badge-container">
                        <span className="predator-badge">APEX AGENT v2.0</span>
                    </div>
                    <h1 className="hero-title">
                        <span className="glow-text">ZERO-KNOWLEDGE</span> <br />
                        ALPHA PREDATOR
                    </h1>
                    <p className="hero-subtitle">
                        The world's first autonomous trading agent using <strong>x402 Payments</strong>
                        and <strong>BITE v2 Threshold Encryption</strong> to hunt Alpha without front-running.
                    </p>

                    <div className="hero-actions">
                        <Link href="/dashboard" className="launch-btn">
                            LAUNCH PREDATOR <span className="arrow">↗</span>
                        </Link>
                        <a href="#features" className="secondary-btn">VIEW INTEL</a>
                    </div>
                </div>

                <div className="hero-visual">
                    <div className="hex-grid">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="hex-item">
                                <div className="hex-inner">
                                    <div className="hex-glow" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ===== INTEL / FEATURES ===== */}
            <section id="features" className="features">
                <div className="section-header">
                    <label>SYSTEM CAPABILITIES</label>
                    <h2>THE PREDATOR'S EDGE</h2>
                </div>

                <div className="feature-grid">
                    <div className="feature-card">
                        <div className="feature-icon">🔍</div>
                        <h3>THE HUNT</h3>
                        <p>Multi-analyst consensus engine. Aggregates Technical, Sentiment, and On-Chain data from <strong>Consensus AI</strong>'s global network.</p>
                        <div className="feature-tag">Consensus v2</div>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">💰</div>
                        <h3>SECURE ACCESS</h3>
                        <p>Built-in <strong>x402 (HTTP 402)</strong> flow. The agent manages its own <strong>CDP Wallet</strong> to pay for high-value intelligence autonomously.</p>
                        <div className="feature-tag">CDP Integrated</div>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">🔐</div>
                        <h3>STEALTH STRIKE</h3>
                        <p>Intent obfuscation via <strong>SKALE BITE v2</strong>. Transactions are threshold-encrypted until on-chain conditions are met, eliminating MEV risks.</p>
                        <div className="feature-tag">BITE v2 Private</div>
                    </div>
                </div>
            </section>

            {/* ===== WORKFLOW SECTION ===== */}
            <section className="workflow-section">
                <div className="workflow-container">
                    <div className="workflow-text">
                        <label>AUTONOMOUS PIPELINE</label>
                        <h2>DECISION TO DEPLOY</h2>
                        <div className="workflow-steps">
                            <div className="step">
                                <span className="step-num">01</span>
                                <div>
                                    <h4>Discovery</h4>
                                    <p>Agent identifies high-momentum pairs and requests premium analyst insights.</p>
                                </div>
                            </div>
                            <div className="step">
                                <span className="step-num">02</span>
                                <div>
                                    <h4>Authorization</h4>
                                    <p>Receives 402 challenge → Pays via CDP Smart Wallet → Unlocks Alpha.</p>
                                </div>
                            </div>
                            <div className="step">
                                <span className="step-num">03</span>
                                <div>
                                    <h4>Execution</h4>
                                    <p>Threshold-encrypts trading strategy on SKALE. Publicly visible, but private until strike.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="workflow-image">
                        {/* Abstract visual representng the agent pipeline */}
                        <div className="pipeline-viz">
                            <div className="viz-box encrypting" />
                            <div className="viz-line" />
                            <div className="viz-box consensus" />
                            <div className="viz-line" />
                            <div className="viz-box strike" />
                        </div>
                    </div>
                </div>
            </section>

            {/* ===== FOOTER ===== */}
            <footer className="landing-footer">
                <div className="footer-content">
                    <div className="footer-logo">🛡️ ZK ALPHA PREDATOR</div>
                    <p>Built for the San Francisco Agentic Commerce x402 Hackathon.</p>
                    <div className="footer-links">
                        <Link href="/dashboard">Dashboard</Link>
                        <a href="https://docs.cdp.coinbase.com/" target="_blank">CDP Docs</a>
                        <a href="https://github.com/skalenetwork/bite-v2" target="_blank">BITE v2</a>
                    </div>
                </div>
            </footer>

            {/* Predator Grid Background Overlay */}
            <div className="predator-grid" />
        </div>
    );
}
