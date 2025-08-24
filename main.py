# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import uvicorn
from typing import List
import os
from app.utils.database import Base, get_db
from app.models.user import User
from app.router import api


# FastAPI app
app = FastAPI()

app.include_router(api.router)
    

@app.get("/users/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == item_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}

# @app.put("/users/{item_id}", response_model=dict)
# def update_item(item_id: int, name: str, description: str = None, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == item_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user.name = name
#     user.description = description
#     db.commit()
#     db.refresh(user)
#     return {"id": user.id, "name": user.name, "description": user.description}

# @app.delete("/users/{item_id}", response_model=dict)
# def delete_item(item_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == item_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": f"User {item_id} deleted successfully"}

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)