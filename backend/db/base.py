from backend.settings.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, and_
from backend.models.tasks import Category, Task


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

            items_to_update = (await session.execute(stmt)).scalars().all()

            if not items_to_update:
                return False

            for item in items_to_update:
                for key, value in update_fields.items():
                    setattr(item, key, value)

            await session.commit()
            return (
                await session.execute(
                    select(base)
                    .where(
                        *[getattr(base, column) == value for column, value in filters.items()]
                    )
                )
            ).scalars().first()

    @classmethod
    async def delete(cls, base, filters):
        async with AsyncSession(cls._instance.engine) as session:
            stmt = (
                select(base)
                .where(*[getattr(base, column) == value for column, value in filters.items()])
            )

            items_to_delete = (await session.execute(stmt)).scalars().all()

            if not items_to_delete:
                return False

            for item in items_to_delete:
                await session.delete(item)

            await session.commit()
            return True


async def init_db():
    engine = DatabaseConnection().engine
    async with engine.begin() as conn:
        for table in (Category, Task):
            await conn.run_sync(table.metadata.create_all)
