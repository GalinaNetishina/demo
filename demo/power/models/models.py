from datetime import datetime
from re import M
from typing import TYPE_CHECKING, Any, List

from sqlalchemy import BigInteger, ForeignKey, Index, String, select, text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base import Model, SATSMixin, SADeletedAtMixin
from .power_port_model import PowerPortModel
from .power_outlet_model import PowerOutletModel

class DeviceModelModel(Model, SATSMixin, SADeletedAtMixin):
    __tablename__ = "device_models"
   

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    type: Mapped[str]
    name: Mapped[str] = mapped_column()

    power_port_templates: Mapped[List["PowerPortTemplateModel"]] = relationship(
        back_populates="device_model"
        )

    power_outlet_templates: Mapped[List["PowerOutletTemplateModel"]] = relationship(
        back_populates="device_model"
        )

    # @property
    # def is_editable(self) -> bool:
    #     if self.tenant_id is not None:
    #         return True
    #     else:
    #         return False

    # def delete(self):
    #     self.deleted_at = datetime.utcnow()


class DeviceModel(Model, SATSMixin, SADeletedAtMixin):
    __tablename__ = "devices"
    
    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    type: Mapped[str]
    power_ports: Mapped[PowerPortModel] = relationship()
    power_outlets: Mapped[PowerOutletModel] = relationship()
