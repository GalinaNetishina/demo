import math
from abc import abstractmethod
from datetime import datetime
from enum import StrEnum
from secrets import token_hex
from typing import Any, ClassVar, Generic, Iterator, Self, Sequence, Type, TypeVar
from typing import get_args as get_typing_args

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, Session


class ZepError(Exception):
    """
    Base class for application exceptions.
    """

    def __init__(self, message: str):
        self.id = self.generate_code()
        self.message = message

        super().__init__("%s: %s" % (self.id, message))

    @staticmethod
    def generate_code() -> str:
        time = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        rand = token_hex(5)

        return "E%s-%s" % (time, rand)


class NotFoundError(ZepError):
    query_class: ClassVar[type]

    def __init__(self) -> None:
        super().__init__(f"no results found for {self.query_class.__qualname__}")


class MultipleResultsFoundError(ZepError):
    query_class: ClassVar[type]

    def __init__(self) -> None:
        super().__init__(f"multiple results found for {self.query_class.__qualname__}")


SAQueryModel = TypeVar("SAQueryModel")
SAQueryException = TypeVar("SAQueryException")


class SAQueryResult(Generic[SAQueryModel]):
    def __init__(self, records: Sequence[SAQueryModel]) -> None:
        self._records = records

    def __iter__(self) -> Iterator[SAQueryModel]:
        return iter(self._records)

    def __getitem__(self, item: int) -> SAQueryModel:
        return self._records[item]

    def __len__(self) -> int:
        return len(self._records)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self._records == other._records

        return super().__eq__(other)


class SAQueryPaginatedResult(SAQueryResult[SAQueryModel]):
    def __init__(
        self,
        records: Sequence[SAQueryModel],
        page: int,
        page_size: int,
        total_count: int,
    ):
        super().__init__(records)

        self.page = page
        self.page_size = page_size
        self.total_count = total_count

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total_count / self.page_size)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._records == other._records
                and self.page == other.page
                and self.page_size == other.page_size
                and self.total_count == other.total_count
            )

        return super().__eq__(other)


class SAQueryBase(Generic[SAQueryModel]):
    NotFoundError: Type[Exception] = NotFoundError
    MultipleResultsFoundError: Type[Exception] = MultipleResultsFoundError

    def __init__(
        self,
        sa_select: Select[tuple[SAQueryModel]] | None = None,
    ):
        if sa_select is None:
            sa_select = self._get_initial_sa_select()

        self._sa_select = sa_select

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls.NotFoundError = cls._create_exception_class(
            "NotFoundError", cls.NotFoundError, cls.__module__
        )
        cls.MultipleResultsFoundError = cls._create_exception_class(
            "MultipleResultsFoundError", cls.MultipleResultsFoundError, cls.__module__
        )

    def _create_child(self, sa_select: Select[tuple[SAQueryModel]]) -> Self:
        return self.__class__(sa_select)

    def _get_initial_sa_select(self) -> Select[tuple[SAQueryModel]]:
        model_class = self.get_model_class()
        return select(model_class).select_from(model_class)

    @property
    def sa_select(self) -> Select[tuple[SAQueryModel]]:
        return self._sa_select

    @classmethod
    def get_model_class(cls) -> Type[SAQueryModel]:
        generic_base = cls.__orig_bases__[0]  # type: ignore
        return get_typing_args(generic_base)[0]  # type: ignore

    @classmethod
    def _create_exception_class(
        cls,
        name: str,
        base: Type[SAQueryException],
        module: str,
    ) -> Type[SAQueryException]:
        attrs = {
            "query_class": cls,
            "__module__": module,
            "__qualname__": f"{cls.__qualname__}.{name}",
        }

        return type(name, (base,), attrs)


class SAQueryError(ZepError):
    pass


