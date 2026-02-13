import httpx
import logging
import asyncio
from typing import Dict, Optional
from execution.payment_manager import payment_manager
from execution.budget_manager import budget_manager
from config.settings import settings

logger = logging.getLogger(__name__)

class PremiumMarketInsightTool:
    """
    Tool that fetches premium market data.
    Demonstrates Agentic Commerce by handling HTTP 402 Payment Required challenges automatically.
    """
    
    def __init__(self, base_url: str = f"http://localhost:8000"):
        self.base_url = base_url
        self.endpoint = "/premium/sentiment"
        
    async def get_sentiment(self, justification: str = "Market analysis required") -> Dict:
        """
        Fetch premium sentiment. detailed flow:
        1. Try to fetch (expecting 402).
        2. if 402, parse payment requirements.
        3. Check budget.
        4. Pay.
        5. Retry with proof.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}{self.endpoint}")
            
            if resp.status_code == 200:
                return resp.json()
                
            if resp.status_code == 402:
                logger.info("Received 402 Payment Required. Negotiating payment...")
                
                # Parse 402 headers
                address = resp.headers.get("X-Payment-Address")
                amount = float(resp.headers.get("X-Payment-Amount", 0.05))
                asset = resp.headers.get("X-Payment-Asset", "usdc")
                
                if not address:
                    return {"error": "Invalid 402 response: Missing address"}
                    
                # Budget Check
                if not budget_manager.authorize_expense(amount, "Premium Sentiment", justification):
                    return {"error": "Budget exceeded. Cannot purchase data."}
                    
                # Pay
                try:
                    receipt = await payment_manager.pay(address, amount, asset)
                    
                    # Record expense
                    budget_manager.record_expense(
                        amount, 
                        "Premium Sentiment", 
                        receipt["transaction_hash"],
                        justification
                    )
                    
                    # Retry with "Proof" (simulated via token or just retrying if service tracks IP/mock)
                    # For this hackathon demo, we will pass a "X-Payment-Token: valid_token_123" header 
                    # which simulates the 'proof of payment' generated after the transaction.
                    
                    retry_resp = await client.get(
                        f"{self.base_url}{self.endpoint}",
                        headers={"X-Payment-Token": "valid_token_123"} 
                    )
                    
                    if retry_resp.status_code == 200:
                         logger.info("Payment successful. Data unlocked.")
                         return retry_resp.json()
                    else:
                         return {"error": f"Failed after payment: {retry_resp.status_code}"}
                         
                except Exception as e:
                    logger.error(f"Payment failed: {e}")
                    return {"error": f"Payment failed: {str(e)}"}
            
            return {"error": f"Unexpected status: {resp.status_code}"}

# Singleton
premium_tool = PremiumMarketInsightTool()
