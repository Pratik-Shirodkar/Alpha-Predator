
import sys
import os
import traceback
import asyncio

sys.path.append(os.getcwd())

try:
    from backend.run_verification import main
    asyncio.run(main())
except Exception:
    traceback.print_exc()
