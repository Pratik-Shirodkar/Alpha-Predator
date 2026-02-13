
import sys
import os
import asyncio
import logging
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport

# Add root to path so we can import backend
sys.path.append(os.getcwd())
# Add backend to path so internal imports work
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Import Backend Components
# Import Backend Components
from main import app
from tools.analyst_network import AnalystNetworkTool
from execution.budget_manager import budget_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

async def run_test():
    print("\n--- STARTING INTEGRATION TEST: Analyst Pay Flow ---\n")
    
    # 1. Setup Transport to talk to FastAPI app directly
    transport = ASGITransport(app=app)
    
    # 2. Patch httpx.AsyncClient to use our transport
    # The tool creates a new client each time, so we need to patch the class constructor
    # We want to return a client that talks to our ASGITransport
    
    # We create a specific instance to use
    test_client = AsyncClient(transport=transport, base_url="http://test")
    
    # We can't easily patch the class to return an instance because __aenter__ is called on result.
    # But AsyncClient is a context manager.
    # The code does: async with httpx.AsyncClient() as client:
    
    # So if we patch httpx.AsyncClient, the return value of the call (constructor) 
    # must be an object whose __aenter__ returns our test_client.
    
    class MockClientContext:
        async def __aenter__(self):
            return test_client
        async def __aexit__(self, exc_type, exc_value, traceback):
            pass
            
    with patch('httpx.AsyncClient', return_value=MockClientContext()):
        
        # 3. Initialize Tool (base_url is ignored by our mock client, but good practice)
        tool = AnalystNetworkTool(base_url="http://test")
        
        # 4. Verify getting 402 and paying
        # We need to ensure budget manager allows it
        # Reset budget for clean test
        from decimal import Decimal
        budget_manager.total_spend = Decimal("0.00") 
        budget_manager.purchases = []
        
        print(f"[Test] Initial Budget Spend: ${budget_manager.total_spend}")
        print("[Test] Querying 'technical' analyst (Expect 402 -> Pay -> 200)...")
        
        # EXECUTE
        result = await tool.query_analyst("technical", "Integration Test Justification")
        
        # VERIFY
        if "error" in result:
            print(f"❌ FAILED: received error: {result['error']}")
        else:
            print(f"✅ SUCCESS: Got result keys: {list(result.keys())}")
            print(f"   Analyst: {result.get('analyst')}")
            print(f"   Score: {result.get('score')}")
            
        # 5. Check Budget
        print(f"\n[Test] Final Budget Spend: ${budget_manager.total_spend}")
        if budget_manager.total_spend > 0:
             print("✅ Budget updated correctly (Simulated Payment).")
        else:
             print("❌ Budget did not update.")

if __name__ == "__main__":
    asyncio.run(run_test())
