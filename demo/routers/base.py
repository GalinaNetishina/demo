import os
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from itertools import cycle
from typing import Any, AsyncIterator, Generic, Iterator, Protocol, Self, TypeVar
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from power.queries.base import SAQueryPaginatedResult, ZepError


class SAConnManError(ZepError):
    pass


class SAConnType(Enum):
    PRIMARY = 1
    REPLICA = 2


class SASessionFactory(Protocol):
    """
    SQLAlchemy session factory protocol. Compatible with `sqlalchemy.orm.sessionmaker`.
    """

    def __call__(self, **kwargs: Any) -> Session: ...


class SAConnManSession(Session):
    pass


class SAConnManSessionPrimary(SAConnManSession):
    pass


class SAConnManSessionReplica(SAConnManSession):
    def commit(self) -> None:
        raise SAConnManError("can't commit on replica session")


class SAConnMan:
    """
    Session lifecycle manager for SQLAlchemy.

    Instance of ``SAConnMan`` should be created once per application in a globally
    available place. On application startup, :meth:`configure` method should be called.

    Usage example:

    .. code-block:: python

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from zep.lib.connman import SAConnMan

        primary_engine = create_engine("postgresql://user:pass@master_host:port/dbname")
        primary_factory = sessionmaker(primary_engine)

        replica_engine_1 = create_engine(
            "postgresql://user:pass@standby_host_1:port/dbname"
        )
        replica_engine_2 = create_engine(
            "postgresql://user:pass@standby_host_2:port/dbname"
        )

        replica_factories = [
            sessionmaker(replica_engine_1),
            sessionmaker(replica_engine_2),
        ]

        connman = SAConnMan()
        connman.configure(primary_factory, replica_factories)

        with connman.session(connman.PRIMARY) as session:
            # SQLAlchemy session connected to primary server
            session.execute("SELECT 1").fetchone()

        with connman.session(connman.REPLICA) as session:
            # SQLAlchemy session connected to one of replica servers
            session.execute("SELECT 1").fetchone()
    """

    PRIMARY = SAConnType.PRIMARY
    REPLICA = SAConnType.REPLICA

    def __init__(self) -> None:
        self._configured = False

    def configure(
        self,
        primary_session_factory: SASessionFactory,
        replica_session_factories: list[SASessionFactory] = [],
    ) -> None:
        self._primary_session_factory = primary_session_factory
        self._replica_session_factories = cycle(replica_session_factories)
        self._replica_session_exists = bool(replica_session_factories)
        self._configured = True

    def connect(
        self,
        primary_url: str,
        replica_urls: list[str] = [],
        pool_size: int = 5,
        pool_max_overflow: int = 10,
        enable_otel: bool = False,
    ) -> None:
        engines_for_otel: list[Engine] = []

        primary_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=pool_max_overflow,
        )

        engines_for_otel.append(primary_engine)

        primary_session_factory = sessionmaker(
            primary_engine, future=True, class_=SAConnManSessionPrimary
        )

        replica_session_factories: list[SASessionFactory] = []

        for replica_url in replica_urls:
            replica_engine = create_engine(
                replica_url,
                pool_pre_ping=True,
                pool_size=pool_size,
                max_overflow=pool_max_overflow,
            )

            engines_for_otel.append(replica_engine)

            replica_session_factories.append(
                sessionmaker(
                    replica_engine, future=True, class_=SAConnManSessionReplica
                )
            )

        if enable_otel:
            self.setup_otel_instrumentation(engines=engines_for_otel)

        self.configure(primary_session_factory, replica_session_factories)

    # def setup_otel_instrumentation(self, engines: list[Engine]) -> None:
    #     from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    #     otel_instrumentor = SQLAlchemyInstrumentor()
    #     otel_instrumentor.instrument(engines=engines)

    @contextmanager
    def session(
        self, type: SAConnType, *, expire_on_commit: bool = True, **kwargs: Any
    ) -> Iterator[Session]:
        session_factory = self._get_session_factory(type)

        session = session_factory(expire_on_commit=expire_on_commit, **kwargs)

        try:
            yield session
        finally:
            session.close()

    def _get_session_factory(self, type: SAConnType) -> SASessionFactory:
        if not self._configured:
            raise SAConnManError("connman is not configured")

        if type not in [SAConnType.PRIMARY, SAConnType.REPLICA]:
            raise SAConnManError("unknown session type: %s" % repr(type))

        if type == SAConnType.PRIMARY or not self._replica_session_exists:
            return self._primary_session_factory
        else:
            return next(self._replica_session_factories)


class SASessionAIOFactory(Protocol):
    """
    SQLAlchemy async session factory protocol. Compatible with
    `sqlalchemy.ext.asyncio.async_sessionmaker`.
    """

    def __call__(self, **kwargs: Any) -> AsyncSession: ...


class SAConnManSessionAIO(AsyncSession):
    pass


class SAConnManSessionAIOPrimary(SAConnManSessionAIO):
    pass


class SAConnManSessionAIOReplica(SAConnManSessionAIO):
    async def commit(self) -> None:
        raise SAConnManError("can't commit on replica session")


