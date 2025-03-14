from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


engine = create_engine(
    url=settings.DSN_postgresql_psycopg, pool_size=50, max_overflow=100
)
session_maker = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)





# from typing import Protocol
# class ReadRepo(Protocol):
#     @classmethod
#     async def get_one(cls, session, id: int):
#         ...
#     @classmethod
#     async def get_many(cls, session, *args, **kwargs):
#         ...

# class WriteRepo(Protocol):
#     @classmethod
#     async def add_one(cls, session, id: int):
#         ...
#     @classmethod
#     async def add_many(cls, session, *args, **kwargs):
#         ...
