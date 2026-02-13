import sys
import os
import io

# Force UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from virtuals_sdk.game.agent import Agent, Function
from virtuals_sdk.game.worker import Worker
from pydantic.v1 import ValidationError

def test():
    api_key = "local_demo_key"
    print("Testing Agent instantiation...")
    try:
        # Minimal Worker
        def dummy_fn(s): return "ok"
        w = Worker(
            api_key=api_key,
            name="TestWorker",
            description="Test",
            functions=[Function(fn=dummy_fn, description="Test fn")]
        )
        
        # Minimal Agent
        a = Agent(
            api_key=api_key,
            name="TestAgent",
            description="Test Desc",
            workers=[w],
            goal="Test Goal"
        )
        print("Agent instantiated successfully!")
    except ValidationError as e:
        print(f"Caught ValidationError for {e.model.__name__}!")
        for error in e.errors():
            print(f" - Field: {error.get('loc')}, Msg: {error.get('msg')}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test()
