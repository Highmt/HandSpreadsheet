from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF, QRect, QRectF
from PyQt5.QtGui import QBrush, QPen, QFont, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsEllipseItem, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsSimpleTextItem, QGraphicsTextItem

from src.SSEnum import SSEnum


class OverlayGraphics(QGraphicsView):
    def __init__(self):
        super(OverlayGraphics, self).__init__()
        self.setStyleSheet("background:transparent")  # ビューの背景透明化
        self.overlayScene = QGraphicsScene()
        self.setScene(self.overlayScene)
        self.overlayScene.setSceneRect(QRectF(self.rect()))
        self.modal_pos = SSEnum.VERTICAL.value
        self.createItem()


    def createItem(self):
        #　ターゲットマーカの作成
        self.target_circle = QGraphicsEllipseItem(QtCore.QRectF(-10, -10, 20, 20))
        self.target_circle.setBrush(QBrush(Qt.red))
        self.target_circle.setPen(QPen(Qt.black))
        self.overlayScene.addItem(self.target_circle)
        self.targetVisible(False)
        self.modal_rect = QGraphicsRectItem(QtCore.QRectF(0, 0, 100, 60), self.target_circle)
        self.modal_rect.setBrush(QBrush(Qt.gray))
        self.modal_rect.setPen(QPen(Qt.gray))
        self.modal_rect.setOpacity(0.8)  # 透明度を設定
        self.operate_text = QGraphicsSimpleTextItem("削除", self.modal_rect)
        self.operate_text.setPos(30, 5)
        self.operate_text.setScale(1.7)
        self.operate_option = QGraphicsSimpleTextItem("上詰め", self.modal_rect)
        self.operate_option.setPos(32.5, 40)
        self.setTargetPos(440, 200)
        print(self.overlayScene.sceneRect())

    # オーバレイヤのサイズが変わると呼び出される．シーンのサイズをビューの大きさに固定(-5 はマージン)
    def resizeEvent(self, event):
        self.overlayScene.setSceneRect(QRectF(0, 0, self.size().width() - 5, self.size().height() - 5))

    def setTargetPos(self, x_pos, y_pos):  # ウィンドウ左上からの位置　（画面一からウインドウ左上の一を引く）
        self.target_circle.setPos(QPointF(x_pos, y_pos))
        self.setModalPos()

    def setModalPos(self):
        if self.modal_pos == SSEnum.HORIZON:
            # モーダルを右に表示しきれない場合に左に表示
            if self.target_circle.pos().x() > self.overlayScene.width() - self.modal_rect.rect().size().width() * 1.5:
                self.modal_rect.setPos(-self.modal_rect.rect().size().width() * 1.5,
                                       -self.modal_rect.rect().size().height() / 2)
            else:  # 右に表示
                self.modal_rect.setPos(self.modal_rect.rect().size().width() / 2,
                                       -self.modal_rect.rect().size().height() / 2)

        else:
            # モーダルを下に表示しきれない場合に上に表示
            if self.target_circle.pos().y() > self.overlayScene.height() - self.modal_rect.rect().size().height() * 1.5:
                self.modal_rect.setPos(-self.modal_rect.rect().size().width() / 2,
                                       -self.modal_rect.rect().size().height() * 1.5)
            else:  # 下に表示
                self.modal_rect.setPos(-self.modal_rect.rect().size().width() / 2,
                                       self.modal_rect.rect().size().height() / 2)

    def targetVisible(self, bool):
        if bool:
            self.target_circle.setRect(-10, -10, 20, 20)
        else:
            self.target_circle.setRect(0, 0, 0, 0)

    def feedbackVisible(self, text, option):
        self.operate_text.setText(text)
        self.operate_option.setText(option)
        self.show()
