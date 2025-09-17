import httpx
from datetime import datetime
from app.configs.ind_power_conf import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

API_TOKEN = "secret-bearer-token"

async def fetch_data_with_bearer_token(url):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx/5xx errors
            data = response.json()
            return {"success": True, "data": data}
    except httpx.HTTPError as e:
        return {"success": False, "data": data}
    
async def periodic_call_api_task():
    now = datetime.now()

    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("Persistent cron task executed on: " + formatted_time)

async def fetch_data_with_basic_auth(url: str):
    try:
        # print("indonesiapower/vendor.ugm", BASIC_AUTH_PASSWORD)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
        return {"success": True, "result": data}
    except httpx.HTTPError as e:
        return {"success": False, "error": str(e)}