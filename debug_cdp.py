import sys
import os

print(f"Python: {sys.executable}")
try:
    import cdp
    print(f"CDP imported from: {cdp.__file__}")
    print(f"Dir(cdp): {dir(cdp)}")
    
    if hasattr(cdp, 'Cdp'):
        print("Cdp class found in cdp module")
    else:
        print("Cdp class NOT found in cdp module")
        
    if hasattr(cdp, 'Wallet'):
        print("Wallet class found in cdp module")
    else:
        print("Wallet class NOT found in cdp module")

except ImportError as e:
    print(f"Error importing cdp: {e}")

