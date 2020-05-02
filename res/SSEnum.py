from enum import Enum


class DirectionEnum(Enum):
    HORIZON = 0
    VERTICAL = 1
    FRONT = 2
    BACK = 3


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

class TestSectionEnum(Enum):
    INSERT = 0
    DELETE = 1
    CUT_COPY_PASTE = 2
    SORT = 3


class TestModeEnum(Enum):
    GESTURE = 0
    SHORTCUT_KEY = 1
    MENU = 2