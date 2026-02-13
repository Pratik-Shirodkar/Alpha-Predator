import asyncio
import logging
import json
import sys
import os

# Fix path to ensure imports work from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from data.data_models import MarketData, Ticker, OrderBook, OrderBookLevel
from agents.bull_agent import bull_agent
from execution.budget_manager import budget_manager
from execution.bite_manager import bite_manager
from tools.analyst_network import analyst_tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- MOCKING FOR DEMO ---
async def mock_call_llm(prompt: str) -> str:
    # "See even a glimmer of hope" -> Return 0.5 to trigger Analyst Network
    return json.dumps({
        "action": "HOLD",
        "confidence": 0.6, 
        "reasoning": "Market looks interesting, but I need confirmation from the swarm."
    })

# Apply Mock
bull_agent._call_llm = mock_call_llm

# Fix: Mock Analyst Tool to avoid needing running server for this script
# (We want to verify logic, not network stack here)
async def mock_gather_consensus(justification):
    print(f"\n[Mock Network] Gathering consensus for: {justification}")
    print("[Mock Network] Paying 3 Analysts (Total: $0.80)...")
    budget_manager.record_expense(0.80, "Analyst Swarm", "0xMockTxBatch", justification)
    return {
        "technical": {"score": 0.85, "insight": "Techs are strong"},
        "sentiment": {"score": 0.75, "insight": "Sentiment is rising"},
        "onchain": {"score": 0.95, "insight": "Whales buying aggressively"}
    }

analyst_tool.gather_consensus = mock_gather_consensus
# -----------------------------

async def main():
    print("\n--- ZERO-KNOWLEDGE ALPHA PREDATOR: VERIFICATION ---\n")
    
    # 1. Setup Mock Market Data
    # 1. Setup Mock Market Data
    market_data = MarketData(
        symbol="BTC/USDT",
        timestamp=datetime.now(),
        ticker=Ticker(
            symbol="BTC/USDT",
            last_price=65000.0,
            high_24h=66000.0,
            low_24h=64000.0,
            volume_24h=5000.0,
            change_24h=1500.0,  # Added missing field
            change_pct_24h=2.5,
            bid=64990.0,
            ask=65010.0,
            timestamp=datetime.now() # Added missing field
        ),
        orderbook=OrderBook(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            bids=[OrderBookLevel(price=64990, quantity=1.0)],
            asks=[OrderBookLevel(price=65010, quantity=1.0)]
        ),
        candles=[], # Added missing field
        funding_rate=0.0001
    )
    
    print(f"Stats BEFORE: Total Spend = ${budget_manager.total_spend}")
    print(f"BITE Pool Size: {len(bite_manager.encrypted_pool)}")
    
    # 2. Run Analysis
    print("\n[Bull Agent (ZK Predator)] Hunting for Alpha...")
    result = await bull_agent.analyze(market_data, signals=[])
    
    # 3. Output Results
    print("\n--- EXECUTED STRATEGY ---")
    
    if result.get("action") == "PROPOSE_ENCRYPTED_EXECUTION":
        print(" SUCCESS: Encrypted Strategy Generated!")
        print(f"TxID: {result['bite_tx']['bite_tx_id']}")
        print(f"Encrypted Blob: {result['bite_tx']['encrypted_blob']}")
        print(f"Release Condition: {result['bite_tx']['condition']}")
        print(f"Consensus Confidence: {result['confidence']:.2f}")
    else:
        print(" FAILED: Did not generate encrypted strategy.")
        print(result)
    
    print("\n--- BUDGET STATUS ---")
    print(f"Total Spend: ${budget_manager.total_spend}")
    if budget_manager.purchases:
        last = budget_manager.purchases[-1]
        print(f"Last Purchase: {last['tool']} for ${last['amount']}")
        print(f"Justification: {last['justification']}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
