from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker
from auth_data import database_url

# from aiohttp import web
# from models import db

# class PostgresAccessor:
#     def __init__(self) -> None:
#         self.db = None

#     def setup(self, application: web.Application) -> None:
#         application.on_startup.append(self._on_connect)
#         application.on_cleanup.append(self._on_disconnect)

#     async def _on_connect(self, application: web.Application):
#         self.config = application["config"]["postgres"]
#         await db.set_bind(self.config["database_url"])
#         self.db = db

#     async def _on_disconnect(self, _) -> None:
#         if self.db is not None:
#             await self.db.pop_bind().close()

engine = create_engine(database_url)

local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(local_session)
Base = declarative_base()
Base.query = session.query_property()