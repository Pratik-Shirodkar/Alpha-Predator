import os
import logging
import traceback
import asyncio
from dotenv import load_dotenv
from eth_account import Account

# Load env variables
load_dotenv("backend/.env")

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("debug_output.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug_cdp")

def log(msg):
    logger.info(msg)

async def main():
    api_key_name = os.getenv("CDP_API_KEY_NAME")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET")
    
    log(f"Name: {api_key_name}")

    try:
        from cdp.cdp_client import CdpClient
        log("CDP Client imported.")
        
        # Initialize Client
        client = CdpClient(
            api_key_id=api_key_name,
            api_key_secret=api_key_secret
        )
        log("CDP Client initialized.")
        
        # 1. Create a LOCAL EOA Account (not managed by CDP)
        # We can use a random one or a fixed one for testing
        local_owner = Account.create()
        log(f"Local Owner Address: {local_owner.address}")
        
        # 2. Get/Create Smart Wallet using this LOCAL owner
        # We give it a unique name to avoid conflicts
        wallet_name = f"SmartWallet-{local_owner.address[:8]}"
        log(f"Getting/Creating Smart Wallet with name: {wallet_name}...")
        
        # This call should work because 'local_owner' is a BaseAccount
        wallet = await client.evm.get_or_create_smart_account(
            owner=local_owner, 
            name=wallet_name
        )
        log(f"SUCCESS: Smart Wallet Address: {wallet.address}")
        
        # 3. Check balance
        log("Checking balance...")
        balance = await wallet.balance("eth")
        log(f"Balance: {balance} ETH")

            
    except Exception as e:
        log("-" * 40)
        log(f"ERROR: {type(e).__name__}: {e}")
        log(traceback.format_exc())
        log("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
