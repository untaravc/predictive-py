# main.py
from fastapi import FastAPI, Depends
import uvicorn
import os
from app.utils.database import Base, get_db
from app.router import api

# FastAPI app
app = FastAPI()

app.include_router(api.router)

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)