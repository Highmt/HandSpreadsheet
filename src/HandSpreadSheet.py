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
from PyQt5.QtCore import QDate, QPoint, Qt, QPointF
from PyQt5.QtGui import QColor, QIcon, QKeySequence, QPainter, QPixmap, QPen, QBrush, QImage, QPalette
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QColorDialog,
                             QComboBox, QDialog, QFontDialog, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QToolBar, QVBoxLayout, QGraphicsView, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsEllipseItem)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

from src.DrawTable import DrawTable
from src.LeapMotion import Leap
from src.HandSpreadSheetLeap import handListener
from src.study.spreadsheetdelegate import SpreadSheetDelegate
from src.study.spreadsheetitem import SpreadSheetItem
from src.study.printview import PrintView
from src.study.util import decode_pos, encode_pos


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
        self.table = QTableWidget(rows, cols, self)  # テーブルウィジットの初期化
        # ヘッダーのアルファベット設定
        for c in range(cols):
            character = chr(ord('A') + c)
            self.table.setHorizontalHeaderItem(c, QTableWidgetItem(character))

        self.table.setItemPrototype(self.table.item(rows - 1, cols - 1))  # テーブルアイテムの初期化
        self.table.setItemDelegate(SpreadSheetDelegate(self))   #デリゲート
        self.createActions()   # アクションの追加
        self.updateColor(0)
        self.setupMenuBar()
        self.setupContents()
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

        # Create a sample listener and controller
        self.listener = handListener(self)
        self.controller = Leap.Controller()

        self.overlayLayout = QHBoxLayout(self.table)
        self.overlayLayout.setContentsMargins(0, 0, 0, 0)

        # self.overlayWidget = DrawTable()

        self.overlayWidget = QGraphicsView()
        self.overlayWidget.setStyleSheet("background:transparent")

        self._ellipse_item = QGraphicsEllipseItem(QtCore.QRectF(50, 50, 20, 20))
        self._ellipse_item.setBrush(QBrush(Qt.red))
        self._ellipse_item.setPen(QPen(Qt.black))
        self.scene = QGraphicsScene()
        self.scene.addItem(self._ellipse_item)
        self.overlayWidget.setScene(self.scene)
        self.overlayLayout.addWidget(self.overlayWidget)
        self._ellipse_item.setPos(QPointF(80.0, 80.0))   #　ターゲットの位置変更可能
        self.overlayWidget.hide()

    def createStatusBar(self):
        self.leapLabel = QLabel("LeapMotion is disconnecting")
        self.leapLabel.setAlignment(Qt.AlignLeft)
        self.leapLabel.setMinimumSize(self.leapLabel.sizeHint())

        self.statusBar().addWidget(self.leapLabel)


    def createActions(self):
        self.start_Leap = QAction("startLeap", self)
        self.start_Leap.triggered.connect(self.startLeap)

        self.end_Leap = QAction("endLeap", self)
        self.end_Leap.triggered.connect(self.endLeap)
        self.end_Leap.setEnabled(False)


        self.firstSeparator = QAction(self)
        self.firstSeparator.setSeparator(True)

        self.secondSeparator = QAction(self)
        self.secondSeparator.setSeparator(True)

    def setupMenuBar(self):
        self.leapMenu = self.menuBar().addMenu("&LeapMotion")
        self.leapMenu.addAction(self.start_Leap)
        self.leapMenu.addAction(self.end_Leap)

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
        self._ellipse_item.setPos(QPointF(20.0, 20.0))


    def endLeap(self):
        self.controller.remove_listener(self.listener)
        self.overlayWidget.hide()


    def setupContextMenu(self):
        # self.addAction((self.start_Leap))
        # self.addAction(self.end_Leap)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def setupContents(self):
        titleBackground = QColor(Qt.lightGray)
        titleFont = self.table.font()
        titleFont.setBold(True)
        # column 0
        self.table.setItem(0, 0, SpreadSheetItem("Item"))
        self.table.item(0, 0).setBackground(titleBackground)
        self.table.item(0, 0).setToolTip("This column shows the purchased item/service")
        self.table.item(0, 0).setFont(titleFont)
        self.table.setItem(1, 0, SpreadSheetItem("AirportBus"))
        self.table.setItem(2, 0, SpreadSheetItem("Flight (Munich)"))
        self.table.setItem(3, 0, SpreadSheetItem("Lunch"))
        self.table.setItem(4, 0, SpreadSheetItem("Flight (LA)"))
        self.table.setItem(5, 0, SpreadSheetItem("Taxi"))
        self.table.setItem(6, 0, SpreadSheetItem("Dinner"))
        self.table.setItem(7, 0, SpreadSheetItem("Hotel"))
        self.table.setItem(8, 0, SpreadSheetItem("Flight (Oslo)"))
        self.table.setItem(9, 0, SpreadSheetItem("Total:"))
        self.table.item(9, 0).setFont(titleFont)
        self.table.item(9, 0).setBackground(Qt.lightGray)
        # column 1
        self.table.setItem(0, 1, SpreadSheetItem("Date"))
        self.table.item(0, 1).setBackground(titleBackground)
        self.table.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
        self.table.item(0, 1).setFont(titleFont)
        self.table.setItem(1, 1, SpreadSheetItem("15/6/2006"))
        self.table.setItem(2, 1, SpreadSheetItem("15/6/2006"))
        self.table.setItem(3, 1, SpreadSheetItem("15/6/2006"))
        self.table.setItem(4, 1, SpreadSheetItem("21/5/2006"))
        self.table.setItem(5, 1, SpreadSheetItem("16/6/2006"))
        self.table.setItem(6, 1, SpreadSheetItem("16/6/2006"))
        self.table.setItem(7, 1, SpreadSheetItem("16/6/2006"))
        self.table.setItem(8, 1, SpreadSheetItem("18/6/2006"))
        self.table.setItem(9, 1, SpreadSheetItem())
        self.table.item(9, 1).setBackground(Qt.lightGray)
        # column 2
        self.table.setItem(0, 2, SpreadSheetItem("Price"))
        self.table.item(0, 2).setBackground(titleBackground)
        self.table.item(0, 2).setToolTip("This column shows the price of the purchase")
        self.table.item(0, 2).setFont(titleFont)
        self.table.setItem(1, 2, SpreadSheetItem("150"))
        self.table.setItem(2, 2, SpreadSheetItem("2350"))
        self.table.setItem(3, 2, SpreadSheetItem("-14"))
        self.table.setItem(4, 2, SpreadSheetItem("980"))
        self.table.setItem(5, 2, SpreadSheetItem("5"))
        self.table.setItem(6, 2, SpreadSheetItem("120"))
        self.table.setItem(7, 2, SpreadSheetItem("300"))
        self.table.setItem(8, 2, SpreadSheetItem("1240"))
        self.table.setItem(9, 2, SpreadSheetItem())
        self.table.item(9, 2).setBackground(Qt.lightGray)
        # column 3
        self.table.setItem(0, 3, SpreadSheetItem("Currency"))
        self.table.item(0, 3).setBackground(titleBackground)
        self.table.item(0, 3).setToolTip("This column shows the currency")
        self.table.item(0, 3).setFont(titleFont)
        self.table.setItem(1, 3, SpreadSheetItem("NOK"))
        self.table.setItem(2, 3, SpreadSheetItem("NOK"))
        self.table.setItem(3, 3, SpreadSheetItem("EUR"))
        self.table.setItem(4, 3, SpreadSheetItem("EUR"))
        self.table.setItem(5, 3, SpreadSheetItem("USD"))
        self.table.setItem(6, 3, SpreadSheetItem("USD"))
        self.table.setItem(7, 3, SpreadSheetItem("USD"))
        self.table.setItem(8, 3, SpreadSheetItem("USD"))
        self.table.setItem(9, 3, SpreadSheetItem())
        self.table.item(9, 3).setBackground(Qt.lightGray)
        # column 4
        self.table.setItem(0, 4, SpreadSheetItem("Ex. Rate"))
        self.table.item(0, 4).setBackground(titleBackground)
        self.table.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        self.table.item(0, 4).setFont(titleFont)
        self.table.setItem(1, 4, SpreadSheetItem("1"))
        self.table.setItem(2, 4, SpreadSheetItem("1"))
        self.table.setItem(3, 4, SpreadSheetItem("8"))
        self.table.setItem(4, 4, SpreadSheetItem("8"))
        self.table.setItem(5, 4, SpreadSheetItem("7"))
        self.table.setItem(6, 4, SpreadSheetItem("7"))
        self.table.setItem(7, 4, SpreadSheetItem("7"))
        self.table.setItem(8, 4, SpreadSheetItem("7"))
        self.table.setItem(9, 4, SpreadSheetItem())
        self.table.item(9, 4).setBackground(Qt.lightGray)
        # column 5
        self.table.setItem(0, 5, SpreadSheetItem("NOK"))
        self.table.item(0, 5).setBackground(titleBackground)
        self.table.item(0, 5).setToolTip("This column shows the expenses in NOK")
        self.table.item(0, 5).setFont(titleFont)
        self.table.setItem(1, 5, SpreadSheetItem("* C2 E2"))
        self.table.setItem(2, 5, SpreadSheetItem("* C3 E3"))
        self.table.setItem(3, 5, SpreadSheetItem("* C4 E4"))
        self.table.setItem(4, 5, SpreadSheetItem("* C5 E5"))
        self.table.setItem(5, 5, SpreadSheetItem("* C6 E6"))
        self.table.setItem(6, 5, SpreadSheetItem("* C7 E7"))
        self.table.setItem(7, 5, SpreadSheetItem("* C8 E8"))
        self.table.setItem(8, 5, SpreadSheetItem("* C9 E9"))
        self.table.setItem(9, 5, SpreadSheetItem("sum F2 F9"))
        self.table.item(9, 5).setBackground(Qt.lightGray)

    def changeLeap(self, isConnect):
        if isConnect:
            self.start_Leap.setEnabled(False)
            self.end_Leap.setEnabled(True)
            self.leapLabel.setText("LeapMotion is connecting")
        else:
            self.end_Leap.setEnabled(False)
            self.start_Leap.setEnabled(True)
            self.leapLabel.setText("LeapMotion is disconnecting")

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    sheet = SpreadSheet(50, 60)
    sheet.setWindowIcon(QIcon(QPixmap("images/interview.png")))
    sheet.resize(1000, 600)
    sheet.show()
    sys.exit(app.exec_())

    # Remove the sample listener when done
    # controller.remove_listener(listener)