from typing import TYPE_CHECKING, Any

from goodboy import Error, Int, Str
from goodboy_sqlalchemy import Column

from zep.ems.dcim.device_models.device_models_model import DeviceModelModel
from zep.ems.dcim.device_models.device_models_service import DeviceModelService
from zep.ems.dcim.power import (
    PowerOutletFeedLegEnum,
    PowerOutletModel,
    PowerOutletTypeEnum,
)
from zep.ems.dcim.power.power_templates.power_outlet_template_model import (
    PowerOutletTemplateModel,
)




def tenant_id_rule(
    self, value: int, typecast: bool, context: dict[Any, Any]
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


# ? validate if self.power_port :
# self.power_port.device_model == self.device.device_model


class PowerOutletService(SAService[PowerOutletModel]):
    def schema(self) -> Mapped:
        return Mapped(
            PowerOutletModel,
            column_names=[
                "name",
                "label",
                "description",
                "cable_id",
                "cable_end",
                "mark_connected",
            ],
            keys=[
                Column("id", Int(), unique=True),
                Column("tenant_id", Str(rules=[tenant_id_rule], allow_none=True)),
                # Column("cable_id", Str(rules=[cable_id_rule], allow_none=True)),
                Column(
                    "feed_leg",
                    Str(allowed=PowerOutletFeedLegEnum.list(), allow_none=True),
                    required=False,
                ),
                Column(
                    "type",
                    Str(allow_none=True, allowed=PowerOutletTypeEnum.list()),
                    required=False,
                ),
            ],
        )


class PowerOutletTemplateService(SAService[PowerOutletTemplateModel]):
    def schema(self) -> Mapped:
        return Mapped(
            PowerOutletTemplateModel,
            column_names=[
                "name",
                "label",
                "description",
            ],
            keys=[
                # Column("name", MultiLangSchema()),
                Column("id", Int(), unique=True),
                Column(
                    "device_model_id",
                    Int(rules=[device_model_id_rule], allow_none=False),
                ),
                Column(
                    "type",
                    Str(allowed=PowerOutletTypeEnum.list(), allow_none=True),
                    required=False,
                ),
                Column(
                    "feed_leg",
                    Str(allowed=PowerOutletFeedLegEnum.list(), allow_none=True),
                    required=False,
                ),
            ],
        )


# def create_power_outlet_templates(
#     sender: SAService,
#     instance: 'DeviceModelModel',
#     context: dict[str, Any]
#     ) -> None:
#     outlet_templates = instance.power_outlet_templates
#     service = PowerOutletTemplateService(sender.session)
#     for outlet in outlet_templates:
#         service.create(**outlet)
#     sender.session.commit()


# def update_power_outlet_templates(
#     sender: SAService,
#     instance: "DeviceModelModel",
#     context: dict[str, Any]
#     ) -> None:
#     outlet_templates = instance.power_outlet_templates
#     service = PowerOutletTemplateService(sender.session)
#     for outlet in outlet_templates:
#         service.update({k: v for k, v in outlet.items() if v})
#     sender.session.commit()


# created.connect(create_power_outlet_templates, sender=DeviceModelService)
# updated.connect(create_power_outlet_templates, sender=DeviceModelService)
