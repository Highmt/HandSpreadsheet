from enum import Enum


class DirectionEnum(Enum):
    HORIZON = 0
    VERTICAL = 1
    FRONT = 2
    BACK = 3
    NONE = 4


class HandEnum(Enum):
    FREE = 0
    PINCH_IN = 1
    PINCH_OUT = 2
    REVERSE = 3
    PALM = 4
    GRIP = 5



class ActionEnum(Enum):
    INSERT = 0
    DELETE = 1
    COPY = 2
    CUT = 3
    PASTE = 4
    SORT = 5
