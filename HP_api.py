
from flask import Flask, request, jsonify
import requests
from urllib.parse import urlencode
import json
import pandas as pd 

app = Flask(__name__)

# ============================================================
# Zoho Credentials (USA Region)
# ============================================================
CLIENT_ID = "1000.CQOT74EJL83CJ979QD2ZN6Q59MXD0C"
CLIENT_SECRET = "4a826f5eea1620bdf9ba53d76d73e67b41a798e5d2"
REDIRECT_URI = "http://localhost:5000/callback"

# Store tokens temporarily (in production, use database)
tokens = {}

# ============================================================
# Route 1: Home Page
# ============================================================
@app.route("/get-hp-data")
def get_hp_data():

    token_url = "https://login.external.hp.com/as/token.oauth2"


# Your HP Credentials
client_id = "4fedb219-8f3f-4d7e-8a83-f9b8018c1757"
client_secret = "InjUzjaHW7h5l2yNwFN5o1LpThyREZKKVa99YVatUkEovgst4X"

# Form data
token_url = "https://login.external.hp.com/as/token.oauth2"

response = requests.post(
    token_url,
    auth=(client_id, client_secret),
    data={
        "grant_type": "client_credentials"
    }
)

# print("Token Status:", response.status_code)
# print(response.text)

token = response.json()["access_token"]

# print("\nAccess Token:")
# print(token)

# Step 2 - Call Customer Insight API

url = "https://partner.api.hp.com/partner-data/unison/v1/mastercustomerinsights"

headers = {
    "token": token,
    "x-api-key": "3qb10o1qb06fe0oqbbt4b9662redxe9e"
}

