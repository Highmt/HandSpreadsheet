from enum import Enum


class SSEnum(Enum):
    HORIZON = 0
    VERTICAL = 1


class HandEnum(Enum):
    FREE = 0
    PINCH_IN = 1
    PINCH_OUT = 2
    PALM_OPEN = 3
    GRAB = 4
    PINCH_OUT_R = 5


class ActionEnum(Enum):
    INSERT = 0
    DELETE = 1
    COPY = 2
    CUT = 3
    PASTE = 4
    SORT = 5
