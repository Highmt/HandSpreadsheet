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
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QToolBar, QMenu, QPushButton, QDialog, QRadioButton,
                             QVBoxLayout, QButtonGroup, QDesktopWidget, QDockWidget)

from res.SSEnum import ActionEnum, DirectionEnum
from src.HandScensing.AppListener import AppListener
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

class HandSpreadSheet(QMainWindow):
    def __init__(self, rows, cols, parent=None):
        super(HandSpreadSheet, self).__init__(parent)

        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)  # ツールバーの追加
        self.formulaInput = QLineEdit()
        self.cellLabel = QLabel(self.toolBar)
        self.cellLabel.setMinimumSize(80, 0)
        self.toolBar.addWidget(self.cellLabel)
        self.toolBar.addWidget(self.formulaInput)
        self.table = myTable(rows, cols, self)

        # TODO: リボンメニュー（未作成）
        # self.ribonBar = QToolBar()
        # self.addToolBar(self.ribonBar)

        # アクションの追加
        self.createMenuActions()
        self.createTableActions()

        self.updateColor()
        self.setupMenuBar()

        self.mainDock = QDockWidget("MAIN SHEET", self)
        self.mainDock.setWidget(self.table)
        self.mainDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.mainDock)

        # self.setCentralWidget(self.table)
        self.createStatusBar()

        # self.setupContextMenu()  # コンテクストメニュー設定
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.openContextMenu)

        self.table.currentItemChanged.connect(self.updateStatus)
        self.table.currentItemChanged.connect(self.updateColor)
        self.table.currentItemChanged.connect(self.updateLineEdit)
        self.table.itemChanged.connect(self.updateStatus)
        self.formulaInput.returnPressed.connect(self.returnPressed)
        self.table.itemChanged.connect(self.updateLineEdit)
        self.table.itemSelectionChanged.connect(self.cellSelect)
        self.setWindowTitle("HandSpreadSheet")

        # Create an overlay layer
        self.overlayLayout = QHBoxLayout(self.table)
        self.overlayLayout.setContentsMargins(0, 0, 0, 0)
        self.overlayGraphics = OverlayGraphics()  # 描画するGraphicsView
        self.overlayLayout.addWidget(self.overlayGraphics)

        # self.table.itemAt(50, 50).setSelected(True) # テーブルアイテムの設定の仕方

        # set hand track setting
        self.isUseOpti = True
        if self.isUseOpti:
            self.setAppListener()

        monitor = QDesktopWidget().screenGeometry(1)
        self.move(monitor.left(), monitor.top())
        # self.showFullScreen()
        self.showMaximized()

        self.mainDock.widget().setMinimumWidth(self.width())
        self.mainDock.widget().setMaximumWidth(self.width())

    def setAppListener(self):
    # Create a sample listener and controller
        self.listener = AppListener()
        self.listener.initOptiTrack()
        self.listener.do_calibration()
        self.listener.stop()
        self.listener.setListener()

        self.setOptiSignal()

        self.startOpti()  # デバッグ時につけると初期状態でOptiTrack起動
        return

    def createStatusBar(self):

        self.optiLabel = QLabel("")
        # self.optiLabel = QLabel("OptiTrack is disconnecting")
        self.optiLabel.setAlignment(Qt.AlignLeft)
        self.optiLabel.setMinimumSize(self.optiLabel.sizeHint())

        self.pointStatusLabel = QLabel("")
        self.pointStatusLabel.setAlignment(Qt.AlignLeft)
        self.pointStatusLabel.setContentsMargins(0, 0, 30, 0)

        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignLeft)
        self.statusLabel.setContentsMargins(0, 0, 30, 0)

        self.statusBar().addWidget(self.optiLabel)
        # self.statusBar().addPermanentWidget(self.pointStatusLabel)
        self.statusBar().addPermanentWidget(self.statusLabel)

        self.statusBar().setFont(QFont('Times', 60))

    def createMenuActions(self):
        self.start_Opti = QAction("StartOpti", self)
        self.start_Opti.setShortcut('Ctrl+O')
        self.start_Opti.setShortcutContext(Qt.ApplicationShortcut)
        self.start_Opti.triggered.connect(self.startOpti)

        self.end_Opti = QAction("EndOpti", self)
        self.end_Opti.setShortcut('Shift+Ctrl+O')
        self.end_Opti.setShortcutContext(Qt.ApplicationShortcut)
        self.end_Opti.triggered.connect(self.endOpti)
        self.end_Opti.setEnabled(False)

        self.active_Point = QAction("active", self)
        self.active_Point.triggered.connect(self.activePointing)
        self.active_Point.setEnabled(False)

        self.negative_Point = QAction("negative", self)
        self.negative_Point.triggered.connect(self.negativePointing)
        self.negative_Point.setEnabled(False)

    def setupMenuBar(self):
        self.optiMenu = self.menuBar().addMenu("&OptiTrack")
        self.optiMenu.addAction(self.start_Opti)
        self.optiMenu.addAction(self.end_Opti)

        self.optiMenu.addSeparator()

        self.pointMenu = self.optiMenu.addMenu("&PointMode")
        self.pointMenu.addAction(self.active_Point)
        self.pointMenu.addAction(self.negative_Point)
        self.pointMenu.setEnabled(False)

    def createTableActions(self):
        self.insert_Action = QAction("Insert...", self)
        self.insert_Action.setShortcut("Ctrl+I")
        self.insert_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.insert_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.insert_Action)
        self.insert_Action.triggered.connect(self.showInsertDialog)

        self.delete_Action = QAction("Delete...", self)
        self.delete_Action.setShortcut("Ctrl+D")
        self.delete_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.delete_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.delete_Action)
        self.delete_Action.triggered.connect(self.showDeleteDialog)

        self.sort_AtoZ_Action = QAction("Sort A to Z", self)
        self.sort_AtoZ_Action.setShortcut("Alt+Down")
        self.sort_AtoZ_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.sort_AtoZ_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.sort_AtoZ_Action)
        self.sort_AtoZ_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.SORT.value, DirectionEnum.FRONT.value))

        self.sort_ZtoA_Action = QAction("Sort Z to A", self)
        self.sort_ZtoA_Action.setShortcut("Alt+Up")
        self.sort_ZtoA_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.sort_ZtoA_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.sort_ZtoA_Action)
        self.sort_ZtoA_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.SORT.value, DirectionEnum.BACK.value))

        self.copy_Action = QAction("Copy", self)
        self.copy_Action.setShortcut("Ctrl+C")
        self.copy_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.copy_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.copy_Action)
        self.copy_Action.triggered.connect(lambda: self.actionOperate(ActionEnum.COPY.value, DirectionEnum.NONE.value))

        self.cut_Action = QAction("Cut", self)
        self.cut_Action.setShortcut("Ctrl+X")
        self.cut_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.cut_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.cut_Action)
        self.cut_Action.triggered.connect(lambda: self.actionOperate(ActionEnum.CUT.value, DirectionEnum.NONE.value))

        self.paste_Action = QAction("Paste", self)
        self.paste_Action.setShortcut("Ctrl+V")
        self.paste_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.paste_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.paste_Action)
        self.paste_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.PASTE.value, DirectionEnum.NONE.value))

        # ショートカットキー専用アクション
        self.insert_right_Action = QAction(self)
        self.insert_right_Action.setShortcut("Ctrl+Right")
        self.insert_right_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.insert_right_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.insert_right_Action)
        self.insert_right_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.INSERT.value, DirectionEnum.HORIZON.value))

        self.insert_down_Action = QAction(self)
        self.insert_down_Action.setShortcut("Ctrl+Down")
        self.insert_down_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.insert_down_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.insert_down_Action)
        self.insert_down_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.INSERT.value, DirectionEnum.VERTICAL.value))

        self.delete_left_Action = QAction(self)
        self.delete_left_Action.setShortcut("Ctrl+Left")
        self.delete_left_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.delete_left_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.delete_left_Action)
        self.delete_left_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.DELETE.value, DirectionEnum.HORIZON.value))

        self.delete_up_Action = QAction(self)
        self.delete_up_Action.setShortcut("Ctrl+Up")
        self.delete_up_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.delete_up_Action.setShortcutVisibleInContextMenu(True)
        self.addAction(self.delete_up_Action)
        self.delete_up_Action.triggered.connect(
            lambda: self.actionOperate(ActionEnum.DELETE.value, DirectionEnum.VERTICAL.value))

    def openContextMenu(self, event):
        menu = QMenu()
        menu.addAction(self.cut_Action)
        menu.addAction(self.copy_Action)
        menu.addAction(self.paste_Action)
        menu.addAction("Paste Special...")
        menu.addSeparator()
        menu.addAction("Smart Lookup...")
        menu.addAction("Thesaurus...")
        menu.addSeparator()
        menu.addAction(self.insert_Action)
        menu.addAction(self.delete_Action)
        menu.addAction("Clear Contents")
        menu.addSeparator()
        menu.addAction("Filter")
        sort_menu = QMenu("Sort")
        sort_menu.addAction(self.sort_AtoZ_Action)
        sort_menu.addAction(self.sort_ZtoA_Action)
        menu.addMenu(sort_menu)
        menu.addSeparator()
        menu.addAction("New Comment")
        menu.addAction("New Note")
        menu.addSeparator()
        menu.addAction("Format Cells...")
        menu.addAction("Pick From Drop-down List...")
        menu.addAction("Define Name...")
        menu.addAction("Hyperlink...")
        menu.addSeparator()
        smartphone = QAction("Smart Phone", self)
        menu.addAction(smartphone)
        smartphone.setEnabled(False)
        menu.addAction("Take Photo")
        menu.addAction("Scan Documents")
        menu.addAction("Add Sketch")
        menu.addSeparator()
        menu.addAction("Services")
        menu.exec_(self.mapToGlobal(event))

    def showInsertDialog(self):
        insert_dialog = QDialog()
        radio_layout = QVBoxLayout(insert_dialog)
        label = QLabel('Witch direction shift cells?')
        self.radio_insert_group = QButtonGroup()
        self.radio_insert_right = QRadioButton('Shift cells right')
        self.radio_insert_down = QRadioButton('Shift cells down')
        self.radio_insert_group.addButton(self.radio_insert_right, DirectionEnum.HORIZON.value)
        self.radio_insert_group.addButton(self.radio_insert_down, DirectionEnum.VERTICAL.value)
        radio_layout.addWidget(label)
        radio_layout.addWidget(self.radio_insert_right)
        radio_layout.addWidget(self.radio_insert_down)

        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        radio_layout.addLayout(button_layout)
        insert_button.clicked.connect(self.clickedDialogInsertButton)
        insert_button.clicked.connect(insert_dialog.close)
        cancel_button.clicked.connect(insert_dialog.close)
        insert_dialog.setWindowTitle("Insert...")
        insert_dialog.setWindowModality(Qt.ApplicationModal)
        insert_dialog.exec_()

    def clickedDialogInsertButton(self):
        if self.radio_insert_group.checkedId() > 0:
            self.actionOperate(ActionEnum.INSERT.value, self.radio_insert_group.checkedId())

    def showDeleteDialog(self):
        delete_dialog = QDialog()
        radio_layout = QVBoxLayout(delete_dialog)
        label = QLabel('Witch direction shift cells?')
        self.radio_delete_group = QButtonGroup()
        self.radio_delete_left = QRadioButton('Shift cells left')
        self.radio_delete_up = QRadioButton('Shift cells up')
        self.radio_delete_group.addButton(self.radio_delete_left, DirectionEnum.HORIZON.value)
        self.radio_delete_group.addButton(self.radio_delete_up, DirectionEnum.VERTICAL.value)
        radio_layout.addWidget(label)
        radio_layout.addWidget(self.radio_delete_left)
        radio_layout.addWidget(self.radio_delete_up)

        delete_button = QPushButton("Delete")
        cancel_button = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)
        radio_layout.addLayout(button_layout)
        delete_button.clicked.connect(self.clickedDialogDeleteButton)
        delete_button.clicked.connect(delete_dialog.close)
        cancel_button.clicked.connect(delete_dialog.close)
        delete_dialog.setWindowTitle("Delete...")
        delete_dialog.setWindowModality(Qt.ApplicationModal)
        delete_dialog.exec_()

    def clickedDialogDeleteButton(self):
        if self.radio_delete_group.checkedId() > 0:
            self.actionOperate(ActionEnum.DELETE.value, self.radio_delete_group.checkedId())

    def updateStatus(self, item):
        if item and item == self.table.currentItem():
            self.statusBar().showMessage(item.data(Qt.StatusTipRole), 1500)
            self.cellLabel.setText("Cell: (%s)" % encode_pos(self.table.row(item),
                                                             self.table.column(item)))

    def updateColor(self):
        pixmap = QPixmap(16, 16)
        color = QColor()
        if not color.isValid():
            color = self.palette().base().color()
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 16, 16, color)
        lighter = color.lighter()
        painter.setPen(lighter)
        # light frame
        painter.drawPolyline(QPoint(0, 15), QPoint(0, 0), QPoint(15, 0))
        painter.setPen(color.darker())
        # dark frame
        painter.drawPolyline(QPoint(1, 15), QPoint(15, 15), QPoint(15, 1))
        painter.end()
        # self.colorAction.setIcon(QIcon(pixmap))

    def updateLineEdit(self, item):
        if item != self.table.currentItem():
            return
        if item and len(self.table.selectedItems()) == 1:
            self.formulaInput.setText(item.data(Qt.EditRole))
        else:
            self.formulaInput.clear()

    def returnPressed(self):
        text = self.formulaInput.text()
        row = self.table.currentRow()
        col = self.table.currentColumn()
        item = self.table.item(row, col)
        if not item:
            self.table.setItem(row, col, SpreadSheetItem(text))

        else:
            item.setData(Qt.EditRole, text)
        self.table.viewport().update()

    def startOpti(self):
        # Have the sample listener receive events from the controller
        self.listener.restart()

    def endOpti(self):
        self.listener.restart()

    def activePointing(self):
        self.listener.setPointingMode(True)
        self.active_Point.setEnabled(False)
        self.negative_Point.setEnabled(True)
        self.overlayGraphics.setTargetMode(True)
        # self.pointStatusLabel.setText("Pointing mode: active")

    def negativePointing(self):
        self.listener.setPointingMode(False)
        self.negative_Point.setEnabled(False)
        self.active_Point.setEnabled(True)
        self.overlayGraphics.setTargetMode(False)
        # self.pointStatusLabel.setText("Pointing mode: negative")

    def changeOpti(self, toConnect):
        if toConnect:
            self.start_Opti.setEnabled(False)
            self.end_Opti.setEnabled(True)
            self.pointMenu.setEnabled(True)
            self.active_Point.setEnabled(True)
            # self.optiLabel.setText("OptiTrack: connecting")
            # self.pointStatusLabel.setText("Pointing mode: negative")
        else:
            self.end_Opti.setEnabled(False)
            self.start_Opti.setEnabled(True)
            self.pointMenu.setEnabled(False)
            self.negative_Point.setEnabled(False)
            # self.optiLabel.setText("OptiTrack: disconnecting")
            self.overlayGraphics.hide()
            self.pointStatusLabel.setText("")

    def closeEvent(self, event):
        self.listener.shutdown()
        print("close")

    def finish(self):
        self.showNormal()
        QTimer.singleShot(5000, self.close)

    def cellSelect(self):
        if self.table.selectedItems():
            self.overlayGraphics.luRect, self.overlayGraphics.rbRect = self.table.getItemCoordinate()
            self.overlayGraphics.isSelected = True

    def actionOperate(self, act, direction):
        self.table.actionOperate(act, direction)

        if self.isUseOpti:
            self.listener.resetHand()

    def setOptiSignal(self):
        self.listener.hide_feedback.connect(self.overlayGraphics.hide)
        self.listener.show_feedback.connect(self.overlayGraphics.show)
        self.listener.change_feedback.connect(self.overlayGraphics.feedbackShow)
        self.listener.action_operation.connect(self.actionOperate)
        self.listener.start_end_opti.connect(self.changeOpti)
