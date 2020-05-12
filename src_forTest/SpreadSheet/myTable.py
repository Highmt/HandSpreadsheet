import random

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange, QMenu, QAction

from res.SSEnum import ActionEnum, DirectionEnum
from src_forTest.SpreadSheet.spreadsheetdelegate import SpreadSheetDelegate
from src_forTest.SpreadSheet.spreadsheetitem import SpreadSheetItem


class myTable(QTableWidget):
    def __init__(self, rows, cols, parent):
        super(myTable, self).__init__(rows, cols, parent)
        self.num_col = cols
        self.num_row = rows
        self.setupHeader(cols)  # ヘッダーのアルファベット設定
        self.setItemPrototype(self.item(rows - 1, cols - 1))  # テーブルアイテムの初期化
        self.setItemDelegate(SpreadSheetDelegate(self))   # デリゲート
        self.initContents()
        # self.setupContents()
        #
        self.clipTable = QTableWidget(rows, cols, None)  # コピー，カットのための仮装テーブル
        self.clipRanges = QTableWidgetSelectionRange()  # コピー，カットしたセルの領域情報
        self.verticalHeader().setDefaultSectionSize(60)
        self.horizontalHeader().setDefaultSectionSize(120)



    def setupHeader(self, cols):
        for c in range(cols):
            character = chr(ord('A') + c)
            self.setHorizontalHeaderItem(c, QTableWidgetItem(character))

    def initContents(self):
        for i in range(0, self.num_row):
            for j in range(0, self.num_col):
                self.setItem(i, j, SpreadSheetItem())

    def setupContents(self):
        titleBackground = QColor(Qt.lightGray)
        titleFont = self.font()
        titleFont.setBold(True)
        # column 0
        self.item(0, 0).setText("項目")
        self.item(0, 0).setBackground(titleBackground)
        # self.item(0, 0).setToolTip("This column shows the purchased item/service")
        self.item(0, 0).setFont(titleFont)
        self.item(1, 0).setText("家賃")
        self.item(2, 0).setText("食費")
        self.item(3, 0).setText("水道")
        self.item(4, 0).setText("電気")
        self.item(5, 0).setText("ガス")
        self.item(6, 0).setText("交通費")
        self.item(7, 0).setText("娯楽")
        self.item(8, 0).setText("給料")
        self.item(9, 0).setText("Total:")
        self.item(9, 0).setFont(titleFont)
        # self.item(9, 0).setBackground(Qt.lightGray)
        # column 1
        self.item(0, 1).setText("日付")
        self.item(0, 1).setBackground(titleBackground)
        # self.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
        self.item(0, 1).setFont(titleFont)
        self.item(1, 1).setText("2020/2/14")
        self.item(2, 1).setText("2020/2/14")
        self.item(3, 1).setText("2020/2/1")
        self.item(4, 1).setText("2020/2/1")
        self.item(5, 1).setText("2020/2/1")
        self.item(6, 1).setText("2020/2/1")
        self.item(7, 1).setText("2020/2/20")
        self.item(8, 1).setText("2020/2/20")
        self.setItem(9, 1, SpreadSheetItem())
        # self.item(9, 1).setBackground(Qt.lightGray)
        # column 2
        self.item(0, 2).setText("金額")
        self.item(0, 2).setBackground(titleBackground)
        # self.item(0, 2).setToolTip("This column shows the price of the purchase")
        self.item(0, 2).setFont(titleFont)
        self.item(1, 2).setText("-45000")
        self.item(2, 2).setText("-20000")
        self.item(3, 2).setText("-4000")
        self.item(4, 2).setText("-3000")
        self.item(5, 2).setText("-5500")
        self.item(6, 2).setText("-4000")
        self.item(7, 2).setText("-20000")
        self.item(8, 2).setText("100000")
        self.item(9, 2).setText("5000")
        # self.item(9, 2).setBackground(Qt.lightGray)
        # column 3
        self.item(0, 3).setText("計上済")
        self.item(0, 3).setBackground(titleBackground)
        self.item(0, 3).setToolTip("This column shows the currency")
        self.item(0, 3).setFont(titleFont)
        self.item(1, 3).setText("○")
        self.item(2, 3).setText("○")
        self.item(3, 3).setText("○")
        self.item(4, 3).setText("○")
        self.item(5, 3).setText("○")
        self.item(6, 3).setText("○")
        self.item(7, 3).setText("")
        self.item(8, 3).setText("○")
        # self.item(9, 3).setBackground(Qt.lightGray)
        # column 4
        self.item(0, 4).setText("備考")
        self.item(0, 4).setBackground(titleBackground)
        self.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        self.item(0, 4).setFont(titleFont)
        self.item(1, 4).setText("")
        self.item(2, 4).setText("")
        self.item(3, 4).setText("")
        self.item(4, 4).setText("")
        self.item(5, 4).setText("")
        self.item(6, 4).setText("")
        self.item(7, 4).setText("")
        self.item(8, 4).setText("先月より多い")
        # self.item(9, 4).setBackground(Qt.lightGray)


    def insertCell(self, d):
        selectrange = self.selectedRanges()[0]
        if d == DirectionEnum.HORIZON.value:
            for i in range(selectrange.topRow(), selectrange.bottomRow()+1):

                for j in range(self.columnCount()-1, selectrange.rightColumn(), -1):
                    temp = self.takeItem(i, j-selectrange.columnCount())
                    self.setItem(i, j, temp)

                for j in range(selectrange.leftColumn(), selectrange.rightColumn() + 1):
                    self.setItem(i, j, SpreadSheetItem())
                    self.item(i, j).setBackground(Qt.red)
        else:
            for j in range(selectrange.leftColumn(), selectrange.rightColumn()+1):

                for i in range(self.rowCount()-1, selectrange.bottomRow(), -1):
                    temp = self.takeItem(i - selectrange.rowCount(), j)
                    self.setItem(i, j, temp)
                for i in range(selectrange.topRow(), selectrange.bottomRow() + 1):
                    self.setItem(i, j, SpreadSheetItem())
                    self.item(i, j).setBackground(Qt.red)


    def deleteCell(self, d):
        selectrange = self.selectedRanges()[0]
        if d == DirectionEnum.HORIZON.value:
            for i in range(selectrange.topRow(), selectrange.bottomRow()+1):

                for j in range(selectrange.leftColumn(), self.columnCount() - selectrange.columnCount()):
                    temp = self.takeItem(i, j + selectrange.columnCount())
                    self.setItem(i, j, temp)
                for j in range(self.columnCount() - selectrange.columnCount(), self.columnCount()):
                    self.setItem(i, j, SpreadSheetItem())

        else:
            for j in range(selectrange.leftColumn(), selectrange.rightColumn()+1):

                for i in range(selectrange.topRow(), self.rowCount() - selectrange.rowCount()):
                    temp = self.takeItem(i + selectrange.rowCount(), j)
                    self.setItem(i, j, temp)
                for i in range(self.rowCount() - selectrange.rowCount(), self.rowCount()):
                    self.setItem(i, j, SpreadSheetItem())

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
                self.setItem(i, j, temp)

    def copyCells(self):
        self.clipRanges = self.selectedRanges()[0]
        for i in range(self.clipRanges.topRow(), self.clipRanges.bottomRow()+1):
            for j in range(self.clipRanges.leftColumn(), self.clipRanges.rightColumn()+1):
                temp = self.item(i, j).clone()
                self.clipTable.setItem(i, j, temp)


    def cutCells(self):
        self.clipRanges = self.selectedRanges()[0]
        for i in range(self.clipRanges.topRow(), self.clipRanges.bottomRow()+1):
            for j in range(self.clipRanges.leftColumn(), self.clipRanges.rightColumn()+1):
                temp = self.takeItem(i, j)
                self.clipTable.setItem(i, j, temp)
                self.setItem(i, j, SpreadSheetItem())



    def pasteCells(self):
        selectrange = self.selectedRanges()[0]
        for i in range(0, self.clipRanges.rowCount()):
            for j in range(0, self.clipRanges.columnCount()):
                temp = self.clipTable.item(self.clipRanges.topRow() + i, self.clipRanges.leftColumn() + j).clone()
                self.setItem(selectrange.topRow() + i, selectrange.leftColumn() + j, temp)



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


    def getItemCoordinate(self):
        itemList = self.selectedItems()
        # self.cutCells()
        if itemList:
            return self.visualItemRect(itemList[0]), self.visualItemRect(itemList[-1])
            # self.first_item = itemList[0]
            # self.last_item = itemList[-1]

    def setRandomCellColor(self):
        self.target_top = random.randint(1, self.columnCount()-4)
        self.target_left = random.randint(1, self.rowCount()-4)
        self.target_bottom = self.target_top + random.randint(1, 3)
        self.target_right = self.target_left + random.randint(1, 3)
        for i in range(self.target_top, self.target_bottom):
            for j in range(self.target_left, self.target_right):
                self.item(i, j).setBackground(Qt.blue)

    def resetRandomCellColor(self):
        for i in range(self.target_top, self.target_bottom):
            for j in range(self.target_left, self.target_right):
                self.item(i, j).setBackground(Qt.white)

