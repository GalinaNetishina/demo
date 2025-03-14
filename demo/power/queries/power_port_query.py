from enum import StrEnum
from typing import Self


from zep.lib.models import SAQueryWithSort

from zep.ems.dcim.power.power_ports.power_port_model import PowerPortModel
from zep.ems.dcim.power.power_templates.power_port_template_model import (
    PowerPortTemplateModel,
)


class PowerPortSort(StrEnum):
    ID = "id"
    ID_DESC = "-id"


class PowerPortTemplateQuery(SAQueryWithSort[PowerPortTemplateModel, PowerPortSort]):
    def filter_by_device_model_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerPortTemplateModel.model_id == id)
        )


class PowerPortQuery(SAQueryWithSort[PowerPortModel, PowerPortSort]):
    def filter_by_id(self, id: int) -> Self:
        return self._create_child(self._sa_select.filter(PowerPortModel.id == id))

    def filter_by_tenant_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerPortModel.tenant_id == id)
        )

    def filter_by_device_model_id(self, id: int) -> Self:
        return self._create_child(self._sa_select.filter(PowerPortModel.model_id == id))
