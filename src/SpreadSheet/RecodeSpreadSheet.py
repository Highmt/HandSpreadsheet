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
import math
import os
import random
import sys
import time

import numpy as np
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QToolBar, QMenu, QPushButton, QDialog, QRadioButton,
                             QVBoxLayout, QButtonGroup, QDesktopWidget)

from res.SSEnum import ActionEnum, DirectionEnum, TestSectionEnum
from src.HandScensing.AppListener import AppListener
from src.HandScensing.CollectListener import CollectListener
from src.SpreadSheet.HandSpreadSheet import HandSpreadSheet
from src.SpreadSheet.OverlayGraphics import OverlayGraphics
from src.SpreadSheet.myTable import myTable
from src.Utility.spreadsheetitem import SpreadSheetItem
from src.Utility.util import encode_pos


# class circleWidget(QWidget):
#     def __init__(self, parent = None):
#         super(circleWidget, self).__init__(parent)
#
#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setPen(Qt.red)
#         painter.setBrush(Qt.yellow)
#         painter.drawEllipse(10, 10, 100, 100)

TASK_NUM = 1
USER_NO = 0
FILE_DIR = '../../res/data/study1/data{}'.format(USER_NO)
recordFeature = ["timestamp", "action", "direction"]
class RecodeSpreadSheet(HandSpreadSheet):
    def __init__(self, rows, cols, mode, section, parent=None):
        super(RecodeSpreadSheet, self).__init__(rows, cols, mode, section, parent)
        self.time_df = pd.DataFrame(columns=recordFeature)
        self.time_df.to_csv("{}/timeData.csv".format(self.listener.file_dir), mode='w')
        self.setRecordTimingTriger()

    def setRecordTimingTriger(self):
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
        time.sleep(0.1)
        self.listener.started = True
        self.startOpti()  # デバッグ時につけると初期状態でOptiTrack起動

    def actionOperate(self, act, direction):
        pass

    # TODO: FIX
    def recording(self):
        if self.table.selectedItems():
            if not self.isTestrun:
                print("Test has not started yet")

            elif self.table.selectedRanges()[0].topRow() == self.table.target_top and \
                    self.table.selectedRanges()[0].bottomRow() == self.table.target_height + self.table.target_top - 1 and \
                    self.table.selectedRanges()[0].leftColumn() == self.table.target_left and \
                    self.table.selectedRanges()[0].rightColumn() == self.table.target_width + self.table.target_left - 1:
                os.system('play -n synth %s sin %s' % (150 / 1000, 600))

                mocap_data = self.listener.getCurrentData()

                self.current_true_dict.get("action"), self.current_true_dict.get("direction")
                t = mocap_data.suffix_data.timestamp - self.listener.start_timestamp
                ps = pd.Series([t, self.current_true_dict.get("action"), self.current_true_dict.get("direction")], index=recordFeature)
                self.time_df = self.time_df.append(ps, ignore_index=True)

                self.table.resetRandomCellColor()

                print("Remaining Task: {}".format(len(self.true_list)))
                if len(self.true_list) == 0:
                    self.time_df.to_csv("{}/timeData.csv".format(self.listener.file_dir), mode='a', header=False, index=False)
                    self.finish()
                else:
                    self.startTest()

            self.table.clearSelection()
