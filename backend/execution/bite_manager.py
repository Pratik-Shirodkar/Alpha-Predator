import logging
import json
import hashlib
import asyncio
import httpx
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BiteManager:
    """
    Integrates with SKALE's BITE v2 (Blockchain Integrated Threshold Encryption)
    via the official BITE V2 Sandbox 2 chain, using the real @skalenetwork/bite SDK
    through a Next.js API bridge.
    
    Chain: BITE V2 Sandbox 2
    RPC: https://base-sepolia-testnet.skalenodes.com/v1/bite-v2-sandbox
    Chain ID: 103698795
    BITE Contract: 0xc4083B1E81ceb461Ccef3FDa8A9F24F0d764B6D8
    """
    
    def __init__(self, bridge_url: str = "http://localhost:3000/api/bite/encrypt"):
        self.encrypted_pool = {}
        self.bridge_url = bridge_url
        self.real_sdk_used = False

    async def encrypt_intent(self, intent: Dict[str, Any], condition: str) -> Dict[str, str]:
        """
        Encrypts a trade intent using the REAL SKALE BITE v2 SDK via the Next.js bridge.
        """
        tx_id = f"bite_{hashlib.md5(json.dumps(intent).encode()).hexdigest()[:8]}"
        bite_receipt = None
        encrypted_blob = f"mock_bite_{tx_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.bridge_url,
                    json={
                        "intent": intent,
                        "condition": condition
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    bite_receipt = response.json()
                    encrypted_blob = bite_receipt.get("encryptedMessage", encrypted_blob)
                    self.real_sdk_used = True
                    logger.info(f"BITE: Real SDK encryption on BITE V2 Sandbox 2 successful!")
                    logger.info(f"BITE: Chain ID: {bite_receipt.get('chainId')}")
                    logger.info(f"BITE: Encrypted length: {bite_receipt.get('encryptedMessageLength')}")
                    if bite_receipt.get("committee"):
                        logger.info(f"BITE: Epoch: {bite_receipt['committee'].get('epochId')}")
                else:
                    logger.warning(f"BITE: SDK bridge returned {response.status_code}. Using mock.")
        except Exception as e:
            logger.error(f"BITE: SDK bridge failed ({e}). Using mock.")

        # Store in mempool
        self.encrypted_pool[tx_id] = {
            "blob": encrypted_blob,
            "real_intent": intent, 
            "condition": condition,
            "status": "ENCRYPTED",
            "real_sdk": self.real_sdk_used,
            "bite_receipt": bite_receipt
        }
        
        logger.info(f"BITE: Intent {tx_id} encrypted. Condition: {condition}")
        
        # Build broadcast data with real BITE info
        broadcast_data: Dict[str, Any] = {
            "bite_tx_id": tx_id,
            "encrypted_blob": encrypted_blob[:120] + "..." if len(encrypted_blob) > 120 else encrypted_blob,
            "condition": condition,
            "sdk": "@skalenetwork/bite" if self.real_sdk_used else "mock",
            "chain": "BITE V2 Sandbox 2" if self.real_sdk_used else "Mock",
            "chainId": 103698795 if self.real_sdk_used else 0,
        }
        
        if bite_receipt and bite_receipt.get("committee"):
            broadcast_data["committee"] = bite_receipt["committee"]
            broadcast_data["encryptedLength"] = bite_receipt.get("encryptedMessageLength", 0)
        
        # Broadcast BITE Event
        from api.websocket import connection_manager
        asyncio.create_task(connection_manager.broadcast_status({
            "type": "bite_encrypted",
            "data": broadcast_data
        }))
        
        return {
            "bite_tx_id": tx_id,
            "encrypted_blob": encrypted_blob,
            "condition": condition
        }

    def try_decrypt_and_execute(self, bite_tx_id: str, current_market_data: Any) -> Dict[str, Any]:
        """
        Checks conditions and triggers decryption.
        In production, SKALE consensus handles this automatically via onDecrypt().
        """
        tx = self.encrypted_pool.get(bite_tx_id)
        if not tx:
            return {"error": "Tx not found"}
            
        condition = tx["condition"]
        try:
            param, operator, value = condition.split(" ")
            value = float(value)
            
            current_val = 0.0
            if param == "CONFIDENCE":
                current_val = current_market_data.get("consensus_score", 0.0)
            
            met = False
            if operator == ">":
                met = current_val > value
                
            if met:
                tx["status"] = "DECRYPTED_AND_EXECUTED"
                logger.info(f"BITE: Condition Met ({current_val} {operator} {value}). Decrypting...")
                return {
                    "status": "EXECUTED",
                    "decrypted_intent": tx["real_intent"]
                }
            else:
                logger.info(f"BITE: Condition NOT Met ({current_val} {operator} {value}). Keeping encrypted.")
                return {"status": "PENDING_CONDITION"}
                
        except Exception as e:
            logger.error(f"BITE Execution Error: {e}")
            return {"error": str(e)}

# Singleton
bite_manager = BiteManager()
