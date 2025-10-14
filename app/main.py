# main.py
import uvicorn
import asyncio
from fastapi import FastAPI, Depends
from app.router import api
from app.services.lifespan_service import lifespan
from app.utils.oracle_db import test_connection, get_connection

# FastAPI app
app = FastAPI(lifespan=lifespan)

app.include_router(api.router)

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8020, reload=True)