import random
import sys
from PyQt5.QtWidgets import QApplication

from res.SSEnum import TestModeEnum
from src.SpreadSheet.RecodeSpreadSheet import RecodeSpreadSheet

ModeName = "Gesture"
# SectionNames = ["Insert", "Delete", "Cut&Copy&Paste", "Sort"]
NUM_section = 5
if __name__ == '__main__':
    mode = TestModeEnum.GESTURE.value
    for section in range(NUM_section):
        app = QApplication(sys.argv)
        print("Task: {0}-{1}\n ---------start----------.".format(section, ModeName))
        sheet = RecodeSpreadSheet(rows=16, cols=16, mode=mode, section=section)
        app.exec_()
        print("Task: {0}-{1}\n ----------END-----------.".format(section, ModeName))
        print("Please relax\nPush Return-key to next Section")
        del sheet
        del app
        input()
    sys.exit()
