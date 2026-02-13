import sys
import os
import io
import json

# Force UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to sys.path (matches how main.py runs)
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from agents.virtuals_agent import virtuals_agent

def verify():
    print("=" * 60)
    print("  Virtuals G.A.M.E. Framework — Wrapper Verification")
    print("=" * 60)

    # 1. Check agent metadata
    agent = virtuals_agent.agent
    print(f"\n  Agent Name : {agent.name}")
    print(f"  Goal       : {agent.goal[:80]}...")
    print(f"  Workers    : {len(agent.workers)}")

    # 2. Check workers + functions
    for w in agent.workers:
        fn_names = [f.name for f in w.functions]
        print(f"    -> {w.name}  functions={fn_names}")

    # 3. Capability manifest
    caps = virtuals_agent.capabilities()
    print(f"\n  Capability Manifest:")
    print(f"  {json.dumps(caps, indent=2)}")

    print("\n" + "=" * 60)
    print("  VERIFICATION PASSED")
    print("=" * 60)

if __name__ == "__main__":
    verify()
