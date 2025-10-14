import httpx
from datetime import datetime
from app.configs.base_conf import settings

API_TOKEN = "secret-bearer-token"
    
async def periodic_call_api_task():
    now = datetime.now()

    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("Persistent cron task executed on: " + formatted_time)

async def fetch_data_with_basic_auth(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
        return {"success": True, "result": data}
    except httpx.HTTPError as e:
        return {"success": False, "error": str(e)}