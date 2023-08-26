from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import DatabaseConnection
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class UserBase(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    ruls = Column(String)
    password = Column(String, default=False)
    verified = Column(Boolean, default=False)
    verification_code = Column(String)



class Users:
    def __init__(self):
        self.engine = DatabaseConnection().engine

    @staticmethod
    async def find(request=None):
        return await DatabaseConnection.get(UserBase, request)

    @staticmethod
    async def find_one(request=None):
        users = await DatabaseConnection.get(UserBase, request)
        return users[0] if users else {}

    @staticmethod
    async def insert(request=None):
        return await DatabaseConnection.insert(UserBase, request)



user_db = Users()
