from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QImage
from PyQt5.QtWidgets import QTableWidget, QLayout, QLabel
from PyQt5.uic.properties import QtGui


class DrawTable(QLabel):
    def __init__(self):
        super(DrawTable, self).__init__()
        self.img = QImage(500, 500, QImage.Format_ARGB32)

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.painter.drawImage(0, 0, self.img)
