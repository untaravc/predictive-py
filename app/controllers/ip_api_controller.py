from app.models.user import User, UserUpdate, UserCreate
from fastapi import Depends, HTTPException
from app.services.ip_api_service import get_external_data

async def get_ip_api_data():
    url = "https://jsonplaceholder.typicode.com/posts"
    result = await get_external_data(url)

    return result