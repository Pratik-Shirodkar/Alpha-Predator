import virtuals_sdk.game.agent
import virtuals_sdk.game.worker
import virtuals_sdk.game.custom_types
import inspect
import sys

def discover():
    try:
        from pydantic.v1 import BaseModel as V1BaseModel
    except ImportError:
        V1BaseModel = None
        
    try:
        from pydantic import BaseModel as V2BaseModel
    except ImportError:
        V2BaseModel = None

    modules = [
        virtuals_sdk.game.agent,
        virtuals_sdk.game.worker,
        virtuals_sdk.game.custom_types
    ]

    print(f"Pydantic V1 available: {V1BaseModel is not None}")
    print(f"Pydantic V2 available: {V2BaseModel is not None}")

    for module in modules:
        print(f"\nScanning module: {module.__name__}")
        for name, cls in inspect.getmembers(module, inspect.isclass):
            is_v1 = V1BaseModel and issubclass(cls, V1BaseModel)
            is_v2 = V2BaseModel and issubclass(cls, V2BaseModel)
            
            if is_v1 or is_v2:
                version = "V1" if is_v1 else "V2"
                print(f" - Found model: {name} ({version})")
                
                # Check for 'goal' field
                if is_v1:
                    fields = cls.__fields__.keys()
                    required = [f.name for f in cls.__fields__.values() if f.required]
                else:
                    fields = cls.model_fields.keys()
                    required = [f_name for f_name, f_info in cls.model_fields.items() if f_info.is_required()]
                
                print(f"   Fields: {list(fields)}")
                print(f"   Required: {required}")
                if "goal" in fields:
                    print(f"   *** GOAL FIELD FOUND IN {name} ***")

if __name__ == "__main__":
    discover()
