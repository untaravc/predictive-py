import httpx

API_TOKEN = "secret-bearer-token"

async def get_external_data(url):
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
    print("Persistent cron task executed..")