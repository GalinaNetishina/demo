from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .cable_model import CabledObjectMixin, CabledPathEndpoint
from .base import Model, SATSMixin
from . import PowerPortTypeEnum



class PowerPortModel(SATSMixin, CabledObjectMixin, CabledPathEndpoint, Model):
    __tablename__ = "power_ports"
    __table_args__ = (
        CheckConstraint("max_draw >= allocated_draw", name="allocated_draw_check"),
        CheckConstraint("max_draw >= 0", name="max_draw_positive_check"),
        CheckConstraint("allocated_draw >= 0", name="allocated_draw_positive_check"),
    
    )
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column()
    device_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("devices.id", ondelete="CASCADE")
    )

    name: Mapped[str] = mapped_column()
    label: Mapped[str | None]
    description: Mapped[str | None]
    max_draw: Mapped[int | None]
    allocated_draw: Mapped[int | None]

    type: Mapped[PowerPortTypeEnum] = mapped_column(
        Enum(
            PowerPortTypeEnum,
            name="power_ports_types",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        nullable=True,
    )
    device: Mapped["DeviceModel"] = relationship()
