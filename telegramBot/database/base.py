from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from  settings import Settings


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/asyncalchemy"
DATABASE_URL = f"postgresql+asyncpg://" + DATABASE_URL


def create_session(self):
# echo view in log sql requests
engine = create_async_engine(Settings.get_db_url(), echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()
async with async_session() as session:
    async with session.begin():
        return session




async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)

# local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = scoped_session(local_session)
# Base = declarative_base()
# Base.query = session.query_property()