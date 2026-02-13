
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import httpx
import logging
import traceback
from agents.bull_agent import bull_agent
from data.data_models import MarketData, Ticker, OrderBook, OrderBookLevel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zk", tags=["ZK Predator"])

class TriggerRequest(BaseModel):
    symbol: str = "BTC/USDT"


async def _fetch_live_market_data(symbol: str) -> MarketData:
    """Fetch live market data from CoinGecko + Binance."""
    now = datetime.now()
    
    # Map symbol to CoinGecko id
    coin_map = {
        "BTC/USDT": ("bitcoin", "BTCUSDT"),
        "ETH/USDT": ("ethereum", "ETHUSDT"),
        "SOL/USDT": ("solana", "SOLUSDT"),
    }
    cg_id, binance_sym = coin_map.get(symbol, ("bitcoin", "BTCUSDT"))
    
    last_price = 65000.0
    high_24h = 66000.0
    low_24h = 64000.0
    volume_24h = 5000.0
    change_pct_24h = 0.0
    bid = 64990.0
    ask = 65010.0
    bids_list = [OrderBookLevel(price=64990, quantity=1.0)]
    asks_list = [OrderBookLevel(price=65010, quantity=1.0)]
    funding_rate = 0.0001
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Price from CoinGecko (free, no API key)
        try:
            cg_resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": cg_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_high_low_24h": "true",
                }
            )
            if cg_resp.status_code == 200:
                d = cg_resp.json().get(cg_id, {})
                last_price = d.get("usd", last_price)
                high_24h = d.get("usd_24h_high", last_price * 1.01)
                low_24h = d.get("usd_24h_low", last_price * 0.99)
                volume_24h = d.get("usd_24h_vol", 5000000000) / 1_000_000  # millions
                change_pct_24h = d.get("usd_24h_change", 0.0)
                logger.info(f"CoinGecko: {symbol} = ${last_price:,.2f} ({change_pct_24h:+.2f}%)")
        except Exception as e:
            logger.warning(f"CoinGecko fetch failed: {e}. Using defaults.")
        
        # 2. Order book from Binance (free, no API key)
        try:
            ob_resp = await client.get(
                f"https://api.binance.com/api/v3/depth",
                params={"symbol": binance_sym, "limit": 5}
            )
            if ob_resp.status_code == 200:
                ob = ob_resp.json()
                bids_list = [OrderBookLevel(price=float(b[0]), quantity=float(b[1])) for b in ob.get("bids", [])[:5]]
                asks_list = [OrderBookLevel(price=float(a[0]), quantity=float(a[1])) for a in ob.get("asks", [])[:5]]
                if bids_list:
                    bid = bids_list[0].price
                if asks_list:
                    ask = asks_list[0].price
                logger.info(f"Binance: Bid=${bid:,.2f} Ask=${ask:,.2f} Depth={len(bids_list)}")
        except Exception as e:
            logger.warning(f"Binance orderbook fetch failed: {e}. Using defaults.")
        
        # 3. Funding rate from Binance Futures
        try:
            fr_resp = await client.get(
                "https://fapi.binance.com/fapi/v1/fundingRate",
                params={"symbol": binance_sym, "limit": 1}
            )
            if fr_resp.status_code == 200:
                fr_data = fr_resp.json()
                if fr_data:
                    funding_rate = float(fr_data[0].get("fundingRate", 0.0001))
                    logger.info(f"Binance Funding: {funding_rate*100:.4f}%")
        except Exception as e:
            logger.warning(f"Binance funding fetch failed: {e}.")
    
    change_24h = last_price * (change_pct_24h / 100.0)
    
    return MarketData(
        symbol=symbol,
        timestamp=now,
        ticker=Ticker(
            symbol=symbol,
            last_price=last_price,
            high_24h=high_24h,
            low_24h=low_24h,
            volume_24h=volume_24h,
            change_24h=change_24h,
            change_pct_24h=change_pct_24h,
            bid=bid,
            ask=ask,
            timestamp=now
        ),
        orderbook=OrderBook(
            symbol=symbol,
            timestamp=now,
            bids=bids_list,
            asks=asks_list
        ),
        candles=[],
        funding_rate=funding_rate
    )


@router.post("/trigger")
async def trigger_zk_predator(request: TriggerRequest):
    """
    Trigger the ZK Alpha Predator Workflow with REAL market data.
    """
    try:
        return await _run_trigger(request)
    except Exception as e:
        logger.error(f"Trigger failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_trigger(request: TriggerRequest):
    from api.websocket import connection_manager
    
    # 1. Fetch REAL Market Data
    await connection_manager.broadcast_status({
        "type": "agent_status",
        "status": "Scanning Market..."
    })
    
    market_data = await _fetch_live_market_data(request.symbol)
    
    # 2. Run the Bull Agent with real LLM + real data
    result = await bull_agent.analyze(market_data, signals=[])
    
    # 3. Broadcast BITE transaction if encryption occurred
    if result.get("action") == "PROPOSE_ENCRYPTED_EXECUTION" and "bite_tx" in result:
        await connection_manager.broadcast_status({
            "type": "bite_encrypted",
            "data": result["bite_tx"]
        })
    
    await connection_manager.broadcast_status({
        "type": "agent_status",
        "status": "Workflow Complete"
    })
    
    return result


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
        "mock_mode": payment_manager.mode == "mock"
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
