from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model, SATSMixin
from . import PowerOutletTypeEnum, PowerOutletFeedLegEnum


class PowerOutletTemplateModel(Model, SATSMixin):
    __tablename__ = "power_outlets_templates"

    id: Mapped[int] = mapped_column(
        "id", BigInteger, primary_key=True, autoincrement=True
    )
    device_model_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("device_models.id", ondelete="CASCADE")
    )
    power_port_template_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("power_ports_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column()
    label: Mapped[str | None]
    description: Mapped[str | None]

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
    power_port_template: Mapped["PowerPortTemplateModel"] = relationship()
    device_model: Mapped["DeviceModelModel"] = relationship(
        back_populates="power_outlet_templates"
    )
