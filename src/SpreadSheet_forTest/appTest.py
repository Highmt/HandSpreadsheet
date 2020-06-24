import random
import sys
from PyQt5.QtWidgets import QApplication

from res.SSEnum import TestSectionEnum, TestModeEnum
from src.SpreadSheet_forTest.HandSpreadSheet import HandSpreadSheet

ModeNames = ["Gesture", "Shortcut-key", "Menu"]
SectionNames = ["Insert", "Delete", "Cut&Copy&Paste", "Sort"]
if __name__ == '__main__':
    modeList = [TestModeEnum.GESTURE.value, TestModeEnum.SHORTCUT_KEY.value]
    random.shuffle(modeList)
    sectionList = []
    for section in TestSectionEnum:
        sectionList.append(section.value)
    random.shuffle(sectionList)
    section_count = 1

    for section in sectionList:
        modes = list(modeList)
        task_count = 1
        for mode in modes:
            app = QApplication(sys.argv)
            print("Task: {0}-{1}\nSection: {2}, Mode: {3} start.".format(section_count, task_count,
                                                                         SectionNames[section], ModeNames[mode]))
            sheet = HandSpreadSheet(7, 7, mode, section)
            sheet.resize(500, 500)
            sheet.showFullScreen()
            app.exec_()
            print("Task: {0}-{1}\nSection: {2}, Mode: {3} end.".format(section_count, task_count,
                                                                       SectionNames[section], ModeNames[mode]))
            print("Push Return-key to next Task")
            del sheet
            del app
            task_count += 1
            input()
        section_count += 1
    sys.exit()
