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
from PyQt5 import QtCore
from PyQt5.QtCore import QDate, QPoint, Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QIcon, QKeySequence, QPainter, QPixmap, QPen, QBrush, QImage, QPalette
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QColorDialog,
                             QComboBox, QDialog, QFontDialog, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QToolBar, QVBoxLayout, QGraphicsView, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsEllipseItem)

from src.LeapMotion import Leap
from src.HandSpreadSheetLeap import handListener
from src.OverlayGraphics import OverlayGraphics
from src.myTable import myTable
from src.spreadsheetitem import SpreadSheetItem
from src.util import decode_pos, encode_pos


# class circleWidget(QWidget):
#     def __init__(self, parent = None):
#         super(circleWidget, self).__init__(parent)
#
#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setPen(Qt.red)
#         painter.setBrush(Qt.yellow)
#         painter.drawEllipse(10, 10, 100, 100)

class SpreadSheet(QMainWindow):
    def __init__(self, rows, cols, parent=None):
        super(SpreadSheet, self).__init__(parent)

        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)  #　ツールバーの追加
        self.formulaInput = QLineEdit()
        self.cellLabel = QLabel(self.toolBar)
        self.cellLabel.setMinimumSize(80, 0)
        self.toolBar.addWidget(self.cellLabel)
        self.toolBar.addWidget(self.formulaInput)
        self.table = myTable(rows, cols, self)

        self.createActions()   # アクションの追加
        self.updateColor(0)
        self.setupMenuBar()

        self.setupContextMenu()
        self.setCentralWidget(self.table)
        self.statusBar()
        self.createStatusBar()
        self.table.currentItemChanged.connect(self.updateStatus)
        self.table.currentItemChanged.connect(self.updateColor)
        self.table.currentItemChanged.connect(self.updateLineEdit)
        self.table.itemChanged.connect(self.updateStatus)
        self.formulaInput.returnPressed.connect(self.returnPressed)
        self.table.itemChanged.connect(self.updateLineEdit)
        self.setWindowTitle("HandSpreadSheet")

        # Create a overlay layer
        self.overlayLayout = QHBoxLayout(self.table)
        self.overlayLayout.setContentsMargins(0, 0, 0, 0)
        self.overlayGraphics = OverlayGraphics()  # 描画するGraphicsView
        self.overlayLayout.addWidget(self.overlayGraphics)
        # self.overlayGraphics.hide()  # 描画を非表示

        # Create a sample listener and controller
        self.listener = handListener(self)
        self.controller = Leap.Controller()

        # self.table.itemAt(50, 50).setSelected(True) # テーブルアイテムの設定の仕方

    def createStatusBar(self):
        self.leapLabel = QLabel("LeapMotion is disconnecting")
        self.leapLabel.setAlignment(Qt.AlignLeft)
        self.leapLabel.setMinimumSize(self.leapLabel.sizeHint())

        self.pointingLabel = QLabel("")
        self.pointingLabel.setAlignment(Qt.AlignLeft)

        self.statusBar().addWidget(self.leapLabel)
        self.statusBar().addPermanentWidget(self.pointingLabel)


    def createActions(self):
        self.start_Leap = QAction("startLeap", self)
        self.start_Leap.triggered.connect(self.startLeap)

        self.end_Leap = QAction("endLeap", self)
        self.end_Leap.triggered.connect(self.endLeap)
        self.end_Leap.setEnabled(False)

        self.active_Point = QAction("active", self)
        self.active_Point.triggered.connect(self.activePointing)
        self.active_Point.setEnabled(False)

        self.negative_Point = QAction("negative", self)
        self.negative_Point.triggered.connect(self.negativePointing)
        self.negative_Point.setEnabled(False)

        self.firstSeparator = QAction(self)
        self.firstSeparator.setSeparator(True)

        self.secondSeparator = QAction(self)
        self.secondSeparator.setSeparator(True)

    def setupMenuBar(self):
        self.leapMenu = self.menuBar().addMenu("&LeapMotion")
        self.leapMenu.addAction(self.start_Leap)
        self.leapMenu.addAction(self.end_Leap)

        self.pointMode = self.leapMenu.addMenu("&PointMode")
        self.pointMode.addAction(self.active_Point)
        self.pointMode.addAction(self.negative_Point)
        self.pointMode.setEnabled(False)

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
        self.overlayGraphics.hide()

    def activePointing(self):
        self.listener.setPointingMode(True)
        self.active_Point.setEnabled(False)
        self.negative_Point.setEnabled(True)
        self.pointingLabel.setText("Pointing mode: active")

    def negativePointing(self):
        self.listener.setPointingMode(False)
        self.negative_Point.setEnabled(False)
        self.active_Point.setEnabled(True)
        self.pointingLabel.setText("Pointing mode: negative")

    def setupContextMenu(self):
        # self.addAction((self.start_Leap))
        # self.addAction(self.end_Leap)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def changeLeap(self, toConnect):
        if toConnect:
            self.start_Leap.setEnabled(False)
            self.end_Leap.setEnabled(True)
            self.pointMode.setEnabled(True)
            self.active_Point.setEnabled(True)
            self.leapLabel.setText("LeapMotion: connecting")
            self.pointingLabel.setText("Pointing mode: negative")
        else:
            self.end_Leap.setEnabled(False)
            self.start_Leap.setEnabled(True)
            self.pointMode.setEnabled(False)
            self.negative_Point.setEnabled(False)
            self.leapLabel.setText("LeapMotion: disconnecting")
            self.pointingLabel.setText("")

    def getOverlayGrahics(self):
        return self.overlayGraphics

    # def resizeEvent(self, event):
    #     self.overlayGraphics.overlayScene.setSceneRect(self.overlayGraphics.rect())

    def closeEvent(self, event):
        self.controller.remove_listener(self.listener)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    sheet = SpreadSheet(50, 50)
    sheet.setWindowIcon(QIcon(QPixmap("images/target.png")))
    sheet.resize(1000, 600)
    sheet.show()
    sys.exit(app.exec_())

    # Remove the sample listener when done
    # controller.remove_listener(listener)