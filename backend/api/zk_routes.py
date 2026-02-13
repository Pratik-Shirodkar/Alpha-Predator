
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from agents.bull_agent import bull_agent
from data.data_models import MarketData, Ticker, OrderBook, OrderBookLevel

router = APIRouter(prefix="/api/zk", tags=["ZK Predator"])

class TriggerRequest(BaseModel):
    symbol: str = "BTC/USDT"
    force_demo: bool = True

@router.post("/trigger")
async def trigger_zk_predator(request: TriggerRequest):
    """
    Trigger the ZK Alpha Predator Workflow.
    """
    # 1. Mock Market Data (In a real app, this would come from a service)
    market_data = MarketData(
        symbol=request.symbol,
        timestamp=datetime.now(),
        ticker=Ticker(
            symbol=request.symbol,
            last_price=65000.0,
            high_24h=66000.0,
            low_24h=64000.0,
            volume_24h=5000.0,
            change_24h=1200.0,
            change_pct_24h=2.5,
            bid=64990.0,
            ask=65010.0,
            timestamp=datetime.now()
        ),
        orderbook=OrderBook(
            symbol=request.symbol,
            timestamp=datetime.now(),
            bids=[OrderBookLevel(price=64990, quantity=1.0)],
            asks=[OrderBookLevel(price=65010, quantity=1.0)]
        ),
        candles=[],
        funding_rate=0.0001
    )

    # 2. Force Demo Logic if requested
    if request.force_demo:
        # Mock the initial LLM call to ensure we proceed to Analyst Network
        async def mock_call_llm(prompt: str) -> str:
            return '{"confidence": 0.5, "action": "HOLD", "reasoning": "Market looks interesting, checking swarm."}'
        
        # Temporarily patch
        original_call = bull_agent._call_llm
        bull_agent._call_llm = mock_call_llm
        
        try:
             # Broadcast Status
            from api.websocket import connection_manager
            await connection_manager.broadcast_status({
                "type": "agent_status",
                "status": "Scanning Market..."
            })
            
            result = await bull_agent.analyze(market_data, signals=[])
            
            await connection_manager.broadcast_status({
                "type": "agent_status",
                "status": "Workflow Complete"
            })
            
            return result
        finally:
            # Restore
            bull_agent._call_llm = original_call
            
    else:
         return await bull_agent.analyze(market_data, signals=[])


@router.get("/audit")
async def get_audit_trail():
    """Return full spend audit trail."""
    from execution.budget_manager import budget_manager
    summary = budget_manager.get_summary()
    return {
        "total_spend": summary["total_spend"],
        "purchase_count": summary["purchase_count"],
        "purchases": summary["recent_purchases"]
    }


@router.get("/wallet")
async def get_wallet_status():
    """Return current wallet status."""
    from execution.payment_manager import payment_manager
    return {
        "address": payment_manager.get_address(),
        "balance": float(await payment_manager.get_balance()),
        "mock_mode": payment_manager.mock_mode
    }

@router.get("/status")
async def get_agent_status():
    """Return agent status and integration health."""
    from agents.virtuals_agent import virtuals_agent
    return {
        "agent": "ZK Alpha Predator",
        "status": "online",
        "virtuals_integration": bool(virtuals_agent.api_key),
        "mode": "production" if virtuals_agent.api_key else "demo",
        "capabilities": virtuals_agent.capabilities()
    }
