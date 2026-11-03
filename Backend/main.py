import os, requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from zoho_auth import generate_access_token
from zoho_analytics import get_organizations, get_workspaces, get_views,get_view_data

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/zoho/generate-token")
def generate_token():
    try:
        generate_access_token()
        return {"message": "Access token generated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/zoho/orgs")
# def get_orgs():
#     try:
#         token = generate_access_token()
#         r = requests.get(
#             f"{os.getenv('ZOHO_ANALYTICS_URL')}/restapi/v2/orgs",
#             headers={"Authorization": f"Zoho-oauthtoken {token}"},
#             timeout=30,
#         )
#         if not r.ok:
#             raise HTTPException(status_code=r.status_code, detail=r.text)
#         return r.json()  # { data: { orgs: [...] } }
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/zoho/orgs")
def get_orgs():
    try:
        return get_organizations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/zoho/orgs/{org_id}/workspaces")
def api_workspaces(org_id: str):
    try:
        return get_workspaces(org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
        
@app.get("/api/zoho/orgs/{org_id}/workspaces/{workspace_id}/views")
def api_views(org_id: str, workspace_id: str):
    try:
        return get_views(org_id, workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/api/zoho/orgs/{org_id}/workspaces/{workspace_id}/views/{view_id}/data")
def api_view_data(org_id: str, workspace_id: str, view_id: str):
    try:
        result = get_view_data(org_id, workspace_id, view_id)
        rows = result.get("data", [])
        if not isinstance(rows, list):
            return result  # unexpected shape, send it as is
        return {"data": {"rows": rows[:200], "total": len(rows)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))