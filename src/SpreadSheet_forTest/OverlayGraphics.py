from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF, QRect, QRectF
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtWidgets import QGraphicsView, QGraphicsEllipseItem, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsSimpleTextItem

from res.SSEnum import DirectionEnum


class OverlayGraphics(QGraphicsView):
    def __init__(self):
        super(OverlayGraphics, self).__init__()
        self.setStyleSheet("background:transparent")  # ビューの背景透明化
        self.overlayScene = QGraphicsScene()
        self.setScene(self.overlayScene)
        self.overlayScene.setSceneRect(QRectF(self.rect()))
        self.createItem()

        self.luRect = QRect()
        self.rbRect = QRect()
        self.isSelected = False
        self.setTargetMode(False)
        self.hide()  # 初期状態は非表示

    def createItem(self):
        # 　ターゲットマーカの作成
        self.target_circle = QGraphicsEllipseItem(QtCore.QRectF(-10, -10, 20, 20))
        self.target_circle.setBrush(QBrush(Qt.red))
        self.target_circle.setPen(QPen(Qt.black))
        self.overlayScene.addItem(self.target_circle)
        self.setTargetMode(False)

        # モーダルの作成：モーダルはターゲット位置に追従する
        self.pop_rect = QGraphicsRectItem(QtCore.QRectF(0, 0, 100, 60), self.target_circle)
        self.pop_rect.setBrush(QBrush(Qt.gray))
        self.pop_rect.setPen(QPen(Qt.gray))
        self.pop_rect.setOpacity(0.8)  # 透明度を設定

        self.operate_text = QGraphicsSimpleTextItem("", self.pop_rect)
        self.operate_text.setScale(1.7)
        self.sub_operate_text = QGraphicsSimpleTextItem("", self.pop_rect)
        self.sub_operate_text.setScale(1.7)
        self.setTargetPos(400, 180, DirectionEnum.VERTICAL.value)

    # オーバレイヤのサイズが変わると呼び出される．シーンのサイズをビューの大きさに追従(-5 はマージン)
    def resizeEvent(self, event):
        self.overlayScene.setSceneRect(QRectF(0, 0, self.size().width() - 5, self.size().height() - 5))

    # ウィンドウ左上からの位置（画面位置からウインドウ左上の位置を引く）
    def setTargetPos(self, x_pos, y_pos, direction):
        self.target_circle.setPos(QPointF(x_pos, y_pos))
        self.setPopPos(direction)

    def setPopTextPos(self, text1, text2):
        lentext1 = len(text1)
        lentext2 = len(text2)
        if lentext2 == 0:
            self.operate_text.setPos((self.pop_rect.rect().size().width() / 2) - (lentext1 / 2 * 14), 15)
        else:
            self.operate_text.setPos((self.pop_rect.rect().size().width() / 2) - (lentext1 / 2 * 14), 5)
            self.sub_operate_text.setPos((self.pop_rect.rect().size().width() / 2) - (lentext2 / 2 * 14), 30)

    def setPopPos(self, direction):
        if direction == DirectionEnum.VERTICAL.value:
            # モーダルを右に表示しきれない場合に左に表示
            if self.target_circle.pos().x() > self.overlayScene.width() - self.pop_rect.rect().size().width() * 1.5:
                self.pop_rect.setPos(-self.pop_rect.rect().size().width() * 1.5,
                                     -self.pop_rect.rect().size().height() / 2)
            else:  # 右に表示
                self.pop_rect.setPos(self.pop_rect.rect().size().width() / 2,
                                     -self.pop_rect.rect().size().height() / 2)

        else:
            # モーダルを下に表示しきれない場合に上に表示
            if self.target_circle.pos().y() > self.overlayScene.height() - self.pop_rect.rect().size().height() * 1.5:
                self.pop_rect.setPos(-self.pop_rect.rect().size().width() / 2,
                                     -self.pop_rect.rect().size().height() * 1.5)
            else:  # 下に表示
                self.pop_rect.setPos(-self.pop_rect.rect().size().width() / 2,
                                     self.pop_rect.rect().size().height() / 2)

    def setTargetMode(self, active):
        self.targetMode = active
        if active:
            self.target_circle.setRect(-10, -10, 20, 20)
        else:  # ターゲットを非表示にする
            self.target_circle.setRect(0, 0, 0, 0)

    # def targetVisible(self, visible):
    #     if visible:
    #         self.target_circle.setRect(-10, -10, 20, 20)
    #     else:
    #         self.target_circle.setRect(0, 0, 0, 0)

    def feedbackShow(self, text1, text2, direction):
        if self.isSelected:
            self.operate_text.setText(text1)
            self.sub_operate_text.setText(text2)
            # ターゲットモードがアクティブでないとき，ターゲットマーカの位置は選択セルに依存
            if not self.targetMode:
                if direction == DirectionEnum.HORIZON.value:
                    x_pos = (self.luRect.left() + self.rbRect.right()) / 2 + 20
                    y_pos = self.rbRect.bottom() - self.rbRect.height() / 2 + 20
                else:
                    x_pos = self.rbRect.right() - self.rbRect.width() / 2 + 20
                    y_pos = (self.luRect.top() + self.rbRect.bottom()) / 2 + 20

                self.setTargetPos(x_pos, y_pos, direction)
                self.setPopTextPos(text1, text2)
            self.show()
