import sys
import os
import io

# Force UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from virtuals_sdk.game.agent import Agent
import inspect

def inspect_base():
    # Find BaseAgent by looking at the closure or globals of Agent.__init__
    init_func = Agent.__init__
    globals_dict = init_func.__globals__
    
    base_agent_cls = globals_dict.get('BaseAgent')
    print(f"BaseAgent class: {base_agent_cls}")
    if base_agent_cls:
        print(f"BaseAgent module: {base_agent_cls.__module__}")
        try:
            print(f"BaseAgent fields (Pydantic V1): {base_agent_cls.__fields__.keys()}")
        except:
            try:
                print(f"BaseAgent fields (Pydantic V2): {base_agent_cls.model_fields.keys()}")
            except:
                print("BaseAgent does not appear to be a Pydantic model directly.")
        
        try:
            print("\nBaseAgent.__init__ signature:")
            print(inspect.signature(base_agent_cls.__init__))
        except Exception as e:
            print(f"Error getting signature: {e}")

if __name__ == "__main__":
    inspect_base()
