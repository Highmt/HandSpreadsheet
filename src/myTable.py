from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.spreadsheetdelegate import SpreadSheetDelegate
from src.spreadsheetitem import SpreadSheetItem


class myTable(QTableWidget):
    def __init__(self, rows, cols, parent):
        super(myTable, self).__init__(rows, cols, parent)
        self.setupHeader(cols)  # ヘッダーのアルファベット設定
        self.setItemPrototype(self.item(rows - 1, cols - 1))  # テーブルアイテムの初期化
        self.setItemDelegate(SpreadSheetDelegate(self))   #デリゲート
        self.setupContents()

    def setupHeader(self, cols):
        for c in range(cols):
            character = chr(ord('A') + c)
            self.setHorizontalHeaderItem(c, QTableWidgetItem(character))

    def setupContents(self):
        titleBackground = QColor(Qt.lightGray)
        titleFont = self.font()
        titleFont.setBold(True)
        # column 0
        self.setItem(0, 0, SpreadSheetItem("Item"))
        self.item(0, 0).setBackground(titleBackground)
        self.item(0, 0).setToolTip("This column shows the purchased item/service")
        self.item(0, 0).setFont(titleFont)
        self.setItem(1, 0, SpreadSheetItem("AirportBus"))
        self.setItem(2, 0, SpreadSheetItem("Flight (Munich)"))
        self.setItem(3, 0, SpreadSheetItem("Lunch"))
        self.setItem(4, 0, SpreadSheetItem("Flight (LA)"))
        self.setItem(5, 0, SpreadSheetItem("Taxi"))
        self.setItem(6, 0, SpreadSheetItem("Dinner"))
        self.setItem(7, 0, SpreadSheetItem("Hotel"))
        self.setItem(8, 0, SpreadSheetItem("Flight (Oslo)"))
        self.setItem(9, 0, SpreadSheetItem("Total:"))
        self.item(9, 0).setFont(titleFont)
        self.item(9, 0).setBackground(Qt.lightGray)
        # column 1
        self.setItem(0, 1, SpreadSheetItem("Date"))
        self.item(0, 1).setBackground(titleBackground)
        self.item(0, 1).setToolTip("This column shows the purchase date, double click to change")
        self.item(0, 1).setFont(titleFont)
        self.setItem(1, 1, SpreadSheetItem("15/6/2006"))
        self.setItem(2, 1, SpreadSheetItem("15/6/2006"))
        self.setItem(3, 1, SpreadSheetItem("15/6/2006"))
        self.setItem(4, 1, SpreadSheetItem("21/5/2006"))
        self.setItem(5, 1, SpreadSheetItem("16/6/2006"))
        self.setItem(6, 1, SpreadSheetItem("16/6/2006"))
        self.setItem(7, 1, SpreadSheetItem("16/6/2006"))
        self.setItem(8, 1, SpreadSheetItem("18/6/2006"))
        self.setItem(9, 1, SpreadSheetItem())
        self.item(9, 1).setBackground(Qt.lightGray)
        # column 2
        self.setItem(0, 2, SpreadSheetItem("Price"))
        self.item(0, 2).setBackground(titleBackground)
        self.item(0, 2).setToolTip("This column shows the price of the purchase")
        self.item(0, 2).setFont(titleFont)
        self.setItem(1, 2, SpreadSheetItem("150"))
        self.setItem(2, 2, SpreadSheetItem("2350"))
        self.setItem(3, 2, SpreadSheetItem("-14"))
        self.setItem(4, 2, SpreadSheetItem("980"))
        self.setItem(5, 2, SpreadSheetItem("5"))
        self.setItem(6, 2, SpreadSheetItem("120"))
        self.setItem(7, 2, SpreadSheetItem("300"))
        self.setItem(8, 2, SpreadSheetItem("1240"))
        self.setItem(9, 2, SpreadSheetItem())
        self.item(9, 2).setBackground(Qt.lightGray)
        # column 3
        self.setItem(0, 3, SpreadSheetItem("Currency"))
        self.item(0, 3).setBackground(titleBackground)
        self.item(0, 3).setToolTip("This column shows the currency")
        self.item(0, 3).setFont(titleFont)
        self.setItem(1, 3, SpreadSheetItem("NOK"))
        self.setItem(2, 3, SpreadSheetItem("NOK"))
        self.setItem(3, 3, SpreadSheetItem("EUR"))
        self.setItem(4, 3, SpreadSheetItem("EUR"))
        self.setItem(5, 3, SpreadSheetItem("USD"))
        self.setItem(6, 3, SpreadSheetItem("USD"))
        self.setItem(7, 3, SpreadSheetItem("USD"))
        self.setItem(8, 3, SpreadSheetItem("USD"))
        self.setItem(9, 3, SpreadSheetItem())
        self.item(9, 3).setBackground(Qt.lightGray)
        # column 4
        self.setItem(0, 4, SpreadSheetItem("Ex. Rate"))
        self.item(0, 4).setBackground(titleBackground)
        self.item(0, 4).setToolTip("This column shows the exchange rate to NOK")
        self.item(0, 4).setFont(titleFont)
        self.setItem(1, 4, SpreadSheetItem("1"))
        self.setItem(2, 4, SpreadSheetItem("1"))
        self.setItem(3, 4, SpreadSheetItem("8"))
        self.setItem(4, 4, SpreadSheetItem("8"))
        self.setItem(5, 4, SpreadSheetItem("7"))
        self.setItem(6, 4, SpreadSheetItem("7"))
        self.setItem(7, 4, SpreadSheetItem("7"))
        self.setItem(8, 4, SpreadSheetItem("7"))
        self.setItem(9, 4, SpreadSheetItem())
        self.item(9, 4).setBackground(Qt.lightGray)
        # column 5
        self.setItem(0, 5, SpreadSheetItem("NOK"))
        self.item(0, 5).setBackground(titleBackground)
        self.item(0, 5).setToolTip("This column shows the expenses in NOK")
        self.item(0, 5).setFont(titleFont)
        self.setItem(1, 5, SpreadSheetItem("* C2 E2"))
        self.setItem(2, 5, SpreadSheetItem("* C3 E3"))
        self.setItem(3, 5, SpreadSheetItem("* C4 E4"))
        self.setItem(4, 5, SpreadSheetItem("* C5 E5"))
        self.setItem(5, 5, SpreadSheetItem("* C6 E6"))
        self.setItem(6, 5, SpreadSheetItem("* C7 E7"))
        self.setItem(7, 5, SpreadSheetItem("* C8 E8"))
        self.setItem(8, 5, SpreadSheetItem("* C9 E9"))
        self.setItem(9, 5, SpreadSheetItem("sum F2 F9"))
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

    def insertCol(self):
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
