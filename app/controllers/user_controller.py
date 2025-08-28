from app.models.user import User, UserUpdate, UserCreate
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from app.main import get_db

async def create_user(name: str, email: str, db: AsyncSession = Depends(get_db)):
    query = text("INSERT INTO users (name, email) VALUES (:name, :email) RETURNING id, name, email")
    result = await db.execute(query, {"name": name, "email": email})
    await db.commit()
    return result.mappings().first()

# READ (list + pagination)
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = text("SELECT id, name FROM users ORDER BY id OFFSET :skip LIMIT :limit")
    result = await db.execute(query, {"skip": skip, "limit": limit})
    return result.mappings().all()

# READ (single user by ID)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT id, name, email FROM users WHERE id = :id")
    result = await db.execute(query, {"id": user_id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row

# UPDATE
async def update_user(user_id: int, name: Optional[str], email: Optional[str], db: AsyncSession = Depends(get_db)):
    query = text("""
        UPDATE users
        SET name = COALESCE(:name, name),
            email = COALESCE(:email, email)
        WHERE id = :id
        RETURNING id, name, email
    """)
    result = await db.execute(query, {"id": user_id, "name": name, "email": email})
    await db.commit()
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row

# DELETE
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    query = text("DELETE FROM users WHERE id = :id RETURNING id")
    result = await db.execute(query, {"id": user_id})
    await db.commit()
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted_id": row["id"]}