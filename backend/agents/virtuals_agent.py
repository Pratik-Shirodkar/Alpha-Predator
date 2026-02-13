"""
Virtuals G.A.M.E. Framework Integration
========================================
Wraps ZK Alpha Predator as a G.A.M.E.-compatible agent.

Architecture mirrors the Virtuals Protocol SDK (Agent  Worker  Function)
so the predator can be deployed on the Virtuals ecosystem for the $1M/month
revenue-sharing incentive pool.

References:
  - https://github.com/game-by-virtuals/game-python
  - https://whitepaper.virtuals.io/developer-documents/game-framework
"""
import os
import asyncio
import json
import logging
import time
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# 
#  G.A.M.E. Framework Primitives (Virtuals-compatible)
# 

@dataclass
class GameFunction:
    """A callable tool that a Worker can execute."""
    name: str
    description: str
    fn: Callable
    args: List[str] = field(default_factory=list)

    async def execute(self, **kwargs) -> str:
        result = await self.fn(**kwargs) if asyncio.iscoroutinefunction(self.fn) else self.fn(**kwargs)
        return result


@dataclass
class GameWorker:
    """An autonomous unit that owns a set of Functions."""
    name: str
    description: str
    functions: List[GameFunction] = field(default_factory=list)
    instruction: str = ""

    async def execute_function(self, fn_name: str, **kwargs) -> str:
        for func in self.functions:
            if func.name == fn_name:
                logger.info(f"  [Worker:{self.name}] Executing {fn_name}")
                return await func.execute(**kwargs)
        raise ValueError(f"Function {fn_name} not found in worker {self.name}")


@dataclass
class GameAgent:
    """
    Top-level G.A.M.E. agent  the high-level planner.
    Maps to `virtuals_sdk.game.agent.Agent`.
    """
    name: str
    description: str
    goal: str
    workers: List[GameWorker] = field(default_factory=list)
    api_key: Optional[str] = None

    def list_capabilities(self) -> Dict[str, Any]:
        """Returns a JSON-serialisable capability manifest."""
        return {
            "agent": self.name,
            "goal": self.goal,
            "workers": [
                {
                    "name": w.name,
                    "description": w.description,
                    "functions": [f.name for f in w.functions],
                }
                for w in self.workers
            ],
        }


# 
#  Analyst Functions (x402-paid data sources)
# 

async def get_technical_analysis(symbol: str) -> str:
    """Pays for and retrieves technical analysis via x402."""
    from agents.bull_agent import BullAgent
    logger.info(f"   x402  Technical Analysis for {symbol}")
    agent = BullAgent()
    data = await agent.get_analyst_data("Technical", symbol)
    return json.dumps(data) if isinstance(data, dict) else str(data)


async def get_sentiment_analysis(symbol: str) -> str:
    """Pays for and retrieves sentiment analysis via x402."""
    from agents.bull_agent import BullAgent
    logger.info(f"   x402  Sentiment Analysis for {symbol}")
    agent = BullAgent()
    data = await agent.get_analyst_data("Sentiment", symbol)
    return json.dumps(data) if isinstance(data, dict) else str(data)


async def get_onchain_analysis(symbol: str) -> str:
    """Pays for and retrieves on-chain analysis via x402."""
    from agents.bull_agent import BullAgent
    logger.info(f"   x402  On-Chain Analysis for {symbol}")
    agent = BullAgent()
    data = await agent.get_analyst_data("On-Chain", symbol)
    return json.dumps(data) if isinstance(data, dict) else str(data)


# 
#  Workers
# 

technical_worker = GameWorker(
    name="TechnicalAnalyst",
    description="Analyses price action, indicators, and chart patterns.",
    instruction="Use RSI, MACD, Bollinger Bands and volume to evaluate trend strength.",
    functions=[
        GameFunction(
            name="get_technical_analysis",
            description="Fetch technical indicators and signals for a symbol.",
            fn=get_technical_analysis,
            args=["symbol"],
        )
    ],
)

sentiment_worker = GameWorker(
    name="SentimentAnalyst",
    description="Analyses news headlines, social-media sentiment, and fear/greed indices.",
    instruction="Aggregate sentiment scores from multiple sources and flag anomalies.",
    functions=[
        GameFunction(
            name="get_sentiment_analysis",
            description="Fetch aggregated market sentiment data.",
            fn=get_sentiment_analysis,
            args=["symbol"],
        )
    ],
)

onchain_worker = GameWorker(
    name="OnChainAnalyst",
    description="Analyses wallet flows, exchange balances, and whale movements.",
    instruction="Track large-wallet inflows/outflows and exchange reserve changes.",
    functions=[
        GameFunction(
            name="get_onchain_analysis",
            description="Fetch on-chain breadcrumbs and whale-flow data.",
            fn=get_onchain_analysis,
            args=["symbol"],
        )
    ],
)


# 
#  ZK Alpha Predator  the G.A.M.E. Agent
# 

class ZKAlphaPredatorVirtualsAgent:
    """
    Wraps the core BullAgent consensus engine inside the Virtuals
    G.A.M.E. framework so it can be registered on-chain and participate
    in the Virtuals revenue-sharing pool.
    """

    def __init__(self):
        self.api_key = os.getenv("VIRTUALS_API_KEY", "")
        if not self.api_key:
            logger.warning("VIRTUALS_API_KEY not set  running in local-demo mode.")

        self.agent = GameAgent(
            name="Zero-Knowledge Alpha Predator",
            description=(
                "An autonomous trading predator that uses x402 payments "
                "to purchase multi-analyst intelligence, forms a consensus, "
                "and executes encrypted (BITE v2) trade intents."
            ),
            goal="Maximise risk-adjusted returns by discovering and acting on "
                 "high-conviction alpha before the market can front-run.",
            workers=[technical_worker, sentiment_worker, onchain_worker],
            api_key=self.api_key,
        )
        logger.info(f"Virtuals G.A.M.E. Agent initialised: {self.agent.name}")

    # --- Public API -------------------------------------------------------

    async def run_analysis(self, symbol: str) -> Dict[str, Any]:
        """Full consensus cycle via the G.A.M.E. framework."""
        start = time.time()
        logger.info(f"[G.A.M.E.] Starting consensus hunt for {symbol} ...")

        # 1. Plan  log high-level intent
        logger.info(f"[G.A.M.E.] Goal: {self.agent.goal}")

        # 2. Coordinate workers
        for worker in self.agent.workers:
            logger.info(f"[G.A.M.E.] Dispatching Worker  {worker.name}")

        # 3. Execute native consensus engine
        from agents.bull_agent import BullAgent
        native = BullAgent()
        result = await native.run_full_cycle(symbol)

        elapsed = round(time.time() - start, 2)
        decision = result.get("decision", "HOLD") if isinstance(result, dict) else "UNKNOWN"
        logger.info(f"[G.A.M.E.] Hunt complete in {elapsed}s  Decision: {decision}")
        return result

    def capabilities(self) -> Dict[str, Any]:
        """Return the agent's capability manifest (useful for /api endpoints)."""
        return self.agent.list_capabilities()


# Singleton  imported by main.py
virtuals_agent = ZKAlphaPredatorVirtualsAgent()
