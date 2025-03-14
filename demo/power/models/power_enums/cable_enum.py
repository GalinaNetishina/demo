from .base import ZepEnum


class TerminationTypeEnum(ZepEnum):
    POWER_FEED = "power_feed"
    POWER_PORT = "power_port"
    POWER_OUTLET = "power_outlet"
    

class CableLengthUnitEnum(ZepEnum):
    # Metric
    UNIT_KILOMETER = "km"
    UNIT_METER = "m"
    UNIT_CENTIMETER = "cm"

    # Imperial
    UNIT_MILE = "mi"
    UNIT_FOOT = "ft"
    UNIT_INCH = "in"


class CableEndEnum(ZepEnum):
    SIDE_A = "A"
    SIDE_B = "B"


class LinkStatusEnum(ZepEnum):
    STATUS_CONNECTED = "connected"
    STATUS_PLANNED = "planned"
    STATUS_DECOMMISSIONING = "decommissioning"


class CableTypeEnum(ZepEnum):
    TYPE_CAT3 = "cat3"
    TYPE_CAT5 = "cat5"
    TYPE_CAT5E = "cat5e"
    TYPE_CAT6 = "cat6"
    TYPE_CAT6A = "cat6a"
    TYPE_CAT7 = "cat7"
    TYPE_CAT7A = "cat7a"
    TYPE_CAT8 = "cat8"
    TYPE_DAC_ACTIVE = "dac-active"
    TYPE_DAC_PASSIVE = "dac-passive"
    TYPE_MRJ21_TRUNK = "mrj21-trunk"
    TYPE_COAXIAL = "coaxial"
    TYPE_MMF = "mmf"
    TYPE_MMF_OM1 = "mmf-om1"
    TYPE_MMF_OM2 = "mmf-om2"
    TYPE_MMF_OM3 = "mmf-om3"
    TYPE_MMF_OM4 = "mmf-om4"
    TYPE_MMF_OM5 = "mmf-om5"
    TYPE_SMF = "smf"
    TYPE_SMF_OS1 = "smf-os1"
    TYPE_SMF_OS2 = "smf-os2"
    TYPE_AOC = "aoc"
    TYPE_POWER = "power"
    TYPE_USB = "usb"
