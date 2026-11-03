import os, time, requests
from dotenv import load_dotenv

load_dotenv()

_cache = {"token": None, "expires_at": 0}

def generate_access_token() -> str:
    if _cache["token"] and time.time() < _cache["expires_at"]:
        return _cache["token"]

    r = requests.post(
        f"{os.getenv('ZOHO_ACCOUNTS_URL')}/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": os.getenv("ZOHO_CLIENT_ID"),
            "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
            "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN"),
        },
        timeout=30,
    )
    result = r.json()
    if not r.ok or "access_token" not in result:
        raise Exception(f"Zoho token error: {result}")

    _cache["token"] = result["access_token"]
    _cache["expires_at"] = time.time() + int(result.get("expires_in", 3600)) - 60
    return _cache["token"]