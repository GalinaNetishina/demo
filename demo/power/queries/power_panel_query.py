from enum import Enum



from power.models.power_panel_model import PowerPanelModel
from power.queries.base import SAQueryWithSort


class PowerPanelSort(Enum):
    ID = 'id'


class PowerPanelQuery(SAQueryWithSort[PowerPanelModel, PowerPanelSort]):
    def filter_by_id(self, id: int):
        return self._create_child(self._sa_select.filter(
            PowerPanelModel.id == id)
                                  )

    def filter_by_tenant_id(self, id: int):
        return self._create_child(
            self._sa_select.filter(PowerPanelModel.tenant_id == id)
        )

    def filter_by_device_model_id(self, id: int):
        return self._create_child(
            self._sa_select.filter(PowerPanelModel.site_id == id)
        )