class SAConnManAIO:
    PRIMARY = SAConnType.PRIMARY
    REPLICA = SAConnType.REPLICA

    def __init__(self) -> None:
        self._configured = False

    def configure(
        self,
        primary_session_factory: SASessionAIOFactory,
        replica_session_factories: list[SASessionAIOFactory] = [],
    ) -> None:
        self._primary_session_factory = primary_session_factory
        self._replica_session_factories = cycle(replica_session_factories)
        self._replica_session_exists = bool(replica_session_factories)
        self._configured = True

    def connect(
        self,
        primary_url: str,
        replica_urls: list[str] = [],
        pool_size: int = 5,
        pool_max_overflow: int = 10,
    ) -> None:
        primary_engine = create_async_engine(
            primary_url,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=pool_max_overflow,
        )

        primary_session_factory = async_sessionmaker(
            primary_engine, class_=SAConnManSessionAIOPrimary
        )

        replica_session_factories: list[SASessionAIOFactory] = []

        for replica_url in replica_urls:
            replica_engine = create_async_engine(
                replica_url,
                pool_pre_ping=True,
                pool_size=pool_size,
                max_overflow=pool_max_overflow,
            )

            replica_session_factories.append(
                async_sessionmaker(replica_engine, class_=SAConnManSessionAIOReplica)
            )

        self.configure(primary_session_factory, replica_session_factories)

    @asynccontextmanager
    async def session(
        self, type: SAConnType, *, expire_on_commit: bool = True, **kwargs: Any
    ) -> AsyncIterator[AsyncSession]:
        session_factory = self._get_session_factory(type)

        session = session_factory(expire_on_commit=expire_on_commit, **kwargs)

        try:
            yield session
        finally:
            await session.close()

    def _get_session_factory(self, type: SAConnType) -> SASessionAIOFactory:
        if not self._configured:
            raise SAConnManError("connman is not configured")

        if type not in [SAConnType.PRIMARY, SAConnType.REPLICA]:
            raise SAConnManError("unknown session type: %s" % repr(type))

        if type == SAConnType.PRIMARY or not self._replica_session_exists:
            return self._primary_session_factory
        else:
            return next(self._replica_session_factories)


def rebuild_postgres_url(
    url: str,
    host_override: str | None = None,
    port_override: int | None = None,
    database_override: str | None = None,
    user_override: str | None = None,
    password_override: str | None = None,
    driver_override: str | None = None,
) -> str:
    """
    Build database URL for SQLAlchemy. See `documentation`_ for details.

    .. _documentation: https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
    """

    url_parts = urlparse(url)

    if url_parts.scheme != "postgresql":
        raise ZepError("unsupported url scheme: {url_parts.scheme}")

    if driver_override:
        url_parts = url_parts._replace(scheme=driver_override)

    hostname = host_override or url_parts.hostname or "localhost"
    port = port_override or url_parts.port or 5432
    username = user_override or url_parts.username or os.getlogin()
    password = password_override or url_parts.password

    if password:
        netloc = f"{username}:{password}@{hostname}:{port}"
    else:
        netloc = f"{username}@{hostname}:{port}"

    url_parts = url_parts._replace(netloc=netloc)

    if database_override:
        url_parts = url_parts._replace(path=database_override)

    return url_parts.geturl()


class ZepBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_sa_model(cls, model: Any, exclude: list[str] = []) -> Self:
        model_dict = {}
        for name, field in cls.model_fields.items():
            if name not in exclude:
                if field.alias:
                    model_dict[name] = getattr(model, field.alias)
                else:
                    model_dict[name] = getattr(model, name)

        return cls.model_construct(**model_dict)


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int

    @classmethod
    def from_sa_result(cls, result: SAQueryPaginatedResult[Any]) -> "PaginationMeta":
        return PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_count=result.total_count,
            total_pages=result.total_pages,
        )


_PageItemModel = TypeVar("_PageItemModel", bound="BaseModel")

_TreeItemModel = TypeVar("_TreeItemModel", bound="BaseModel")


class Tree(BaseModel, Generic[_TreeItemModel]):
    items: list[_TreeItemModel]


class Page(BaseModel, Generic[_PageItemModel]):
    items: list[_PageItemModel]
    meta: PaginationMeta

    @classmethod
    def from_sa_result(
        cls,
        model_class: type[_PageItemModel],
        result: SAQueryPaginatedResult[Any],
        context: dict = {},
    ) -> "Page[_PageItemModel]":
        return Page(
            items=[
                model_class.model_validate(
                    item,
                    context={
                        **context,
                        "sa_item": item,
                    },
                )
                for item in result
            ],
            meta=PaginationMeta.from_sa_result(result),
        )


from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, validation_info=None):
        if not (
            value
            and (isinstance(value, ObjectId) or isinstance(value, str))
            and ObjectId().is_valid(value)
        ):
            raise ValueError("Not a valid ObjectId")

        return str(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        new_field_schema = {"type": "string", "examples": ["66488b368a6801e71d70dfe9"]}
        return new_field_schema