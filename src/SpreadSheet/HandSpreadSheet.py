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

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QPainter, QPixmap, QBrush, QKeySequence
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QToolBar, QMenu, QMessageBox, QPushButton, QDialog, QRadioButton,
                             QVBoxLayout, QButtonGroup)

from lib.LeapMotion import Leap
from res.SSEnum import ActionEnum, DirectionEnum
from src.HandScensing.HandListener import HandListener
from src.SpreadSheet.OverlayGraphics import OverlayGraphics
from src.SpreadSheet.myTable import myTable
from src.SpreadSheet.spreadsheetitem import SpreadSheetItem
from src.SpreadSheet.util import encode_pos


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

        # アクションの追加
        self.createMenuActions()
        self.createTableActions()

        self.updateColor(0)
        self.setupMenuBar()


        self.setCentralWidget(self.table)
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

        # Create a overlay layer
        self.overlayLayout = QHBoxLayout(self.table)
        self.overlayLayout.setContentsMargins(0, 0, 0, 0)
        self.overlayGraphics = OverlayGraphics()  # 描画するGraphicsView
        self.overlayLayout.addWidget(self.overlayGraphics)

        # Create a sample listener and controller
        self.listener = HandListener()
        self.controller = Leap.Controller()
        self.setLeapSignal()


        self.startLeap()   # デバッグ時につけると初期状態でLeapMotion起動
        # self.table.itemAt(50, 50).setSelected(True) # テーブルアイテムの設定の仕方

    def createStatusBar(self):
        self.leapLabel = QLabel("LeapMotion is disconnecting")
        self.leapLabel.setAlignment(Qt.AlignLeft)
        self.leapLabel.setMinimumSize(self.leapLabel.sizeHint())

        self.pointStatusLabel = QLabel("")
        self.pointStatusLabel.setAlignment(Qt.AlignLeft)

        self.statusBar().addWidget(self.leapLabel)
        self.statusBar().addPermanentWidget(self.pointStatusLabel)





    def actionInsert(self):
        pass

    def actionDelete(self):
        pass

    def actionSort(self):
        pass

    def actionCopy(self):
        pass

    def actionCut(self):
        pass

    def actionPaste(self):
        pass

    def createMenuActions(self):
        self.start_Leap = QAction("StartLeap", self)
        self.start_Leap.setShortcut('Ctrl+L')
        self.start_Leap.setShortcutContext(Qt.ApplicationShortcut)
        self.start_Leap.triggered.connect(self.startLeap)

        self.end_Leap = QAction("EndLeap", self)
        self.end_Leap.triggered.connect(self.endLeap)
        self.end_Leap.setEnabled(False)

        self.active_Point = QAction("active", self)
        self.active_Point.triggered.connect(self.activePointing)
        self.active_Point.setEnabled(False)

        self.negative_Point = QAction("negative", self)
        self.negative_Point.triggered.connect(self.negativePointing)
        self.negative_Point.setEnabled(False)


    def setupMenuBar(self):
        self.leapMenu = self.menuBar().addMenu("&LeapMotion")
        self.leapMenu.addAction(self.start_Leap)
        self.leapMenu.addAction(self.end_Leap)

        self.leapMenu.addSeparator()

        self.pointMode = self.leapMenu.addMenu("&PointMode")
        self.pointMode.addAction(self.active_Point)
        self.pointMode.addAction(self.negative_Point)
        self.pointMode.setEnabled(False)

    def createTableActions(self):
        self.insert_Action = QAction("Insert...", self)
        self.insert_Action.triggered.connect(self.showInsertDialog)

        self.delete_Action = QAction("Delete...", self)
        self.delete_Action.triggered.connect(self.showDeleteDialog)

        self.sort_AtoZ_Action = QAction("Sort A to Z", self)
        # self.sort_AtoZ_Action.setShortcut('Ctrl+E')
        # self.sort_AtoZ_Action.setShortcutContext(Qt.ApplicationShortcut)
        self.sort_AtoZ_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.SORT.value, DirectionEnum.BACK.value))

        self.sort_ZtoA_Action = QAction("Sort Z to A", self)
        self.sort_ZtoA_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.SORT.value, DirectionEnum.FRONT.value))

        self.copy_Action = QAction("Copy", self)
        self.copy_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.COPY.value, None))

        self.cut_Action = QAction("Cut", self)
        self.cut_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.CUT.value, None))

        self.paste_Action = QAction("Paste", self)
        self.paste_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.PASTE.value, None))

        # ショートカットキー専用アクション
        self.insert_right_Action = QAction("Insert...", self)
        self.insert_right_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.INSERT.value, DirectionEnum.HORIZON.value))
        self.insert_down_Action = QAction("Insert...", self)
        self.insert_down_Action.triggered.connect(lambda: self.table.actionOperate(ActionEnum.INSERT.value, DirectionEnum.VERTICAL.value))

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
        insert_button.clicked.connect(self.clickedInsertButton)
        insert_button.clicked.connect(insert_dialog.close)
        cancel_button.clicked.connect(insert_dialog.close)
        insert_dialog.setWindowTitle("Insert...")
        insert_dialog.setWindowModality(Qt.ApplicationModal)
        insert_dialog.exec_()
        
    def clickedInsertButton(self):
        if self.radio_insert_group.checkedId() > 0:
            self.table.actionOperate(ActionEnum.INSERT.value, self.radio_insert_group.checkedId())

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
        delete_button.clicked.connect(self.clickedDeleteButton)
        delete_button.clicked.connect(delete_dialog.close)
        cancel_button.clicked.connect(delete_dialog.close)
        delete_dialog.setWindowTitle("Delete...")
        delete_dialog.setWindowModality(Qt.ApplicationModal)
        delete_dialog.exec_()

    def clickedDeleteButton(self):
        if self.radio_delete_group.checkedId() > 0:
            self.table.actionOperate(ActionEnum.DELETE.value, self.radio_delete_group.checkedId())

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

    def updateStatus(self, item):
        if item and item == self.table.currentItem():
            self.statusBar().showMessage(item.data(Qt.StatusTipRole), 1000)
            self.cellLabel.setText("Cell: (%s)" % encode_pos(self.table.row(item),
                                                             self.table.column(item)))

    def updateColor(self, item):
        pixmap = QPixmap(16, 16)
        color = QColor()
        # if item:
        #     color = item.backgroundColor()
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
        if item:
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

    def startLeap(self):
        # Have the sample listener receive events from the controller
        self.controller.add_listener(self.listener)

    def endLeap(self):
        self.controller.remove_listener(self.listener)

    def activePointing(self):
        self.listener.setPointingMode(True)
        self.active_Point.setEnabled(False)
        self.negative_Point.setEnabled(True)
        self.overlayGraphics.setTargetMode(True)
        self.pointStatusLabel.setText("Pointing mode: active")

    def negativePointing(self):
        self.listener.setPointingMode(False)
        self.negative_Point.setEnabled(False)
        self.active_Point.setEnabled(True)
        self.overlayGraphics.setTargetMode(False)
        self.pointStatusLabel.setText("Pointing mode: negative")

    def changeLeap(self, toConnect):
        if toConnect:
            self.start_Leap.setEnabled(False)
            self.end_Leap.setEnabled(True)
            self.pointMode.setEnabled(True)
            self.active_Point.setEnabled(True)
            self.leapLabel.setText("LeapMotion: connecting")
            self.pointStatusLabel.setText("Pointing mode: negative")
        else:
            self.end_Leap.setEnabled(False)
            self.start_Leap.setEnabled(True)
            self.pointMode.setEnabled(False)
            self.negative_Point.setEnabled(False)
            self.leapLabel.setText("LeapMotion: disconnecting")
            self.overlayGraphics.hide()
            self.pointStatusLabel.setText("")

    def closeEvent(self, event):
        self.controller.remove_listener(self.listener)

    def cellSelect(self):
        self.overlayGraphics.luRect, self.overlayGraphics.rbRect = self.table.getItemCoordinate()
        self.overlayGraphics.isSelected = True

    def setLeapSignal(self):
        self.listener.hide_feedback.connect(self.overlayGraphics.hide)
        self.listener.show_feedback.connect(self.overlayGraphics.show)
        self.listener.change_feedback.connect(self.overlayGraphics.feedbackShow)
        self.listener.action_operation.connect(self.table.actionOperate)
        self.listener.startorend_leap.connect(self.changeLeap)


