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
    OPEN = 4
    GRIP = 5
    NAME_LIST = ["FREE", "PINCH_IN", "PINCH_OUT", "REVERSE", "OPEN", "GRIP"]

class OperationEnum(Enum):
    Ir = 0
    Id = 1
    Dl = 2
    Du = 3
    Copy = 4
    Cut = 5
    Paste = 6
    Sa = 7
    Sd = 8
    OperationName_LIST = ["Ir", "Id", "Dl", "Du", "Copy", "Cut", "Paste", "Sa", "Sd"]
    OperationName_LIST_JP = ["列の挿入", "行の挿入", "烈の削除", "行の削除", "コピー", "カット", "ペースト", "昇順ソート", "降順ソート"]



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

class FeatureEnum(Enum):
    COLLECT_LIST = [
        "x",
        "y",
        "z",
        "pitch",
        "roll",
        "yaw",
        "Thumb_pos_x",
        "Thumb_pos_y",
        "Thumb_pos_z",
        "Index_pos_x",
        "Index_pos_y",
        "Index_pos_z",
        "Pinky_pos_x",
        "Pinky_pos_y",
        "Pinky_pos_z",
        "Label"
    ]
    FEATURE_LIST = [
        "pitch",
        "roll",
        "yaw",
        "Thumb_dir_x",
        "Thumb_dir_y",
        "Thumb_dir_z",
        "Index_dir_x",
        "Index_dir_y",
        "Index_dir_z",
        "Pinky_dir_x",
        "Pinky_dir_y",
        "Pinky_dir_z",
        "Thumb_Index_x",
        "Thumb_Index_y",
        "Thumb_Index_z",
        "Index_Pinky_x",
        "Index_Pinky_y",
        "Index_Pinky_z",
        "Pinky_Thumb_x",
        "Pinky_Thumb_y",
        "Pinky_Thumb_z",
        "Label"
    ]