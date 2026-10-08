# HS DEVS AUTH - Python Client SDK (`hsauth.py`)

Official Python client library for [HS DEVS AUTH](https://hsauth.mujahid.xyz).

## Highlights
- **Zero Third-Party Dependencies**: Pure Python standard library (`urllib.request`, `json`, `platform`, `hashlib`, `threading`).
- **Cross-Platform**: Runs on Windows, Linux, and macOS without extra binary wheels.
- **In-App Live Messaging & Remote Killswitch**: Native background pulse with callback support.
- **Remote Variables & Files**: Download protected variables and binary files securely.

## Quick Start
```python
from hsauth import api

HSAuthApp = api(
    name="YourAppName",
    ownerid="your_app_identifier_here",
    version="1.0",
    api_url="https://hsauth.mujahid.xyz/api/1.3/"
)

# 1. Initialize
HSAuthApp.init()

# 2. Authenticate
res = HSAuthApp.license("HSAUTH-XXXX-XXXX-XXXX-XXXX")
if res.get("success"):
    print("Logged in!")
    HSAuthApp.start_heartbeat(30)
```
