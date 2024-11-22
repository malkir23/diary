from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.base import DatabaseConnection
from backend.models.tasks import Task, Category

class Tasks:
    def __init__(self):
        self.engine = DatabaseConnection().engine

    @staticmethod
    async def find(request=None):
        return await DatabaseConnection.get(Task, request)

    @staticmethod
    async def insert(request=None):
        return await DatabaseConnection.insert(Task, request)

    @staticmethod
    async def update(filters, update_fields):
        return await DatabaseConnection.update(Task, filters, update_fields)
    @classmethod
    async def delete(cls, filters=None):
        return await DatabaseConnection.get(Task, filters)


class Categorys:
    def __init__(self):
        self.engine = DatabaseConnection().engine

    @staticmethod
    async def find(request=None):
        return await DatabaseConnection.get(Category, request)

    @staticmethod
    async def insert(request=None):
        return await DatabaseConnection.insert(Category, request)

    @staticmethod
    async def update(filters, update_fields):
        return await DatabaseConnection.update(Category, filters, update_fields)
    @classmethod
    async def delete(cls, filters=None):
        return await DatabaseConnection.get(Category, filters)

TASKS = Tasks()
CATEGORYS = Categorys()
