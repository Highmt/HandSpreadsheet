import random

import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QMenu, QAction, \
    QAbstractItemView

from res.SSEnum import ActionEnum, DirectionEnum, TestTaskEnum
from src.Utility.spreadsheetdelegate import SpreadSheetDelegate
from src.Utility.spreadsheetitem import SpreadSheetItem

cell_height = 60
cell_width = 120

class myTable(QTableWidget):
    def __init__(self, rows, cols, parent):
        super(myTable, self).__init__(rows, cols, parent)
        self.num_col = cols
        self.num_row = rows
        self.setupHeader(cols)  # ヘッダーのアルファベット設定
        self.setItemPrototype(self.item(rows - 1, cols - 1))  # テーブルアイテムの初期化
        self.setItemDelegate(SpreadSheetDelegate(self))  # デリゲート

        self.initContents()
        self.setupContents()

        self.clipTable = QTableWidget(rows, cols, None)  # コピー，カットのための仮装テーブル
        self.clipRanges = QTableWidgetSelectionRange()  # コピー，カットしたセルの領域情報
        self.verticalHeader().setDefaultSectionSize(cell_height)
        self.horizontalHeader().setDefaultSectionSize(cell_width)

        # for test
        self.pre_target = QRect(0, 0, 0, 0)
        self.target_top = 0
        self.target_left = 0
        self.target_height = 0
        self.target_width = 0

    def setupHeader(self, cols):
        for c in range(cols):
            character = chr(ord('A') + c)
            self.setHorizontalHeaderItem(c, QTableWidgetItem(character))

    def initContents(self):
        for i in range(0, self.num_row):
            for j in range(0, self.num_col):
                self.setItem(i, j, SpreadSheetItem())

    def loadCSV(self):
        read_data = pd.read_csv('../../res/tabledata.csv', header=None)
        for i in range(min(len(read_data), self.num_row)):
            for j in range(min(len(read_data.columns), self.num_col)):
                self.item(i, j).setText(read_data.iat[i, j])
                if i == 0:
                    self.item(i, j).setBackground(QColor(Qt.lightGray))

    def setupContents(self):
        self.loadCSV()
        # titleBackground = QColor(Qt.lightGray)
        # titleFont = self.font()
        # titleFont.setBold(True)
        # # column 0
        # self.item(0, 0).setText("Item")
        # self.item(0, 0).setBackground(titleBackground)
        # # self.item(0, 0).setToolTip("This column shows the purchased item/service")
        # self.item(0, 0).setFont(titleFont)
        # self.item(1, 0).setText("Rent")
        # self.item(2, 0).setText("Food")
        # self.item(3, 0).setText("Water")
        # self.item(4, 0).setText("Electricity")
        # self.item(5, 0).setText("Gas")
        # self.item(6, 0).setText("Travel")
        # self.item(7, 0).setText("Amusement")
        # self.item(8, 0).setText("Salary")
        # self.item(9, 0).setText("Total")
        # self.item(9, 0).setFont(titleFont)
        # # self.item(9, 0).setBackground(Qt.lightGray)
        # # column 1
        # self.item(0, 1).setText("Date")
        # self.item(0, 1).setBackground(titleBackground)
        # # self.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
        # self.item(0, 1).setFont(titleFont)
        # self.item(1, 1).setText("2020/2/14")
        # self.item(2, 1).setText("2020/2/14")
        # self.item(3, 1).setText("2020/2/1")
        # self.item(4, 1).setText("2020/2/1")
        # self.item(5, 1).setText("2020/2/1")
        # self.item(6, 1).setText("2020/2/1")
        # self.item(7, 1).setText("2020/2/20")
        # self.item(8, 1).setText("2020/2/20")
        # # self.item(9, 1).setBackground(Qt.lightGray)
        # # column 2
        # self.item(0, 2).setText("money")
        # self.item(0, 2).setBackground(titleBackground)
        # # self.item(0, 2).setToolTip("This column shows the price of the purchase")
        # self.item(0, 2).setFont(titleFont)
        # self.item(1, 2).setText("-45000")
        # self.item(2, 2).setText("-20000")
        # self.item(3, 2).setText("-4000")
        # self.item(4, 2).setText("-3000")
        # self.item(5, 2).setText("-5500")
        # self.item(6, 2).setText("-4000")
        # self.item(7, 2).setText("-20000")
        # self.item(8, 2).setText("100000")
        # self.item(9, 2).setText("5000")
        # # self.item(9, 2).setBackground(Qt.lightGray)
        # # column 3
        # self.item(0, 3).setText("allocated")
        # self.item(0, 3).setBackground(titleBackground)
        # self.item(0, 3).setToolTip("This column shows the currency")
        # self.item(0, 3).setFont(titleFont)
        # self.item(1, 3).setText("○")
        # self.item(2, 3).setText("○")
        # self.item(3, 3).setText("○")
        # self.item(4, 3).setText("○")
        # self.item(5, 3).setText("○")
        # self.item(6, 3).setText("○")
        # self.item(7, 3).setText("")
        # self.item(8, 3).setText("○")
        # # self.item(9, 3).setBackground(Qt.lightGray)
        # # column 4
        # self.item(0, 4).setText("note")
        # self.item(0, 4).setBackground(titleBackground)
        # self.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        # self.item(0, 4).setFont(titleFont)
        # self.item(1, 4).setText("")
        # self.item(2, 4).setText("")
        # self.item(3, 4).setText("")
        # self.item(4, 4).setText("")
        # self.item(5, 4).setText("")
        # self.item(6, 4).setText("")
        # self.item(7, 4).setText("")
        # self.item(8, 4).setText("Up from last month.")
        # # self.item(9, 4).setBackground(Qt.lightGray)

    def insertCell(self, d):
        selectrange = self.selectedRanges()[0]
        if d == DirectionEnum.HORIZON.value:
            for i in range(selectrange.topRow(), selectrange.bottomRow() + 1):

                for j in range(self.columnCount() - 1, selectrange.rightColumn(), -1):
                    temp = self.takeItem(i, j - selectrange.columnCount())
                    self.setItem(i, j, temp)

                for j in range(selectrange.leftColumn(), selectrange.rightColumn() + 1):
                    self.setItem(i, j, SpreadSheetItem())
                    # self.item(i, j).setBackground(Qt.red)
        else:
            for j in range(selectrange.leftColumn(), selectrange.rightColumn() + 1):

                for i in range(self.rowCount() - 1, selectrange.bottomRow(), -1):
                    temp = self.takeItem(i - selectrange.rowCount(), j)
                    self.setItem(i, j, temp)
                for i in range(selectrange.topRow(), selectrange.bottomRow() + 1):
                    self.setItem(i, j, SpreadSheetItem())
                    # self.item(i, j).setBackground(Qt.red)

    def deleteCell(self, d):
        selectrange = self.selectedRanges()[0]
        if d == DirectionEnum.HORIZON.value:
            for i in range(selectrange.topRow(), selectrange.bottomRow() + 1):

                for j in range(selectrange.leftColumn(), self.columnCount() - selectrange.columnCount()):
                    temp = self.takeItem(i, j + selectrange.columnCount())
                    self.setItem(i, j, temp)
                for j in range(self.columnCount() - selectrange.columnCount(), self.columnCount()):
                    self.setItem(i, j, SpreadSheetItem())

        else:
            for j in range(selectrange.leftColumn(), selectrange.rightColumn() + 1):

                for i in range(selectrange.topRow(), self.rowCount() - selectrange.rowCount()):
                    temp = self.takeItem(i + selectrange.rowCount(), j)
                    self.setItem(i, j, temp)
                for i in range(self.rowCount() - selectrange.rowCount(), self.rowCount()):
                    self.setItem(i, j, SpreadSheetItem())

    # TODO: 数値を認識する
    def sortCells(self, d):
        sortRanges = self.selectedRanges()[0]
        editTable = QTableWidget(sortRanges.rowCount(), sortRanges.columnCount())

        for i in range(sortRanges.topRow(), sortRanges.bottomRow() + 1):
            for j in range(sortRanges.leftColumn(), sortRanges.rightColumn() + 1):
                temp = self.item(i, j).clone()
                editTable.setItem(i - sortRanges.topRow(), j - sortRanges.leftColumn(), temp)


        if d == DirectionEnum.BACK.value:
            editTable.sortItems(0, Qt.AscendingOrder)
        else:
            editTable.sortItems(0, Qt.DescendingOrder)

        for i in range(sortRanges.topRow(), sortRanges.bottomRow() + 1):
            for j in range(sortRanges.leftColumn(), sortRanges.rightColumn() + 1):
                temp = editTable.takeItem(i - sortRanges.topRow(), j - sortRanges.leftColumn())
                self.item(i, j).setText(temp.text())

    def copyCells(self):
        self.clipRanges = self.selectedRanges()[0]
        for i in range(self.clipRanges.topRow(), self.clipRanges.bottomRow() + 1):
            for j in range(self.clipRanges.leftColumn(), self.clipRanges.rightColumn() + 1):
                temp = self.item(i, j).clone()
                self.clipTable.setItem(i, j, temp)

    def cutCells(self):
        self.clipRanges = self.selectedRanges()[0]
        for i in range(self.clipRanges.topRow(), self.clipRanges.bottomRow() + 1):
            for j in range(self.clipRanges.leftColumn(), self.clipRanges.rightColumn() + 1):
                temp = self.takeItem(i, j)
                self.clipTable.setItem(i, j, temp)
                self.setItem(i, j, SpreadSheetItem())
                print(self.clipTable.item(i, j).text())

    def pasteCells(self):
        selectrange = self.selectedRanges()[0]
        for i in range(0, self.clipRanges.rowCount()):
            for j in range(0, self.clipRanges.columnCount()):
                temp = self.clipTable.item(self.clipRanges.topRow() + i, self.clipRanges.leftColumn() + j).clone()
                self.item(selectrange.topRow() + i, selectrange.leftColumn() + j).setText(temp.text())

    def actionOperate(self, act, direction):
        if self.selectedItems():
            if act == ActionEnum.INSERT.value:
                self.insertCell(direction)
                self.parent().statusBar().showMessage("insert", 1000)

            elif act == ActionEnum.DELETE.value:
                self.deleteCell(direction)
                self.parent().statusBar().showMessage("delete", 1000)

            elif act == ActionEnum.SORT.value:
                self.sortCells(direction)
                self.parent().statusBar().showMessage("sort", 1000)

            elif act == ActionEnum.COPY.value:
                self.copyCells()
                self.parent().statusBar().showMessage("copy", 1000)

            elif act == ActionEnum.CUT.value:
                self.cutCells()
                self.parent().statusBar().showMessage("cut", 1000)

            else:
                if self.clipRanges is not None:
                    self.pasteCells()
                    self.parent().statusBar().showMessage("paste", 1000)

    def fixOperated(self, act, direction):
        if self.selectedItems():
            if act == ActionEnum.INSERT.value:
                self.insertCell(direction)

            elif act == ActionEnum.DELETE.value:
                self.deleteCell(direction)

            elif act == ActionEnum.SORT.value:
                self.sortCells(direction)

            elif act == ActionEnum.COPY.value:
                self.copyCells()

            elif act == ActionEnum.CUT.value:
                self.cutCells()

            else:
                if self.clipRanges is not None:
                    self.pasteCells()

    def getItemCoordinate(self):
        itemList = self.selectedItems()
        # self.cutCells()
        if itemList:
            return self.visualItemRect(itemList[0]), self.visualItemRect(itemList[-1])
            # self.first_item = itemList[0]
            # self.last_item = itemList[-1]

    def setRandomCellColor(self):
        self.setTargetLocation()

        for i in range(self.target_height):
            for j in range(self.target_width):
                self.item(self.target_top + i, self.target_left + j).setBackground(Qt.blue)
        self.pre_target = QRect(self.target_left, self.target_top, self.target_width, self.target_height)

    def setTargetLocation(self):
        while True:
            self.target_top = random.randint(1, self.num_row - 4)
            self.target_left = random.randint(1, self.num_col - 4)
            self.target_height = random.randint(1, 3)
            self.target_width = random.randint(1, 3)

            # 条件をクリアするまで繰り返し設定
            while self.target_width == 1 and self.target_height == 1:
                self.target_height = random.randint(1, 3)
                self.target_width = random.randint(1, 3)
            if self.target_top < self.pre_target.y() or \
                    self.target_left < self.pre_target.x() or \
                    self.target_height + self.target_top > self.pre_target.height() + self.pre_target.y() or \
                    self.target_width + self.target_left > self.pre_target.width() + self.pre_target.x():
                break

    def setGoalTable(self, act, direction):
        if act == TestTaskEnum.SORT.value:
            self.target_top = 1
            self.target_left = random.randint(1, self.num_col - 4)
            self.target_height = 8
            self.target_width = 1

        else:
            self.setTargetLocation()

        for i in range(self.target_height):
            for j in range(self.target_width):
                self.setCurrentCell(self.target_top + i, self.target_left + j)
        self.setRangeSelected(QTableWidgetSelectionRange(self.target_top,
                                                         self.target_left,
                                                         self.target_top + self.target_height - 1,
                                                         self.target_left + self.target_width - 1), True)
        self.fixOperated(act, direction)
        self.clearSelection()


    def resetRandomCellColor(self):
        for i in range(self.target_height):
            for j in range(self.target_width):
                self.item(self.target_top + i, self.target_left + j).setBackground(Qt.white)
