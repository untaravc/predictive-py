from app.models.user import User, UserUpdate, UserCreate
from fastapi import Depends, HTTPException
from app.services.ip_api_service import get_external_data
from app.services.pi_webapi import pull_data


async def get_ip_api_data():
    url = "https://jsonplaceholder.typicode.com/posts"
    result = await get_external_data(url)

    return result

async def pull_data_pi():
    result = await pull_data()
    return result

async def point_seach():
    url = "https://piwebapi.plnindonesiapower.co.id/piwebapi/points/search?dataserverwebid=F1DS2dBunJOlC0ifiqTkEvHTBAUEkx&query=SKR1*"