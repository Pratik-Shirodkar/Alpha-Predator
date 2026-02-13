try:
    from cdp.cdp_client import CdpClient
    print("SUCCESS: CdpClient imported")
    print(f"CdpClient: {CdpClient}")
except ImportError as e:
    print(f"ERROR: {e}")
