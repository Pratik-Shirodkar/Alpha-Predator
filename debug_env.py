import os
from dotenv import load_dotenv

load_dotenv("backend/.env") # Explicitly point to file

key_name = os.getenv("CDP_API_KEY_NAME")
private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY")

print(f"Key Name: {key_name}")
if private_key:
    print(f"Private Key Loaded. Length: {len(private_key)}")
    print(f"Starts with: {private_key[:30]}...")
    if "\\n" in private_key:
        print("Contains literal backslash-n")
    if "\n" in private_key:
        print("Contains actual newline")
else:
    print("Private Key NOT loaded")
