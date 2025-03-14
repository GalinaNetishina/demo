from typing import TYPE_CHECKING, Any, TypeVar

from goodboy import Error, Int, Str
from goodboy_sqlalchemy import Column

from zep.ems.dcim.device_models.device_models_service import DeviceModelService
from zep.ems.dcim.power import PowerPortModel, PowerPortTemplateModel, PowerPortTypeEnum
from zep.ems.tenants import TenantQuery
from zep.lib.goodboy import Mapped, MultiLangSchema
from zep.lib.models import SAService
from zep.lib.models.sa_signals import created, updated

if TYPE_CHECKING:
    from zep.ems.dcim.device_models.device_models_model import DeviceModelModel

SAServiceModel = TypeVar("SAServiceModel")


def tenant_id_rule(
    self, value: str, typecast: bool, context: dict[Any, Any]
) -> tuple[Any, list[Error]]:
    if value:
        try:
            TenantQuery().filter_active().filter_by_id(value).one(context["session"])
        except TenantQuery.NotFoundError:
            return value, [self._error("not_found")]

    return value, []


def device_model_id_rule(
    self, value: int, typecast: bool, context: dict[Any, Any]
) -> tuple[Any, list[Error]]:
    from zep.ems.dcim.device_models import DeviceModelQuery

    if value:
        try:
            DeviceModelQuery().filter_active().filter_by_id(value).one(
                context["session"]
            )
        except DeviceModelQuery.NotFoundError:
            return value, [self._error("not_found")]

    return value, []


def device_id_rule(
    self, value: int, typecast: bool, context: dict[Any, Any]
) -> tuple[Any, list[Error]]:
    from zep.ems.dcim.devices import DeviceQuery

    if value:
        try:
            DeviceQuery().filter_active().filter_by_id(value).one(context["session"])
        except DeviceQuery.NotFoundError:
            return value, [self._error("not_found")]

    return value, []


# ? validate if self.power_port :
# self.power_port.device_model == self.device.device_model


class PowerPortService(SAService[PowerPortModel]):
    def schema(self) -> Mapped:
        return Mapped(
            PowerPortModel,
            column_names=[
                "label",
                "description",
                "cable_id",
                "cable_end",
                "mark_connected",
            ],
            keys=[
                Column("name", MultiLangSchema()),
                Column("id", Int(), unique=True),
                Column("tenant_id", Str(rules=[tenant_id_rule], allow_none=True)),
                Column("device_id", Int(rules=[device_id_rule], allow_none=False)),
                Column("max_draw", Int(greater_or_equal_to=0), required=False),
                Column("allocated_draw", Int(greater_or_equal_to=0), required=False),
                Column(
                    "type",
                    Str(allow_none=True, allowed=PowerPortTypeEnum.list()),
                    required=False,
                ),
            ],
        )


class PowerPortTemplateService(SAService[PowerPortTemplateModel]):
    def schema(self) -> Mapped:
        return Mapped(
            PowerPortTemplateModel,
            column_names=["label", "description"],
            keys=[
                Column("name", MultiLangSchema()),
                Column("id", Int(), unique=True),
                Column(
                    "device_model_id",
                    Int(rules=[device_model_id_rule], allow_none=False),
                ),
                Column(
                    "type",
                    Str(allowed=PowerPortTypeEnum.list(), allow_none=True),
                    required=False,
                ),
                Column("max_draw", Int(greater_or_equal_to=0), required=False),
                Column("allocated_draw", Int(greater_or_equal_to=0), required=False),
            ],
        )


def create_power_port_templates(
    sender: SAService,
    instance: 'DeviceModelModel',
    context: dict[str, Any]
    ) -> None:
    port_templates = instance.power_outlet_templates
    service = PowerPortTemplateService(sender.session)
    for port in port_templates:
        service.create(**port)
    sender.session.commit()


def update_power_port_templates(
    sender: SAService,
    instance: 'DeviceModelModel',
    context: dict[str, Any]
    ) -> None:
    port_templates = instance.power_outlet_templates
    service = PowerPortTemplateService(sender.session)
    for port in port_templates:
        service.update(**{k: v for k, v in port.items() if v}, device_model_id=instance.id)
    sender.session.commit()


created.connect(create_power_port_templates, sender=DeviceModelService)
updated.connect(create_power_port_templates, sender=DeviceModelService)
