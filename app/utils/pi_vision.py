from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from app.configs.base_conf import settings

def getPIWebApiClient():
    client = PIWebApiClient(settings.OSISOF_URL, False, settings.OSISOF_USER, settings.OSISOF_PASSWORD, verifySsl=False)
    return client 