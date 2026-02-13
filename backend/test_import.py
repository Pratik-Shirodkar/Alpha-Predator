import sys
import os
import traceback

print(f"CWD: {os.getcwd()}")
sys.path.append(os.getcwd())
print(f"Path: {sys.path}")

try:
    print("0. Checking Pydantic...")
    import pydantic
    from pydantic_settings import BaseSettings
    print(f"   Success! Pydantic {pydantic.VERSION} found.")
except Exception:
    print("   FAIL: Pydantic or pydantic-settings missing.")
    traceback.print_exc()

try:
    print("0.5. Checking config.settings...")
    from config.settings import settings
    print("   Success! Config loaded.")
except Exception:
    print("   FAIL: config.settings failed.")
    traceback.print_exc()

try:
    print("1. Attempting to import agents.base_agent...")
    from agents.base_agent import BaseAgent
    print("   SalesForce! BaseAgent imported.")
except Exception:
    traceback.print_exc()

try:
    print("2. Attempting to import execution.payment_manager...")
    from execution.payment_manager import payment_manager
    print("   Success! PaymentManager imported.")
except Exception:
    traceback.print_exc()

try:
    print("3. Attempting to import tools.premium_market_insight...")
    from tools.premium_market_insight import premium_tool
    print("   Success! PremiumTool imported.")
except Exception:
    traceback.print_exc()

try:
    print("4. Attempting to import agents.bull_agent...")
    from agents.bull_agent import bull_agent
    print("   Success! BullAgent imported.")
except Exception:
    traceback.print_exc()
