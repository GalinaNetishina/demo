from typing import Any
from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model, SATSMixin


class PowerPanelModel(
    Model,
    SATSMixin
):
    __tablename__ = "power_panels"
    __table_args__: tuple[Any, ...] = (
        UniqueConstraint("site_id", "name", name="unique_site_name"),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    # tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    # site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    # location_id: Mapped[int | None] = mapped_column(
    #     ForeignKey("locations.id", ondelete="SET NULL")
    # )
    site_id: Mapped[int]
    status: Mapped[str]
    name: Mapped[str]
    # name: Mapped[MultiLangString] = mapped_column(MultiLangStringType())
    description: Mapped[str | None]
    
    # tenant: Mapped["TenantModel"] = relationship()
    # site: Mapped["SiteModel"] = relationship()
    # location: Mapped["LocationModel"] = relationship()

    # @classmethod
    # def upsert_by_fixture(
    #     cls, session: Session, scalars: dict[str, Any]
    # ) -> "PowerPanelModel":
    #     query = select(PowerPanelModel).where(PowerPanelModel.name == scalars["name"])
    #     model = session.scalars(query).first()

    #     if model:
    #         for key, value in scalars.items():
    #             setattr(model, key, value)

    #         return model
    #     else:
    #         return cls(**scalars)