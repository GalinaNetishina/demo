from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Model, SATSMixin
from .cable_model import CabledObjectMixin, CabledPathEndpoint
from . import PowerOutletTypeEnum, PowerOutletFeedLegEnum


class PowerOutletModel(SATSMixin, CabledObjectMixin, CabledPathEndpoint, Model):
    __tablename__ = "power_outlets"

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    tenant_id: Mapped[str] = mapped_column()
    device_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("devices.id", ondelete="CASCADE")
    )
    power_port_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("power_ports.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column()
    label: Mapped[str | None]
    description: Mapped[str | None]
    color: Mapped[str] = mapped_column(default="000000", server_default="000000")

    type: Mapped[PowerOutletTypeEnum] = mapped_column(
        Enum(
            PowerOutletTypeEnum,
            name="power_outlets_types",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
    )
    feed_leg: Mapped[PowerOutletFeedLegEnum] = mapped_column(
        Enum(
            PowerOutletFeedLegEnum,
            name="power_outlets_feed_legs",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
    )
    power_port: Mapped["PowerPortModel"] = relationship()
    device: Mapped["DeviceModel"] = relationship()
