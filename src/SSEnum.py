from enum import Enum


class SSEnum(Enum):
    HOLIZON = 0
    VERTICAL = 1

    FREE_STATE = 0
    PINCH_IN = 1
    PINCH_OUT = 2
    PALM_OPEN = 3
    GRAB = 4
