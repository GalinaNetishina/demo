from datetime import datetime
from typing import Any, Union

from fastapi import Body, Depends, Path, Query, Response
from fastapi.routing import APIRouter, APIRoute

from power.queries.power_panel_query import PowerPanelQuery
from power.queries.power_feed_query import PowerFeedQuery
from .base import Page, SAConnMan, ZepBaseModel
from power.models.power_enums import *
from database import session_maker


def get_session():
    with session_maker() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
            
# connman = SAConnMan()


# def setup_connman() -> None:
#     """
#     Establish database connection and configure connman.
#     """

#     if conf.PG_REPLICA_URL:
#         replica_urls = [conf.PG_REPLICA_URL]
#     else:
#         replica_urls = []

#     connman.connect(
#         "postgresql+psycopg2://postgres:postgres@ldb:5435/postrgres" ,
#         [],
#         # pool_size=conf.PG_POOL_SIZE,
#         # pool_max_overflow=conf.PG_POOL_MAX_OVERFLOW,
#         enable_otel=True,
#     )
    
    
class ZepAPIRoute(APIRoute):
    pass


class ZepAPIRouter(APIRouter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, route_class=ZepAPIRoute, **kwargs)


class PowerPanel(ZepBaseModel):
    id: int
    site_id: int
    location_id: int
    status: str | None
    name: str
    description: str | None

    created_at: datetime
    updated_at: datetime


class CreatePowerPanelParams(ZepBaseModel):
    site_id: int
    location_id: int
    status: str | None

    description: str | None = None
    name: str


class UpdatePowerPanelParams(ZepBaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


router = ZepAPIRouter(tags=["power"])


@router.get(
    "/panels",
)
def list_power_panels(
    session=Depends(get_session),
    # current_user: IAMUser = Depends(current_user.require_rule('alarms.read')),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(50, description="Items per page", ge=1),
    id: Union[list[str], None] = Query(None, description="Filter by id"),
    # name: Union[str, None] = Query(None, description="Filter by name"),
):
    query = (
        PowerPanelQuery()
    )

    if id:
        query = query.filter_by_id_in(id)

    # if name:
    #     query = query.filter_by_name_like(name)

    with session:
        result = query.all(session)

    return result


class PowerFeed(ZepBaseModel):
    id: int

    status: str | None
    name: str
    description: str | None
    type: PowerFeedTypeEnum
    supply: PowerFeedSupplyEnum
    phase: PowerFeedPhaseEnum

    voltage: int
    amperage: int
    max_utilization: int

    available_power: int

    created_at: datetime
    updated_at: datetime


class CreatePowerFeedParams(ZepBaseModel):
    power_panel_id: int

    status: str | None
    name: str
    description: str | None = None

    type: PowerFeedTypeEnum | None = PowerFeedTypeEnum.TYPE_PRIMARY
    supply: PowerFeedSupplyEnum | None = PowerFeedSupplyEnum.SUPPLY_AC
    phase: PowerFeedPhaseEnum | None = PowerFeedPhaseEnum.PHASE_SINGLE

    voltage: int | None = None
    amperage: int | None = None
    max_utilization: int | None = None


class UpdatePowerFeedParams(ZepBaseModel):
    status: str | None
    name: str
    description: str | None = None

    type: PowerFeedTypeEnum | None = PowerFeedTypeEnum.TYPE_PRIMARY
    supply: PowerFeedSupplyEnum | None = PowerFeedSupplyEnum.SUPPLY_AC
    phase: PowerFeedPhaseEnum | None = PowerFeedPhaseEnum.PHASE_SINGLE

    voltage: int | None = None
    amperage: int | None = None
    max_utilization: int | None = None


@router.get(
    "/power_feed",
    response_model=Page[PowerFeed],
)
def list_power_feeds(
    session=Depends(get_session),
    # current_user: IAMUser = Depends(current_user.require_rule("power-feed.manage")),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(50, description="Items per page", ge=1),
    id: Union[list[str], None] = Query(None, description="Filter by id"),
    # name: Union[str, None] = Query(None, description="Filter by name"),
):
    query = (
        PowerFeedQuery()
    )

    if id:
        query = query.filter_by_id_in(id)

    # if name:
    #     query = query.filter_by_name_like(name)

    with session:
        result = query.all(session)

    return Page.from_sa_result(PowerFeed, result)