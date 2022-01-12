#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2012 Hans-Peter Jansen <hpj@urpla.net>.
## Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
## Contact: Nokia Corporation (qt-info@nokia.com)
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:LGPL$
## GNU Lesser General Public License Usage
## This file may be used under the terms of the GNU Lesser General Public
## License version 2.1 as published by the Free Software Foundation and
## appearing in the file LICENSE.LGPL included in the packaging of this
## file. Please review the following information to ensure the GNU Lesser
## General Public License version 2.1 requirements will be met:
## http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
##
## In addition, as a special exception, Nokia gives you certain additional
## rights. These rights are described in the Nokia Qt LGPL Exception
## version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU General
## Public License version 3.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of this
## file. Please review the following information to ensure the GNU General
## Public License version 3.0 requirements will be met:
## http:#www.gnu.org/copyleft/gpl.html.
##
## Other Usage
## Alternatively, this file may be used in accordance with the terms and
## conditions contained in a signed written agreement between you and Nokia.
## $QT_END_LICENSE$
##
#############################################################################
import os
import random
import sys
import time

import numpy as np
import pandas as pd
from PyQt5.QtCore import QPoint, Qt, QTimer, QSize, QRect
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QToolBar, QMenu, QPushButton, QDialog, QRadioButton,
                             QVBoxLayout, QButtonGroup, QDesktopWidget, QDockWidget, QListWidget, QTextEdit,
                             QSizePolicy, QApplication)

from res.SSEnum import ActionEnum, DirectionEnum, TestTaskEnum, OperationEnum
from src.HandScensing.AppListener import AppListener
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet
from src.SpreadSheet.OverlayGraphics import OverlayGraphics
from src.SpreadSheet.myTable import myTable, cell_height, cell_width
from src.Utility.spreadsheetitem import SpreadSheetItem
from src.Utility.util import encode_pos


TASK_NUM = 3
USER_NO = 1
FILE = '/Users/yuta/develop/HandSpreadsheet/res/ResultExperiment/result_p{}.csv'.format(USER_NO)

