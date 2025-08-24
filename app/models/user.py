from app.utils.database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, nullable=True)

class UserUpdate(BaseModel):
    name: str

class UserCreate(BaseModel):
    name: str
    email: str