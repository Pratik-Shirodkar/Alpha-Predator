import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# 1. Generate EC key (Coinbase usually uses SECP256R1 for wallets)
private_key = ec.generate_private_key(ec.SECP256R1())

# 2. Get DER (Binary) representation
der_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# 3. Base64 encode the DER bytes
wallet_secret = base64.b64encode(der_bytes).decode('utf-8')

print(f"DER (Base64 encoded): {wallet_secret}")

# Save to file just in case
with open("wallet_secret_der_b64.txt", "w") as f:
    f.write(wallet_secret)
