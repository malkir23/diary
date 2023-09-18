from backend.settings.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, and_


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            database_url = f"postgresql+asyncpg://{settings.POSTGRESQL_INITDB_ROOT_USERNAME}:{settings.POSTGRESQL_INITDB_ROOT_PASSWORD}@postgres_db:{settings.POSTGRES_PORT}/{settings.POSTGRESQL_INITDB_DATABASE}"
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_async_engine(
                database_url, echo=True, future=True
            )
        return cls._instance

    @classmethod
    async def get(cls, base, request=None):
        async with AsyncSession(cls._instance.engine) as session:
            stmt = select(base)
            if request:
                request = and_(
                    *[getattr(base, key) == value for key, value in request.items()]
                )
                stmt = stmt.where(request)
            result = await session.execute(stmt)
            users = result.scalars().all()

            return [user.__dict__ for user in users]

    @classmethod
    async def insert(cls, base, request=None):
        async with AsyncSession(cls._instance.engine) as session:
            new_data = base(**request)

            session.add(new_data)
            await session.commit()
            await session.refresh(new_data)
            return new_data

    @classmethod
    async def update(cls, base, filters, update_fields):
        async with AsyncSession(cls._instance.engine) as session:
            stmt = (
                select(base)
                .where(*[getattr(base, column) == value for column, value in filters.items()])
            )

            users_to_update = (await session.execute(stmt)).scalars().all()

            for user in users_to_update:
                for key, value in update_fields.items():
                    setattr(user, key, value)

            await session.commit()

            return True
        return False