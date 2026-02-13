import httpx
import logging
import asyncio
from typing import Dict, List, Optional
from execution.payment_manager import payment_manager
from execution.budget_manager import budget_manager
from config.settings import settings

logger = logging.getLogger(__name__)

class AnalystNetworkTool:
    """
    Interface to the "Analyst Network".
    Manages querying multiple specialized AI agents (endpoints) and handling their payment requirements.
    """
    
    def __init__(self, base_url: str = f"http://localhost:8000"):
        self.base_url = base_url
        self.endpoints = {
            "technical": "/analysts/technical",
            "sentiment": "/analysts/sentiment",
            "onchain": "/analysts/onchain"
        }
        
    async def query_analyst(self, analyst_type: str, justification: str) -> Dict:
        """
        Query a specific analyst. Handles 402 loop.
        """
        endpoint = self.endpoints.get(analyst_type)
        if not endpoint:
            return {"error": f"Unknown analyst type: {analyst_type}"}
            
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Try Request
                resp = await client.get(url)
                
                if resp.status_code == 200:
                    return resp.json()
                
                if resp.status_code == 402:
                    logger.info(f"Analyst {analyst_type} requires payment. Negotiating...")
                    
                    # Parse Payment Request
                    address = resp.headers.get("X-Payment-Address")
                    amount = float(resp.headers.get("X-Payment-Amount", 0.0))
                    asset = resp.headers.get("X-Payment-Asset", "usdc")
                    
                    if not address or amount == 0:
                        return {"error": "Invalid 402 response"}
                        
                    if not budget_manager.authorize_expense(amount, f"Analyst: {analyst_type}", justification):
                         return {"error": "Budget exceeded"}
                         
                    # Broadcast Payment Intent
                    from api.websocket import connection_manager
                    asyncio.create_task(connection_manager.broadcast_status({
                        "type": "payment_update",
                        "data": {
                            "analyst": analyst_type,
                            "amount": amount,
                            "tx_hash": "pending..."
                        }
                    }))

                    # Pay
                    # Pay
                    receipt = await payment_manager.pay(address, amount, asset)
                    
                    # Log Expense
                    budget_manager.record_expense(
                        amount, 
                        f"Analyst: {analyst_type}", 
                        receipt["transaction_hash"],
                        justification
                    )
                    
                    # Retry with Token (Mock Proof)
                    retry_resp = await client.get(
                        url,
                        headers={"X-Payment-Token": "valid_token_123"} 
                    )
                    
                    if retry_resp.status_code == 200:
                        data = retry_resp.json()
                        # Broadcast Result
                        from api.websocket import connection_manager
                        asyncio.create_task(connection_manager.broadcast_status({
                            "type": "analyst_result",
                            "data": {
                                "type": analyst_type,
                                "data": data
                            }
                        }))
                        return data
                    else:
                        return {"error": f"Failed after payment: {retry_resp.status_code}"}
                        
            except Exception as e:
                logger.error(f"Error querying {analyst_type}: {e}")
                return {"error": str(e)}

    async def gather_consensus(self, justification: str) -> Dict[str, Dict]:
        """
        Query ALL analysts in parallel and return results.
        """
        logger.info("Gathering consensus from Analyst Network...")
        
        tasks = [
            self.query_analyst("technical", justification),
            self.query_analyst("sentiment", justification),
            self.query_analyst("onchain", justification)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "technical": results[0],
            "sentiment": results[1],
            "onchain": results[2]
        }

# Singleton
analyst_tool = AnalystNetworkTool()
