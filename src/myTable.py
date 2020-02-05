from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.SSEnum import ActionEnum
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
        self.item(9, 0).setBackground(Qt.lightGray)
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
        self.item(9, 1).setBackground(Qt.lightGray)
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
        self.item(8, 2).setText("-20000")
        self.item(9, 2).setText("100000")
        self.item(10, 2).setText("5000")
        self.item(10, 2).setBackground(Qt.lightGray)
        # column 3
        self.item(0, 3).setText("形状済")
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
        self.item(9, 3).setBackground(Qt.lightGray)
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
        self.item(9, 4).setBackground(Qt.lightGray)


    def insertCell(self, d):
        #TODO　セル挿入関数
        pass

    def deleteCell(self, d):
        #TODO　セル削除関数
        pass

    def sortCells(self, d):
        #TODO　昇順ソート関数
        # TODO　降順ソート関数
        # self.sortByColumn()
        # self.sortItems()
        pass

    def copyCell(self):
        #TODO　コピー関数
        pass

    def cutCells(self):
        #TODO　カット関数
        pass

    def pasteCells(self):
        # TODO　ペースト関数
        pass

    def actionOperate(self, act, direction):
        if act == ActionEnum.INSERT.value:
            self.insertCell(direction)
            self.parent().statusBar().showMessage("insert", 1000)

        elif act == ActionEnum.DELETE.value:
            self.deleteCell(direction)
            self.parent().statusBar().showMessage("delete", 1000)

        elif act == ActionEnum.SORT.value:
            self.sortCell(direction)
            self.parent().statusBar().showMessage("sort", 1000)

        elif act == ActionEnum.COPY.value:
            self.copyCells()
            self.parent().statusBar().showMessage("copy", 1000)

        elif act == ActionEnum.CUT.value:
            self.cutCells()
            self.parent().statusBar().showMessage("cut", 1000)

        else:
            self.pasteCells()
            self.parent().statusBar().showMessage("paste", 1000)


    def getItemCoordinate(self):
        itemList = self.selectedItems()
        if itemList:
            return self.visualItemRect(itemList[0]), self.visualItemRect(itemList[-1])
            # self.first_item = itemList[0]
            # self.last_item = itemList[-1]



