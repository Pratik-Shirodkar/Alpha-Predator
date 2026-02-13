from fastapi import APIRouter, Header, Response, HTTPException
from typing import Optional, Dict
from execution.payment_manager import payment_manager

router = APIRouter(prefix="/analysts", tags=["Analyst Network"])

# Pricing Model
PRICES = {
    "technical": 0.10,
    "sentiment": 0.20,
    "onchain": 0.50
}

ASSET = "usdc"

def create_402_response(service_type: str, cost: float) -> Response:
    """Helper to generate standardized 402 response"""
    deposit_address = payment_manager.get_address()
    headers = {
        "X-Payment-Address": deposit_address,
        "X-Payment-Amount": str(cost),
        "X-Payment-Asset": ASSET,
        "X-Service-Type": service_type
    }
    return Response(
        content=f'{{"error": "Payment Required", "message": "{service_type.title()} Analysis is locked. Price: {cost} {ASSET}"}}',
        status_code=402,
        headers=headers,
        media_type="application/json"
    )

@router.get("/technical")
async def get_technical_analysis(
    x_payment_token: Optional[str] = Header(None, alias="X-Payment-Token")
):
    if not x_payment_token:
        return create_402_response("technical", PRICES["technical"])
        
    return {
        "analyst": "TechWizard_AI",
        "type": "Technical",
        "score": 0.85, # Bullish
        "indicators": {"RSI": 65, "MACD": "Bullish Cross"},
        "insight": "Strong momentum breakout confirmed on 4H timeframe."
    }

@router.get("/sentiment")
async def get_sentiment_analysis(
    x_payment_token: Optional[str] = Header(None, alias="X-Payment-Token")
):
    if not x_payment_token:
        return create_402_response("sentiment", PRICES["sentiment"])
        
    return {
        "analyst": "NewsReader_Bot",
        "type": "Sentiment",
        "score": 0.60, # Neutral-Bullish
        "sources": ["Twitter", "Bloomberg"],
        "insight": "Retail sentiment is mixed, but institutional mentions are rising."
    }

@router.get("/onchain")
async def get_onchain_analysis(
    x_payment_token: Optional[str] = Header(None, alias="X-Payment-Token")
):
    if not x_payment_token:
        return create_402_response("onchain", PRICES["onchain"])
        
    return {
        "analyst": "WhaleWatcher_v9",
        "type": "On-Chain",
        "score": 0.92, # Very Bullish
        "metrics": {"exchange_outflow": "High", "whale_accumulation": "Detected"},
        "insight": "Significant withdrawal of BTC from exchanges in the last hour. Whales are accumulating."
    }
