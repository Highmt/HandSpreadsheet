from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsView, QGraphicsEllipseItem, QGraphicsScene


class OverlayGraphics(QGraphicsView):
    def __init__(self):
        super(OverlayGraphics, self).__init__()
        self.setStyleSheet("background:transparent")
        self.overlayScene = QGraphicsScene()
        self.createItem()
        self.setScene(self.overlayScene)

    def createItem(self):
        #　ターゲットサークルの作成
        self.target_circle = QGraphicsEllipseItem(QtCore.QRectF(50, 50, 20, 20))
        self.target_circle.setBrush(QBrush(Qt.red))
        self.target_circle.setPen(QPen(Qt.black))
        self.overlayScene.addItem(self.target_circle)

        #　TODO フィードバックモーダルの作成


    def setTargetPos(self, x_pos, y_pos):
        self.target_circle.setPos(QPointF(x_pos, y_pos))

    def test(self):
        print("testtest")