import random
import sys
from PyQt5.QtWidgets import QApplication

from res.SSEnum import TestSectionEnum, TestModeEnum
from src.SpreadSheet_test.HandSpreadSheet import HandSpreadSheet

ModeNames = ["Gesture", "Shortcut-key", "Menu"]
SectionNames = ["Insert", "Delete", "Cut&Copy&Paste", "Sort"]
if __name__ == '__main__':
    modeList = [TestModeEnum.SHORTCUT_KEY.value]
    # random.shuffle(modeList)
    sectionList = []
    # for section in TestSectionEnum:
    #     sectionList.append(section.value)
    # random.shuffle(sectionList)
    sectionList.append(2)
    section_count = 1

    # modeList.reverse()
    modes = list(modeList)
    for mode in modes:
        task_count = 1
        for section in sectionList:
            app = QApplication(sys.argv)
            print("Task: {0}-{1}\nSection: {2}, Mode: {3} start.".format(section_count, task_count,
                                                                         SectionNames[section], ModeNames[mode]))
            sheet = HandSpreadSheet(10, 10, mode, section)
            sheet.resize(1240, 700)
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
