from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidget


class myTable(QTableWidget):
    def __init__(self, rows, cols, parent):
        super(myTable, self).__init__(rows, cols, parent)


