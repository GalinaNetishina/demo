from typing import Any
from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .cable_model import CabledObjectMixin, CabledPathEndpoint
from .base import Model, SATSMixin
from .power_enums import (
    PowerFeedPhaseEnum,
    PowerFeedStatusEnum,
    PowerFeedSupplyEnum,
    PowerFeedTypeEnum
    )


class PowerFeedModel(
    SATSMixin,
    CabledObjectMixin,
    CabledPathEndpoint
    # TaggableModel,
    # ContactsModelMixin,
    # EntryModelMixin,
):
    __tablename__ = "powerfeeds"
    __table_args__: tuple[Any, ...] = (
        UniqueConstraint(
            "power_panel_id", "name", name="unique_power_panel_name"
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    tenant_id: Mapped[str]
    # tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    power_panel_id: Mapped[int] = mapped_column(ForeignKey("power_panels.id", ondelete="CASCADE"))
    # site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    # location_id: Mapped[int | None] = mapped_column(
    #     ForeignKey("locations.id", ondelete="SET NULL")
    # )
    name: Mapped[str]
    # name: Mapped[MultiLangString] = mapped_column(MultiLangStringType())
    description: Mapped[str | None]
    
    status: Mapped[PowerFeedStatusEnum] = mapped_column(
        Enum(
            PowerFeedStatusEnum,
            name="power_feed_statuses",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
        default=PowerFeedStatusEnum.STATUS_ACTIVE
    )
    type: Mapped[PowerFeedTypeEnum] = mapped_column(
        Enum(
            PowerFeedTypeEnum,
            name="power_feed_types",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
        default=PowerFeedTypeEnum.TYPE_PRIMARY
    )
    supply: Mapped[PowerFeedSupplyEnum] = mapped_column(
        Enum(
            PowerFeedSupplyEnum,
            name="power_feed_supplies",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
        default=PowerFeedSupplyEnum.SUPPLY_AC
    )
    phase: Mapped[PowerFeedPhaseEnum] = mapped_column(
        Enum(
            PowerFeedPhaseEnum,
            name="power_feed_phases",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
        default=PowerFeedPhaseEnum.PHASE_SINGLE
    )
    # default values from config?
    voltage: Mapped[int] = mapped_column()
    amperage: Mapped[int]
    max_utilization: Mapped[int]
    
    available_power: Mapped[int] = mapped_column(Integer, default=0)
    
    def set_available_power(self):
        kva = abs(self.voltage) * self.amperage * (self.max_utilization / 100)
        if self.phase == PowerFeedPhaseEnum.PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)
    

    # tenant: Mapped["TenantModel"] = relationship()
    # site: Mapped["SiteModel"] = relationship()
    # location: Mapped["LocationModel"] = relationship()
    # rack: Mapped["RackModel"] = relationship()

    # @classmethod
    # def upsert_by_fixture(
    #     cls, session: Session, scalars: dict[str, Any]
    # ) -> "PowerFeedModel":
    #     query = select(PowerFeedModel).where(PowerFeedModel.name == scalars["name"])
    #     model = session.scalars(query).first()

    #     if model:
    #         for key, value in scalars.items():
    #             setattr(model, key, value)

    #         return model
    #     else:
    #         return cls(**scalars)