class TestSpreadSheet(HandSpreadSheet):
    def __init__(self, section=None, parent=None):
        self.rows = int(QDesktopWidget().height() / cell_height - 2)
        self.cols = int(QDesktopWidget().width() / 4 / cell_width + 1)

        super(TestSpreadSheet, self).__init__(self.rows, self.cols)

        self.dock = QDockWidget("GOAL SHEET", self)
        self.goal_table = myTable(self.rows, self.cols, self)
        self.dock.setWidget(self.goal_table)
        self.dock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.widget().setMinimumWidth(self.width()/2)
        self.dock.widget().setMaximumWidth(self.width()/2)
        self.mainDock.widget().setMinimumWidth(self.width()/2)
        self.mainDock.widget().setMaximumWidth(self.width()/2)

        self.section = section
        self.start_time = 0
        self.setWindowTitle("TestSpreadSheet")
        self.setTestProperty()
        self.setTestTriger()

    def setTestTriger(self):
        self.start_test = QAction("start test", self)
        self.start_test.setShortcut('Ctrl+T')
        self.start_test.setShortcutContext(Qt.ApplicationShortcut)
        self.start_test.triggered.connect(self.startTest)
        self.testMenu = self.menuBar().addMenu("&Test")
        self.testMenu.addAction(self.start_test)

        self.table.currentItemChanged.connect(lambda: self.gestureBegin)

    def gestureBegin(self):
        self.start_time = time.time()

    def stepTask(self):
        self.goal_table.setupContents()
        self.current_true_dict = self.true_list.pop(0)
        if self.current_true_dict.get("action") == TestTaskEnum.COPY_PASTE.value or self.current_true_dict.get("action") == TestTaskEnum.CUT_PASTE.value:
            self.true_list.insert(0, {
                "action": ActionEnum.PASTE.value,
                "direction": DirectionEnum.NONE.value
            })

        self.goal_table.setGoalTable(self.current_true_dict.get("action"), self.current_true_dict.get("direction"))

        for i in range(self.goal_table.target_height):
            for j in range(self.goal_table.target_width):
                self.table.item(self.goal_table.target_top + i, self.goal_table.target_left + j).setBackground(Qt.blue)
        # self.pre_target = QRect(self.target_left, self.target_top, self.target_width, self.target_height)
        self.isTestrun = True
        self.error_count = 0

    def startTest(self):
        self.stepTask()

    def actionOperate(self, act, direction):
        self.actionTestOperate(act=act, direction=direction)

    def actionTestOperate(self, act, direction):
        if self.table.selectedItems():
            if not self.isTestrun:
                self.table.actionOperate(act, direction)
            elif self.table.selectedRanges()[0].topRow() == self.goal_table.target_top and \
                    self.table.selectedRanges()[0].bottomRow() == self.goal_table.target_height + self.goal_table.target_top - 1 and \
                    self.table.selectedRanges()[0].leftColumn() == self.goal_table.target_left and \
                    self.table.selectedRanges()[0].rightColumn() == self.goal_table.target_width + self.goal_table.target_left - 1:

                if act == self.current_true_dict.get("action") and direction == self.current_true_dict.get("direction"):
                    os.system('play -n synth %s sin %s' % (150 / 100, 600))
                else:
                    os.system('play -n synth %s sin %s' % (100 / 100, 220))
                    self.error_count = 1

                self.records = np.append(self.records,
                                         [[USER_NO,
                                           TASK_NUM*len(self.true_action_list)*len(self.true_direction_list) - len(self.true_list), time.time() - self.start_time,
                                           self.error_count,
                                           OperationEnum.OperationGrid.value[self.current_true_dict.get("action")][self.current_true_dict.get("direction")],
                                           OperationEnum.OperationGrid.value[act][direction]]], axis=0)

                if self.current_true_dict.get("action") == TestTaskEnum.COPY_PASTE.value or self.current_true_dict.get("action") == TestTaskEnum.CUT_PASTE.value:
                    self.current_true_dict = self.true_list.pop(0)

                else:
                    if len(self.true_list) == 0:
                        recordDF = pd.DataFrame(self.records, columns=['participant', 'No', 'time', 'error', 'true_manipulation', 'select_manipulation'])
                        recordDF['No'] = recordDF['No'].astype(int)
                        recordDF['error'] = recordDF['error'].astype(int)
                        recordDF['true_manipulation'] = recordDF['true_manipulation'].astype(int)
                        recordDF['true_direction'] = recordDF['true_direction'].astype(int)
                        recordDF['select_manipulation'] = recordDF['select_manipulation'].astype(int)
                        recordDF['select_direction'] = recordDF['select_direction'].astype(int)
                        print(recordDF)
                        if os.path.isfile(FILE):
                            recordDF.to_csv(FILE, mode='a', header=False, index=False)
                        else:
                            recordDF.to_csv(FILE, mode='x', header=True, index=False)
                        self.finish()
                    else:
                        self.stepTask()
                        print("Remaining Task: {}".format(len(self.true_list)))

                # if self.end_Opti.isEnabled():
                self.listener.resetHand()
            self.table.clearSelection()

    def setTestProperty(self):
        # タスク毎の操作種類
        self.true_action_list = []
        self.true_direction_list = []

        self.true_action_list.append(TestTaskEnum.INSERT.value)
        self.true_direction_list.append([DirectionEnum.HORIZON.value, DirectionEnum.VERTICAL.value])
        self.true_action_list.append(TestTaskEnum.DELETE.value)
        self.true_direction_list.append([DirectionEnum.HORIZON.value, DirectionEnum.VERTICAL.value])

        self.true_action_list.append(TestTaskEnum.COPY_PASTE.value)
        self.true_direction_list.append([DirectionEnum.NONE.value])

        self.true_action_list.append(TestTaskEnum.CUT_PASTE.value)
        self.true_direction_list.append([DirectionEnum.NONE.value])

        self.true_action_list.append(TestTaskEnum.SORT.value)
        self.true_direction_list.append([DirectionEnum.FRONT.value, DirectionEnum.BACK.value])

        self.true_list = []
        for i in range(len(self.true_action_list)):
            for j in range(len(self.true_direction_list[i])):
                true_dict = {
                    "action": self.true_action_list[i],
                    "direction": self.true_direction_list[i][j]
                }
                for k in range(TASK_NUM):
                    self.true_list.append(true_dict)

        random.shuffle(self.true_list)
        self.records = np.empty([0, 9])
        self.isTestrun = False

