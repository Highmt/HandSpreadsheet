import random
import sys
from PyQt5.QtWidgets import QApplication

from res.SSEnum import TestModeEnum
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet

ModeNames = ["Gesture", "Shortcut-key", "Menu"]
# SectionNames = ["Insert", "Delete", "Cut&Copy&Paste", "Sort"]
NUM_section = 5
if __name__ == '__main__':
    # modeList = [TestModeEnum.GESTURE.value, TestModeEnum.SHORTCUT_KEY.value]
    mode = TestModeEnum.GESTURE.value
    # random.shuffle(modeList)
    # sectionList = []
    # for section in range(NUM_section):
    #     sectionList.append(section)
    # random.shuffle(sectionList)
    # section_count = 1

    # modeList.reverse()
    # modes = list(modeList)
    # for mode in modes:
    for section in range(NUM_section):
        app = QApplication(sys.argv)
        print("Task: {0}-{1}\n ---------start----------.".format(section, ModeNames[mode]))
        sheet = HandSpreadSheet(rows=16, cols=16, mode=mode, section=section)
        sheet.showFullScreen()
        app.exec_()
        print("Task: {0}-{1}\n ----------END-----------.".format(section, ModeNames[mode]))
        print("Please rela\nPush Return-key to next Section")
        del sheet
        del app
        input()
    sys.exit()
