
from zoho_auth import generate_access_token

try:

    token = generate_access_token()

    print("Zoho Access Token Generated Successfully!")

    print("Token received:", bool(token))

except Exception as e:

    print("Error:", str(e))
