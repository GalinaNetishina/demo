
from enum import Enum
from typing import Self
from power.models.power_feed_model import PowerFeedModel
from power.queries.base import SAQueryWithSort


class PowerFeedSort(Enum):
    ID = 'id'


class PowerFeedQuery(SAQueryWithSort[PowerFeedModel, PowerFeedSort]):
    def filter_by_id(self, id: int) -> Self:
        return self._create_child(self._sa_select.filter(PowerFeedModel.id == id))

    def filter_by_tenant_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerFeedModel.tenant_id == id)
        )

    def filter_by_device_model_id(self, id: int) -> Self:
        return self._create_child(
            self._sa_select.filter(PowerFeedModel.power_panel_id == id)
        )
        