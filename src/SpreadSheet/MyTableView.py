from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import Qt

class MyTableView(QTableView):
    def __init__(self):
        super(MyTableView, self).__init__()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def print_(self, printer):
        self.resize(printer.width(), printer.height())
        self.render(printer)

