from enum import StrEnum
from typing import Self


from zep.lib.models import SAQueryWithSort

from zep.ems.dcim.power.power_outlets.power_outlet_model import PowerOutletModel
from zep.ems.dcim.power.power_templates.power_outlet_template_model import (
    PowerOutletTemplateModel,
)


class PowerOutletSort(StrEnum):
    ID = "id"
    ID_DESC = "-id"


class PowerOutletTemplateQuery(
    SAQueryWithSort[PowerOutletTemplateModel, PowerOutletSort]
):
    def filter_by_device_model_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerOutletTemplateModel.device_model_id == id)
        )


class PowerOutletQuery(SAQueryWithSort[PowerOutletModel, PowerOutletSort]):
    def filter_by_id(self, id: int) -> Self:
        return self._create_child(self._sa_select.filter(PowerOutletModel.id == id))

    def filter_by_tenant_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerOutletModel.tenant_id == id)
        )

    def filter_by_device_model_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerOutletModel.device_model_id == id)
        )
