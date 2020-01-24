from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.spreadsheetdelegate import SpreadSheetDelegate
from src.spreadsheetitem import SpreadSheetItem


class myTable(QTableWidget):
    def __init__(self, rows, cols, parent):
        super(myTable, self).__init__(rows, cols, parent)
        self.num_col = cols
        self.num_row = rows
        self.setupHeader(cols)  # ヘッダーのアルファベット設定
        self.setItemPrototype(self.item(rows - 1, cols - 1))  # テーブルアイテムの初期化
        self.setItemDelegate(SpreadSheetDelegate(self))   #デリゲート
        self.initContents()
        self.setupContents()


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
        self.item(0, 0).setText("Item")
        self.item(0, 0).setBackground(titleBackground)
        self.item(0, 0).setToolTip("This column shows the purchased item/service")
        self.item(0, 0).setFont(titleFont)
        self.item(1, 0).setText("AirportBus")
        self.item(2, 0).setText("Flight (Munich)")
        self.item(3, 0).setText("Lunch")
        self.item(4, 0).setText("Flight (LA)")
        self.item(5, 0).setText("Taxi")
        self.item(6, 0).setText("Dinner")
        self.item(7, 0).setText("Hotel")
        self.item(8, 0).setText("Flight (Oslo)")
        self.item(9, 0).setText("Total:")
        self.item(9, 0).setFont(titleFont)
        self.item(9, 0).setBackground(Qt.lightGray)
        # column 1
        self.item(0, 1).setText("Date")
        self.item(0, 1).setBackground(titleBackground)
        self.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
        self.item(0, 1).setFont(titleFont)
        self.item(1, 1).setText("15/6/2006")
        self.item(2, 1).setText("15/6/2006")
        self.item(3, 1).setText("15/6/2006")
        self.item(4, 1).setText("21/5/2006")
        self.item(5, 1).setText("16/6/2006")
        self.item(6, 1).setText("16/6/2006")
        self.item(7, 1).setText("16/6/2006")
        self.item(8, 1).setText("18/6/2006")
        self.setItem(9, 1, SpreadSheetItem())
        self.item(9, 1).setBackground(Qt.lightGray)
        # column 2
        self.item(0, 2).setText("Price")
        self.item(0, 2).setBackground(titleBackground)
        self.item(0, 2).setToolTip("This column shows the price of the purchase")
        self.item(0, 2).setFont(titleFont)
        self.item(1, 2).setText("150")
        self.item(2, 2).setText("2350")
        self.item(3, 2).setText("-14")
        self.item(4, 2).setText("980")
        self.item(5, 2).setText("5")
        self.item(6, 2).setText("120")
        self.item(7, 2).setText("300")
        self.item(8, 2).setText("1240")
        self.setItem(9, 2, SpreadSheetItem())
        self.item(9, 2).setBackground(Qt.lightGray)
        # column 3
        self.item(0, 3).setText("Currency")
        self.item(0, 3).setBackground(titleBackground)
        self.item(0, 3).setToolTip("This column shows the currency")
        self.item(0, 3).setFont(titleFont)
        self.item(1, 3).setText("NOK")
        self.item(2, 3).setText("NOK")
        self.item(3, 3).setText("EUR")
        self.item(4, 3).setText("EUR")
        self.item(5, 3).setText("USD")
        self.item(6, 3).setText("USD")
        self.item(7, 3).setText("USD")
        self.item(8, 3).setText("USD")
        self.setItem(9, 3, SpreadSheetItem())
        self.item(9, 3).setBackground(Qt.lightGray)
        # column 4
        self.item(0, 4).setText("Ex. Rate")
        self.item(0, 4).setBackground(titleBackground)
        self.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        self.item(0, 4).setFont(titleFont)
        self.item(1, 4).setText("1")
        self.item(2, 4).setText("1")
        self.item(3, 4).setText("8")
        self.item(4, 4).setText("8")
        self.item(5, 4).setText("7")
        self.item(6, 4).setText("7")
        self.item(7, 4).setText("7")
        self.item(8, 4).setText("7")
        self.setItem(9, 4, SpreadSheetItem())
        self.item(9, 4).setBackground(Qt.lightGray)
        # column 5
        self.item(0, 5).setText("NOK")
        self.item(0, 5).setBackground(titleBackground)
        self.item(0, 5).setToolTip("This column shows the expenses in NOK")
        self.item(0, 5).setFont(titleFont)
        self.item(1, 5).setText("* C2 E2")
        self.item(2, 5).setText("* C3 E3")
        self.item(3, 5).setText("* C4 E4")
        self.item(4, 5).setText("* C5 E5")
        self.item(5, 5).setText("* C6 E6")
        self.item(6, 5).setText("* C7 E7")
        self.item(7, 5).setText("* C8 E8")
        self.item(8, 5).setText("* C9 E9")
        self.item(9, 5).setText("sum F2 F9")
        self.item(9, 5).setBackground(Qt.lightGray)

    def deleteCell(self):
        #TODO　セル削除関数
        pass

    def deleteRow(self):
        #TODO　行削除関数
        pass

    def deleteCol(self):
        #TODO　列削除関数
        pass

    def insertCell(self):
        #TODO　セル挿入関数
        pass

    def insertRow(self):
        #TODO　行挿入関数
        pass

    def insert(self):
        #TODO　列挿入関数
        pass

    def sortUp(self):
        #TODO　昇順ソート関数
        pass

    def sortDown(self):
        #TODO　降順ソート関数

        # self.sortByColumn()
        pass

    def copyCells(self):
        #TODO　コピー関数
        pass

    def cutCells(self):
        #TODO　カット関数
        pass

    def getItemCoordinate(self):
        itemList = self.selectedItems()
        if itemList:
            return itemList[0], itemList[-1]
            # self.first_item = itemList[0]
            # self.last_item = itemList[-1]