params = {
    "id": "2-SISC-13084"
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

# print("\nHP API Status:", response.status_code)
# print(response.text)

# Step 3 - Convert to DataFrame

data = response.json()

df = pd.json_normalize(data)

# print(df)

# df.to_excel("HP_CustomerInsight.xlsx", index=False)

print("Data exported successfully.")

   


@app.route("/")
def home():
    if "access_token" in tokens:
        return f'''
        <h1>🎉 Zoho Analytics OAuth - Authenticated</h1>
        <p style="color: green; font-size: 18px;">✅ You are logged in!</p>
        <p><a href="/dashboard" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Go to Dashboard</a></p>
        <p><a href="/logout" style="padding: 10px 20px; background-color: #f44336; color: white; text-decoration: none; border-radius: 5px;">Logout</a></p>
        '''
    else:
        return '''
        <h1>🔐 Zoho Analytics OAuth Integration</h1>
        <p>Welcome! Click the button below to login with Zoho.</p>
        <p><a href="/login" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;">Login with Zoho</a></p>
        '''

# ============================================================
# Route 2: Login - Redirect to Zoho
# ============================================================
@app.route("/login")
def login():
    auth_url = "https://accounts.zoho.com/oauth/v2/auth"
    
    params = {
        "scope": "ZohoAnalytics.data.all,ZohoAnalytics.metadata.read",
        "client_id": CLIENT_ID,
        "response_type": "code",
        "access_type": "offline",
        "redirect_uri": REDIRECT_URI
    }
    
    full_url = f"{auth_url}?{urlencode(params)}"
    # print(f"\n📍 Authorization URL: {full_url}")

    
    return f'''
    <h1>🔐 Zoho Login</h1>
    <p>Click the link below to authorize with Zoho Analytics:</p>
    <p><a href="{full_url}" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;">Click here to authorize with Zoho</a></p>
    '''

# ============================================================
# Route 3: Callback - Handle Authorization Code
# ============================================================
@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    location = request.args.get("location")
    
    # print(f"\n{'='*60}")
    print("CALLBACK RECEIVED")
    # print(f"{'='*60}")
    
    # Check for errors from Zoho
    if error:
        # print(f"❌ ERROR from Zoho: {error}")
        return f'''
        <h1>❌ Authorization Failed</h1>
        <p>Error: {error}</p>
        <p><a href="/login">Try Again</a></p>
        '''
    
    if not code:
        # print("❌ No authorization code received")
        return "Error: No authorization code received"
    
    # print(f"✅ Authorization code received: {code[:50]}...")
    if location:
        print(f"📍 Location: {location}")
    
    # Exchange code for access token
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    print(f"\n📤 Exchanging code for access token...")
    # print(f"   Token URL: {token_url}")
    # print(f"   Client ID: {CLIENT_ID}")
    
    try:
        response = requests.post(token_url, data=data)
        token_data = response.json()

        print("\n📥 Response from Zoho:")
        print(json.dumps(token_data, indent=2))

# Check whether access token was received
        if "access_token" not in token_data:
            return f"""
            <h1>❌ Error Getting Token</h1>
            <pre>{json.dumps(token_data, indent=2)}</pre>
             """

# Save the access token
        access_token = token_data["access_token"]

# Use the API domain returned by Zoho
        api_domain = token_data["api_domain"]

# Create Zoho Authorization Header
        zoho_headers = {
              "Authorization": f"Zoho-oauthtoken {access_token}"
            }

# Call Zoho Analytics API
        ANALYTICS_SERVER = "https://analyticsapi.zoho.com"

        url = f"{ANALYTICS_SERVER}/restapi/v2/orgs"

        # url = f"{api_domain}/analyticsapi/v2/orgs"

        response = requests.get(
        url,
         headers=zoho_headers
        )

        print("\n========== ZOHO ORGS ==========")
        print("Status :", response.status_code)
        print(response.text)

        org_id = "669970455"

        url = f"https://analyticsapi.zoho.com/restapi/v2/orgs/{org_id}/workspaces"

        response = requests.get(
    url,
    headers=zoho_headers
)

        print("========== WORKSPACES ==========")
        print(response.status_code)
        print(response.text)

        

        # if "access_token" in token_data:
        #     tokens["access_token"] = token_data["access_token"]
        #     tokens["refresh_token"] = token_data.get("refresh_token")
        #     tokens["expires_in"] = token_data.get("expires_in")
            
        #     print(f"\n✅ SUCCESS! Access token obtained")
        #     print(f"{'='*60}\n")
            
        #     return f'''
        #     <h1>✅ Authorization Successful!</h1>
        #     <p style="color: green; font-size: 16px;">You have been authenticated with Zoho Analytics.</p>
            
        #     <h2>Token Details:</h2>
        #     <ul>
        #         <li><strong>Access Token:</strong> {token_data['access_token'][:50]}...</li>
        #         <li><strong>Token Type:</strong> {token_data.get('token_type')}</li>
        #         <li><strong>Expires In:</strong> {token_data.get('expires_in')} seconds</li>
        #         <li><strong>Has Refresh Token:</strong> {'Yes' if token_data.get('refresh_token') else 'No'}</li>
        #     </ul>
            
        #     <p><a href="/dashboard" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Go to Dashboard</a></p>
        #     <p><a href="/" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">Home</a></p>
        #     '''
        # else:
        #     print(f"\n❌ ERROR: {token_data}")
        #     print(f"{'='*60}\n")
            
        return f'''
            <h1>❌ Error Getting Token</h1>
            <p style="color: red;">Zoho returned an error:</p>
            <pre>{json.dumps(token_data, indent=2)}</pre>
            <p><a href="/login">Try Again</a></p>
            '''
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        print(f"{'='*60}\n")
        
        return f'''
        <h1>❌ Error</h1>
        <p style="color: red;">{e}</p>
        <p><a href="/login">Try Again</a></p>
        



        '''
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ZOHO ANALYTICS OAUTH INTEGRATION SERVER")
    print("=" * 60)
    print(f"Client ID: {CLIENT_ID}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print("=" * 60)
    print("📍 Visit: http://localhost:5000")
    print("=" * 60)
    print("Before app.run")
    app.run(debug=True, port=5000)
    print("After app.run")




 


