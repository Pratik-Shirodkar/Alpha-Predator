"""
Vercel Serverless Entry Point
Minimal FastAPI app for serverless deployment.
Heavy dependencies (cdp-sdk, web3, pandas, numpy) are not available
in the Vercel runtime, so this exposes a lightweight API surface.
"""
import sys
import os

# Add backend root to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ZK Alpha Predator API",
    description="Zero-Knowledge Alpha Predator - Autonomous Trading Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "ZK Alpha Predator",
        "description": "Autonomous agent that hunts alpha using x402 payments, multi-analyst consensus, and BITE v2 encrypted trade intents.",
        "version": "1.0.0",
        "status": "online",
        "framework": "Virtuals G.A.M.E.",
        "features": [
            "x402 Agentic Payments",
            "Multi-Analyst Consensus (Technical + Sentiment + On-Chain)",
            "BITE v2 Encrypted Trade Intents",
            "CDP Wallet Integration",
            "Virtuals G.A.M.E. Framework"
        ]
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "runtime": "vercel-serverless"}


@app.get("/api/zk/capabilities")
async def capabilities():
    return {
        "agent": "Zero-Knowledge Alpha Predator",
        "goal": "Maximise risk-adjusted returns by discovering and acting on high-conviction alpha before the market can front-run.",
        "workers": [
            {
                "name": "TechnicalAnalyst",
                "description": "Analyses price action, indicators, and chart patterns.",
                "functions": ["get_technical_analysis"]
            },
            {
                "name": "SentimentAnalyst",
                "description": "Analyses news headlines, social-media sentiment, and fear/greed indices.",
                "functions": ["get_sentiment_analysis"]
            },
            {
                "name": "OnChainAnalyst",
                "description": "Analyses wallet flows, exchange balances, and whale movements.",
                "functions": ["get_onchain_analysis"]
            }
        ],
        "integrations": {
            "payments": "x402 Protocol (Coinbase)",
            "wallets": "CDP SDK (Base Sepolia)",
            "encryption": "BITE v2 (SKALE)",
            "framework": "Virtuals G.A.M.E."
        }
    }


@app.get("/api/zk/status")
async def agent_status():
    return {
        "agent": "ZK Alpha Predator",
        "mode": "demo",
        "payment_system": "x402",
        "bite_status": "active",
        "wallet_network": "base-sepolia",
        "virtuals_integration": True,
        "analysts": {
            "technical": {"status": "ready", "data_source": "mock"},
            "sentiment": {"status": "ready", "data_source": "mock"},
            "onchain": {"status": "ready", "data_source": "mock"}
        }
    }