class SAQuery(SAQueryBase[SAQueryModel]):
    def all(self, session: Session) -> SAQueryResult[SAQueryModel]:
        return SAQueryResult(session.scalars(self._sa_select).all())

    def paginate(
        self, session: Session, page: int, page_size: int = 50
    ) -> SAQueryPaginatedResult[SAQueryModel]:
        if page <= 0:
            raise SAQueryError("page can't be less or equal zero")

        if page_size <= 0:
            raise SAQueryError("page_size can't be less or equal zero")

        sa_select = self._sa_select.limit(page_size).offset((page - 1) * page_size)

        records = session.scalars(sa_select).all()
        total_count = self.count(session)

        return SAQueryPaginatedResult(records, page, page_size, total_count)

    def first(self, session: Session) -> SAQueryModel | None:
        return session.scalars(self._sa_select.limit(1)).first()

    def one(self, session: Session) -> SAQueryModel:
        try:
            return session.scalars(self._sa_select.limit(2)).one()
        except NoResultFound:
            raise self.NotFoundError()
        except MultipleResultsFound:
            raise self.MultipleResultsFoundError()

    def first_or_error(self, session: Session) -> SAQueryModel:
        instance = session.scalars(self._sa_select.limit(1)).first()

        if not instance:
            raise self.NotFoundError()

        return instance

    def count(self, session: Session) -> int:
        sa_select_count = self._sa_select.with_only_columns(func.count())
        return session.scalars(sa_select_count).one()


SAQuerySortEnum = TypeVar("SAQuerySortEnum", bound=[StrEnum])


class SAQueryWithSort(
    SAQuery[SAQueryModel],
    Generic[SAQueryModel, SAQuerySortEnum]
    ):
    def all_sorted(
        self, session: Session, sort: list[SAQuerySortEnum] = []
    ) -> SAQueryResult[SAQueryModel]:
        query = self

        for sort_value in sort:
            query = query.sort(sort_value)

        return SAQueryResult(session.scalars(self._sa_select).all())

    def paginate_sorted(
        self,
        session: Session,
        page: int,
        page_size: int = 50,
        sort: list[SAQuerySortEnum] = [],
    ) -> SAQueryPaginatedResult[SAQueryModel]:
        if page <= 0:
            raise SAQueryError("page can't be less or equal zero")

        if page_size <= 0:
            raise SAQueryError("page_size can't be less or equal zero")

        query = self

        for sort_value in sort:
            query = query.sort(sort_value)

        sa_select = query._sa_select.limit(page_size).offset((page - 1) * page_size)

        records = session.scalars(sa_select).all()
        total_count = self.count(session)
        return SAQueryPaginatedResult(records, page, page_size, total_count)

    def sort(self, sort: SAQuerySortEnum) -> Self:
        model_class = self.get_model_class()

        if sort.startswith("-"):
            column_name = sort[1:]
            order_func = desc
        else:
            column_name = sort
            order_func = asc

        column = getattr(model_class, column_name, None)

        if isinstance(column, InstrumentedAttribute):
            return self._create_child(self._sa_select.order_by(order_func(column)))
        else:
            raise ZepError(
                f"couldn't find column for sort value {sort} in model {model_class}, "
                f"please override sort method in class {self.__class__} and explicitly "
                f"define sorting expression"
            )


class SAQueryAIO(SAQueryBase[SAQueryModel]):
    async def all(self, session: AsyncSession) -> SAQueryResult[SAQueryModel]:
        return SAQueryResult((await session.scalars(self._sa_select)).all())

    async def paginate(
        self, session: AsyncSession, page: int, page_size: int = 50
    ) -> SAQueryPaginatedResult[SAQueryModel]:
        if page <= 0:
            raise SAQueryError("page can't be less or equal zero")

        if page_size <= 0:
            raise SAQueryError("page_size can't be less or equal zero")

        sa_select = self._sa_select.limit(page_size).offset((page - 1) * page_size)
        sa_select_count = self._sa_select.with_only_columns(func.count())

        records = (await session.scalars(sa_select)).all()
        total_count = (await session.scalars(sa_select_count)).one()

        return SAQueryPaginatedResult(records, page, page_size, total_count)

    async def first(self, session: AsyncSession) -> SAQueryModel | None:
        return (await session.scalars(self._sa_select.limit(1))).first()

    async def one(self, session: AsyncSession) -> SAQueryModel:
        try:
            return (await session.scalars(self._sa_select.limit(2))).one()
        except NoResultFound:
            raise self.NotFoundError()
        except MultipleResultsFound:
            raise self.MultipleResultsFoundError()

    async def first_or_error(self, session: AsyncSession) -> SAQueryModel:
        instance = (await session.scalars(self._sa_select.limit(1))).first()

        if not instance:
            raise self.NotFoundError()

        return instance
