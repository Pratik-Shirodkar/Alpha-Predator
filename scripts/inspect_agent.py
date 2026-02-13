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

def inspect_agent():
    print(f"Agent class: {Agent}")
    print(f"Agent module: {Agent.__module__}")
    
    # Try to find BaseAgent
    try:
        source = inspect.getsource(Agent.__init__)
        print("\nAgent.__init__ source:")
        print(source)
        
        # Look for the internal model
        # We'll use a dummy instance to see its attributes
        print("\nInspecting attributes after instantiation failure (partial)...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_agent()
