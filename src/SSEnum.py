from enum import Enum


class SSEnum(Enum):
    HOLIZON = 0
    VERTICAL = 1

    FREE = 0
    PINCH_IN = 1
    PINCH_OUT = 2
    PALM_OPEN = 3
    GRAB = 4
    PINCH_OUT_R = 5
