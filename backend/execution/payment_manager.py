import os
import json
import logging
import asyncio
import time
import traceback
from decimal import Decimal
from typing import Optional, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PaymentManager:
    """
    Manages crypto payments using Coinbase Developer Platform (CDP) Wallets (SDK v1.x).
    Handles x402 payment flows and persistent wallet management using a local EOA owner.
    """
    
    def __init__(self):
        self.client = None
        self.wallet = None  # Smart Account instance
        self.owner_account = None # Local EOA (signer)
        self.mode = "mock" # "mock" or "real"
        self.address = "0xMockAddress123456789"
        self.network = "base-sepolia"
        self.wallet_file = "wallet_seed.json"
        self.audit_log = []

    async def initialize(self):
        """Schedule initialization in background so server can start immediately."""
        asyncio.create_task(self._do_initialize())

    async def _do_initialize(self):
        """Actual initialization logic."""
        try:
            load_dotenv()
            
            api_key_name = os.getenv("CDP_API_KEY_NAME")
            api_key_secret = os.getenv("CDP_API_KEY_SECRET")
            self.network = os.getenv("CDP_NETWORK", "base-sepolia")

            if not api_key_name or not api_key_secret:
                logger.warning("CDP credentials not found. Initializing in MOCK mode.")
                self.mode = "mock"
                return

            # Deferred imports to avoid circular issues or missing dependencies in mock
            from cdp.cdp_client import CdpClient
            from eth_account import Account
            
            logger.info("Initializing CDP Client...")
            self.client = CdpClient(
                api_key_id=api_key_name,
                api_key_secret=api_key_secret
            )
            
            # Load or generate Owner Account (Local EOA)
            if os.path.exists(self.wallet_file):
                logger.info("Loading existing wallet seed...")
                with open(self.wallet_file, 'r') as f:
                    data = json.load(f)
                    private_key = data.get("private_key")
                    self.owner_account = Account.from_key(private_key)
                logger.info(f"Loaded existing owner EOA: {self.owner_account.address}")
            else:
                logger.info("Creating new wallet seed...")
                self.owner_account = Account.create()
                with open(self.wallet_file, 'w') as f:
                    json.dump({
                        "private_key": self.owner_account.key.hex(), 
                        "address": self.owner_account.address
                    }, f)
                logger.info(f"Created new owner EOA: {self.owner_account.address}")

            # Get or create Smart Account with this owner
            wallet_name = "BullAgentSmartWallet"
            logger.info(f"Retrieving Smart Account: {wallet_name}...")
            
            self.wallet = await self.client.evm.get_or_create_smart_account(
                owner=self.owner_account,
                name=wallet_name
            )
            
            self.mode = "real"
            self.address = self.wallet.address
            logger.info(f"Payment Manager Mode: REAL (CDP)")
            logger.info(f"Smart Wallet Address: {self.address}")

            # Initial balance check and broadcast
            await self.broadcast_balance()

        except Exception as e:
            logger.error(f"CDP WALLET INITIALIZATION FAILED: {str(e)}")
            logger.error(traceback.format_exc())
            logger.warning("Falling back to MOCK mode.")
            self.mode = "mock"
            self.address = "0xMockAddress123456789"

    async def get_balance(self, asset_id: str = "eth") -> Decimal:
        """Get the current wallet balance."""
        if self.mode == "mock":
            return Decimal("100.00")
        
        try:
            logger.info(f"DEBUG: get_balance calling list_token_balances for {self.wallet.address} on {self.network}...")
            # Use EvmClient to get balance for the smart account
            balances = await self.client.evm.list_token_balances(
                address=self.wallet.address,
                network=self.network
            )
            logger.info(f"DEBUG: list_token_balances returned {len(balances.balances)} entries.")
            
            # Look for the specified asset (defaulting to ETH)
            for b in balances.balances:
                if b.asset_id.lower() == asset_id.lower():
                    return Decimal(str(b.amount))
            
            return Decimal("0.00")
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return Decimal("0.00")

    async def pay(self, address: str, amount: float, asset_id: str = "eth", reason: str = "") -> Dict:
        """Process a real or mock payment."""
        logger.info(f"PAY REQUEST: Paying {amount} {asset_id} to {address} ({reason})")
        
        if self.mode == "mock":
            await asyncio.sleep(1) # simulate network latency
            receipt = {
                "status": "success",
                "transaction_hash": f"0xMockTx{os.urandom(16).hex()}",
                "amount": amount,
                "asset": asset_id,
                "recipient": address,
                "reason": reason,
                "timestamp": time.time()
            }
            self.audit_log.append(receipt)
            logger.info(f"MOCK PAYMENT SUCCESS: {receipt['transaction_hash']}")
            return receipt

        try:
            # Real CDP Transfer
            # Note: amount should be float for wallet.transfer (SDK handles units)
            invocation = await self.wallet.transfer(
                amount=amount,
                asset_id=asset_id,
                destination=address
            )
            
            logger.info(f"Waiting for transaction: {invocation.transaction_hash}...")
            await invocation.wait()
            
            receipt = {
                "status": "success",
                "transaction_hash": invocation.transaction_hash,
                "amount": amount,
                "asset": asset_id,
                "recipient": address,
                "reason": reason,
                "timestamp": time.time()
            }
            self.audit_log.append(receipt)
            logger.info(f"REAL PAYMENT SUCCESS: {invocation.transaction_hash}")
            
            # Broadcast updated balance
            await self.broadcast_balance()
            
            return receipt

        except Exception as e:
            logger.error(f"PAYMENT FAILED: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": time.time()
            }

    def get_address(self) -> str:
        return self.address

    async def broadcast_balance(self):
        """Broadcast current wallet balance to UI via Websocket."""
        try:
            from api.websocket import connection_manager
            balance = await self.get_balance()
            
            await connection_manager.broadcast_status({
                "type": "wallet_update",
                "data": {
                    "address": self.address,
                    "balance": float(balance),
                    "mode": self.mode
                }
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast balance: {e}")

# Singleton instance
payment_manager = PaymentManager()
