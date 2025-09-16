from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient

async def pull_data():
    client = PIWebApiClient("https://test.osisoft.com/piwebapi", useKerberos=False, username="indonesiapower\vendor.ugm", password="password", verifySsl=True)
    print(client)

