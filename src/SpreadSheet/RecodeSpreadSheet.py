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
import copy

import math
import os
import random
import time

import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QDockWidget, QDesktopWidget

from res.SSEnum import ActionEnum, DirectionEnum
from src.HandScensing.CollectListener import CollectListener
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet
from src.SpreadSheet.myTable import myTable, cell_height, cell_width

TASK_NUM = 3
USER_NO = 7
FILE_DIR = '../../res/data/study1/data{}'.format(USER_NO)
recordFeature = ["timestamp", "action", "direction"]

class RecodeSpreadSheet(HandSpreadSheet):
    def __init__(self, rows, cols, mode, section, parent=None):
        self.rows = int(QDesktopWidget().height() / cell_height - 2)
        self.cols = int(QDesktopWidget().width() / 2 / cell_width + 1)
        super(RecodeSpreadSheet, self).__init__(self.rows, self.cols)
        self.mode = mode
        self.section = section
        self.time_df = pd.DataFrame(columns=recordFeature)
        # self.time_df.to_csv("{}/timeData.csv".format(self.listener.file_dir), mode='w')
        # self.table.currentItemChanged.connect(self.gestureBegin)
        self.setWindowTitle("RecodeSpreadSheet")
        self.setTestProperty(self.section)
        self.setTestTriger()

    def setTestTriger(self):
        self.start_test = QAction("start test", self)
        self.start_test.setShortcut('Ctrl+T')
        self.start_test.setShortcutContext(Qt.ApplicationShortcut)
        self.start_test.triggered.connect(self.startTest)
        self.testMenu = self.menuBar().addMenu("&Test")
        self.testMenu.addAction(self.start_test)

        self.execute = QAction("execute operation", self)
        self.execute.setShortcut('Alt+H')
        self.execute.setShortcutContext(Qt.ApplicationShortcut)
        self.execute.triggered.connect(self.recording)
        self.addAction(self.execute)

    def setAppListener(self):
        # Create a sample listener and controller
        self.listener = CollectListener("{}/sec_{}/".format(FILE_DIR, self.section))
        self.listener.initOptiTrack()
        self.listener.do_calibration()
        self.listener.stop()
        self.listener.setListener()
        self.listener.data_num = math.inf
        self.listener.action_threshold = -100.0
        time.sleep(0.1)
        self.startOpti()  # デバッグ時につけると初期状態でOptiTrack起動

    def gestureBegin(self):
        self.listener.started = True

    def actionOperate(self, act, direction):
        pass

    def startTest(self):
        self.stepTask()

    def stepTask(self):
        self.current_true_dict = self.true_list.pop(0)

        if self.current_true_dict.get("action") == ActionEnum.INSERT.value:
            if self.current_true_dict.get('direction') == DirectionEnum.HORIZON.value:
                self.statusLabel.setText("Insert Shift Right")
            else:
                self.statusLabel.setText("Insert Shift Down")

        elif self.current_true_dict.get("action") == ActionEnum.DELETE.value:
            if self.current_true_dict.get('direction') == DirectionEnum.HORIZON.value:
                self.statusLabel.setText("Delete Shift Left")
            else:
                self.statusLabel.setText("Delete Shift Up")

        elif self.current_true_dict.get('action') == ActionEnum.CUT.value:
            self.statusLabel.setText("Cut")
        elif self.current_true_dict.get('action') == ActionEnum.COPY.value:
            self.statusLabel.setText("Copy")
        elif self.current_true_dict.get('action') == ActionEnum.PASTE.value:
            self.statusLabel.setText("Paste")

        else:
            if self.current_true_dict.get('direction') == DirectionEnum.FRONT.value:
                self.statusLabel.setText("Sort A to Z")
            else:
                self.statusLabel.setText("Sort Z to A")

        self.isTestrun = True
        self.error_count = 0
        self.table.setRandomCellColor()

    def recording(self):
        if self.table.selectedItems():
            if not self.isTestrun:
                print("Test has not started yet")

            elif self.table.selectedRanges()[0].topRow() == self.table.target_top and \
                    self.table.selectedRanges()[0].bottomRow() == self.table.target_height + self.table.target_top - 1 and \
                    self.table.selectedRanges()[0].leftColumn() == self.table.target_left and \
                    self.table.selectedRanges()[0].rightColumn() == self.table.target_width + self.table.target_left - 1:
                os.system('play -n synth %s sin %s' % (150 / 1000, 600))

                self.current_true_dict.get("action"), self.current_true_dict.get("direction")
                t = time.time() - self.listener.start_timestamp
                ps = pd.Series([t, self.current_true_dict.get("action"), self.current_true_dict.get("direction")], index=recordFeature)
                self.time_df = self.time_df.append(ps, ignore_index=True)

                print("Remaining Task: {}".format(len(self.true_list)))
                self.listener.started = False
                if len(self.true_list) == 0:
                    self.time_df.to_csv("{}/timeData.csv".format(self.listener.file_dir), mode='a', header=False)
                    self.listener.data_save_pandas(lr="left", data=copy.deepcopy(self.listener.dfs[0]))
                    self.listener.data_save_pandas(lr="right", data=copy.deepcopy(self.listener.dfs[1]))
                    self.finish()
                else:
                    self.stepTask()
                    self.listener.current_collect_id = self.listener.current_collect_id + 1

            self.table.clearSelection()

    def setTestProperty(self, section):
        # タスク毎の操作種類
        self.true_action_list = []
        self.true_direction_list = []

        self.true_action_list.append(ActionEnum.INSERT.value)
        self.true_direction_list.append([DirectionEnum.HORIZON.value, DirectionEnum.VERTICAL.value])
        self.true_action_list.append(ActionEnum.DELETE.value)
        self.true_direction_list.append([DirectionEnum.HORIZON.value, DirectionEnum.VERTICAL.value])

        self.true_action_list.append(ActionEnum.COPY.value)
        self.true_direction_list.append([DirectionEnum.NONE.value])

        self.true_action_list.append(ActionEnum.CUT.value)
        self.true_direction_list.append([DirectionEnum.NONE.value])

        self.true_action_list.append(ActionEnum.PASTE.value)
        self.true_direction_list.append([DirectionEnum.NONE.value])

        self.true_action_list.append(ActionEnum.SORT.value)
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

