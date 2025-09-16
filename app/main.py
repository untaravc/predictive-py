# main.py
from fastapi import FastAPI, Depends
import uvicorn
import app.configs.ind_power_conf, app.configs.oracle_conf
from app.utils.database import Base, get_db
from app.router import api
from app.services.lifespan_service import lifespan
from app.utils.oracle_db import fetch_all, fetch_one, execute_query, test_connection

# FastAPI app
app = FastAPI(lifespan=lifespan)

app.include_router(api.router)
test_connection()

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8020, reload=True)