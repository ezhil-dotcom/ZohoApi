import requests
from zoho_auth import generate_access_token
import time
import json

def get_organizations():

    access_token = generate_access_token()

    url = "https://analyticsapi.zoho.com/restapi/v2/orgs"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print("Status Code:", response.status_code)

    try:
        result = response.json()
    except ValueError:
        print("Response:", response.text)
        return

    if response.status_code == 200:
        # print("\nOrganization Details:")

        orgs = result.get("data", {}).get("orgs", [])

        # for org in orgs:
        #     print("Organization Name:", org.get("orgName"))
        #     print("Organization ID:", org.get("orgId"))
    else:
         print("Error:", result)

    return result

def get_workspaces(org_id):
    response = requests.get(
        "https://analyticsapi.zoho.com/restapi/v2/workspaces",
        headers={
            "Authorization": f"Zoho-oauthtoken {generate_access_token()}",
            "ZANALYTICS-ORGID": org_id,
        },
        timeout=30,
    )

    result = response.json()
    # print("Workspaces status:", response.status_code)

    if response.status_code != 200:
        raise Exception(f"{response.status_code}: {result}")

    # data = result.get("data", {})
    # for ws in data.get("ownedWorkspaces", []) + data.get("sharedWorkspaces", []):
    #     print("Workspace:", ws.get("workspaceName"), "| ID:", ws.get("workspaceId"))

    return result

def get_views(org_id, workspace_id):
    print("views startes here")
    response = requests.get(
        f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/views",
        headers={
            "Authorization": f"Zoho-oauthtoken {generate_access_token()}",
            "ZANALYTICS-ORGID": org_id,
        },
        timeout=30,
    )

    result = response.json()
    # print("Views status:", response.status_code)

    if response.status_code != 200:
        raise Exception(f"{response.status_code}: {result}")

    # for v in result.get("data", {}).get("views", []):
    #     if v.get("viewType") == "QueryTable":
    #         print("View:", v.get("viewName"), "| ID:", v.get("viewId"), "| Type:", v.get("viewType"))
        
    return result

import json  # add to the imports at the top of the file


def get_view_data(org_id, workspace_id, view_id, max_wait=300):
    headers = {
        "Authorization": f"Zoho-oauthtoken {generate_access_token()}",
        "ZANALYTICS-ORGID": org_id,
    }
    base = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}"

    # 1. Create the export job (this is what returns the job ID)
    r = requests.get(
        f"{base}/views/{view_id}/data",
        headers=headers,
        params={"CONFIG": json.dumps({"responseFormat": "json"})},
        timeout=60,
    )
    body = r.json()
    print("Create job:", r.status_code, body)
    if r.status_code != 200:
        raise Exception(f"{r.status_code}: {body}")
    job_id = body["data"]["jobId"]
    print("Job ID:", job_id)

    # 2. Poll until the job is finished
    waited = 0
    while True:
        s = requests.get(f"{base}/exportjobs/{job_id}", headers=headers, timeout=30)
        sbody = s.json()
        if s.status_code != 200:
            raise Exception(f"{s.status_code}: {sbody}")

        status = str(sbody.get("data", {}).get("jobStatus", "")).upper()
        print("Job status:", status)

        if "COMPLETED" in status:
            break
        if any(word in status for word in ("ERROR", "FAIL", "ABORT")):
            raise Exception(f"Export job failed: {sbody}")
        if waited >= max_wait:
            raise Exception(f"Export job timed out after {max_wait}s: {sbody}")

        time.sleep(2)
        waited += 2

    # 3. Download the data
    d = requests.get(f"{base}/exportjobs/{job_id}/data", headers=headers, timeout=120)
    print("Download status:", d.status_code)
    if d.status_code != 200:
        raise Exception(f"{d.status_code}: {d.text}")

    try:
        result = d.json()
    except ValueError:
        raise Exception(f"Data was not JSON: {d.text[:300]}")

    print("Top-level keys:", list(result.keys()) if isinstance(result, dict) else type(result))
    return result

if __name__ == "__main__":
    #get_organizations()
    get_view_data("669970455", "1744699000000069001", "1744699000117545002")