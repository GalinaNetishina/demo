from .base import ZepEnum


class PowerFeedStatusEnum(ZepEnum):
    STATUS_OFFLINE = "offline"
    STATUS_ACTIVE = "active"
    STATUS_PLANNED = "planned"
    STATUS_FAILED = "failed"


class PowerFeedTypeEnum(ZepEnum):
    TYPE_PRIMARY = "primary"
    TYPE_REDUNDANT = "redundant"


class PowerFeedSupplyEnum(ZepEnum):
    SUPPLY_AC = "ac"
    SUPPLY_DC = "dc"


class PowerFeedPhaseEnum(ZepEnum):
    PHASE_SINGLE = "single-phase"
    PHASE_3PHASE = "three-phase"
