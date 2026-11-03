import os, requests
from dotenv import load_dotenv

load_dotenv()

r = requests.post(
    "https://accounts.zoho.com/oauth/v2/token",
    data={
        "grant_type": "authorization_code",
        "client_id": "1000.Q5SSUITJ6VXT6JN2299X65VCGPYP6A",
        "client_secret": "512ebc6811b4288a4e7caa479934deef5208486f5d",
        "code": "1000.96cee9e532d0d1f44ef71f7feaa57798.067d239206b0d17819aa810148c41809",
    },
    timeout=30,
)
print(r.json())