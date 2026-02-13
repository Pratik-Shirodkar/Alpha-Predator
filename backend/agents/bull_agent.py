"""
Bull Agent - Evolution: Zero-Knowledge Alpha Predator
"""
from typing import Optional
import logging
import asyncio
from agents.base_agent import BaseAgent
from data.data_models import MarketData, DebateMessage, TradeAction
from tools.analyst_network import analyst_tool
from execution.bite_manager import bite_manager

logger = logging.getLogger(__name__)

class BullAgent(BaseAgent):
    """
    The Bull Agent looks for LONG opportunities.
    Evolution: Uses Agentic Commerce (x402) to buy insights and BITE v2 to encrypt strategy.
    """
    
    def __init__(self):
        super().__init__(
            name="Bull (ZK Predator)",
            emoji="",
            prompt_file="bull_prompt.txt"
        )
    
    async def analyze(self, market_data: MarketData, signals: list) -> dict:
        """
        Execute the 'Zero-Knowledge Alpha Predator' workflow.
        """
        market_context = self._format_market_context(market_data)
        
        # 1. Discovery (Initial Scan)
        prompt = f"""
{market_context}
Based on this data, analyze whether there's a potential opportunity.
If you see even a glimmer of hope, return CONFIDENCE 0.5 (Neutral).
We will use paid analysts to confirm.
"""
        response = await self._call_llm(prompt)
        result = self._extract_json(response) or {"confidence": 0.5, "action": "HOLD"}
        
        # 2. Paid Research & Consensus
        # If we are interested (confidence > 0.4), we pay for the "Analyst Network"
        confidence = result.get("confidence", 0.5)
        
        if 0.4 <= confidence < 0.9:
            logger.info(f"Target Acquired (Conf: {confidence}). Deploying Analyst Network swarm...")
            
            # --- AGENTIC COMMERCE (x402) ---
            # Pay 3 separate agents for distinct viewpoints
            insights = await analyst_tool.gather_consensus("Building Consensus for BITE Execution")
            
            tech_score = insights['technical'].get('score', 0.5)
            sent_score = insights['sentiment'].get('score', 0.5)
            chain_score = insights['onchain'].get('score', 0.5)
            
            # Weighted Consensus Calculation
            # Technical (30%), Sentiment (20%), On-Chain (50%)
            consensus_score = (tech_score * 0.3) + (sent_score * 0.2) + (chain_score * 0.5)
            
            logger.info(f"Consensus Reached: {consensus_score:.2f} (Tech: {tech_score}, Sent: {sent_score}, Chain: {chain_score})")
            
            result["consensus_score"] = consensus_score
            result["analyst_insights"] = insights
            
            # 3. Encrypted Execution (BITE v2)
            if consensus_score > 0.75:
                # We have high conviction from the swarm.
                # Prepare the "Sealed Strategy"
                
                intent = {
                    "action": "BUY",
                    "asset": market_data.symbol,
                    "amount_usdc": 1000,
                    "rationale": f"Consensus {consensus_score:.2f} > 0.75. Whale accumulation confirmed."
                }
                
                condition = "CONFIDENCE > 0.8" # The network will only decrypt if confidence remains high
                
                # --- ENCRYPTION (BITE) ---
                bite_tx = bite_manager.encrypt_intent(intent, condition)
                
                result["action"] = "PROPOSE_ENCRYPTED_EXECUTION"
                result["bite_tx"] = bite_tx
                result["note"] = f"Strategy Encrypted with BITE v2. TxID: {bite_tx['bite_tx_id']}"
                result["confidence"] = consensus_score
                
            else:
                result["action"] = "HOLD"
                result["note"] = f"Consensus {consensus_score:.2f} too low to execute."
        
        # Add the raw message for display
        result["raw_message"] = response
        result["agent"] = self.name
        result["emoji"] = self.emoji
        
        return result
    
    async def respond_to(self, message: DebateMessage, market_data: MarketData) -> dict:
        return {"reasoning": "I only speak to the Analyst Network."}
    
    def format_proposal_message(self, analysis: dict) -> str:
        """Format analysis into readable message for UI"""
        action = analysis.get("action", "HOLD")
        confidence = analysis.get("confidence", 0.5)
        bite_tx = analysis.get("bite_tx", {})
        
        if action == "PROPOSE_ENCRYPTED_EXECUTION":
            return (
                f" **ZERO-KNOWLEDGE EXECUTION DETECTED**\n"
                f"Consensus Score: {confidence*100:.0f}%\n"
                f"Strategy: **ENCRYPTED** (BITE v2)\n"
                f"TxID: `{bite_tx.get('bite_tx_id', 'N/A')}`\n"
                f"Condition: `{bite_tx.get('condition', 'N/A')}`\n\n"
                f"Waiting for network decryption..."
            )
        else:
            return f" **HOLDING** - Consensus {confidence:.2f} insufficient."


# Singleton instance
bull_agent = BullAgent()
