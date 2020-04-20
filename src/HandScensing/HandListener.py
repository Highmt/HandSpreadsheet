import statistics
import sys
import pyautogui

from lib.LeapMotion.Leap import Listener, Vector, Finger
from src.HandScensing.Predictor import Predictor
from res.SSEnum import HandEnum, DirectionEnum, ActionEnum
from PyQt5 import QtCore

DIS_SIZE = pyautogui.size()
memorySize = 30

class HandListener(QtCore.QThread, Listener):
    show_feedback = QtCore.pyqtSignal()  # フィードバック非表示シグナル
    hide_feedback = QtCore.pyqtSignal()  # フィードバック表示シグナル
    change_feedback = QtCore.pyqtSignal(str, str, int)  # フィードバック内容変換シグナル
    action_operation = QtCore.pyqtSignal(int, int)   # 操作実行シグナル
    startorend_leap = QtCore.pyqtSignal(bool)  # ハンドトラッキングの開始終了

    def __init__(self):
        super(HandListener, self).__init__()
        self.finger_dis_dim = {"up": 0, "low": 0, "left": 0, "right": 0}
        self.finger_dis_size = [0, 0]
        self.isPointingMode = False
        self.predictor = Predictor("KNN")   # 学習モデル
        self.memoryHands = {}
        self.preHands = {}

    def on_caribration(self, controller):
        print("Do caribration")
        print("Point upper-left on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ul = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ul)

        print("Point lower-left on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ll = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ll)

        print("Point upper-right on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_lr = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_lr)

        print("Point lower-right on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ur = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ur)

        # 四隅の値の平均を上下左右の値とする
        self.finger_dis_dim["up"] = (dis_ul.y + dis_ur.y) / 2
        self.finger_dis_dim["low"] = (dis_ll.y + dis_lr.y) / 2
        self.finger_dis_dim["left"] = (dis_ul.x + dis_ll.x) / 2
        self.finger_dis_dim["right"] = (dis_ur.x + dis_lr.x) / 2
        self.finger_dis_size[0] = self.finger_dis_dim["right"] - self.finger_dis_dim["left"]
        self.finger_dis_size[1] = self.finger_dis_dim["low"] - self.finger_dis_dim["up"]
        print(self.finger_dis_size)

        print("\nComplete caribration")
        sys.stdin.readline()

    def on_caribrationTest(self):
        dis_ul = Vector(-120, 215, 0)
        dis_ll = Vector(-130, 90, 0)
        dis_lr = Vector(130, 90, 0)
        dis_ur = Vector(120, 215, 0)

        self.finger_dis_dim["up"] = (dis_ul.y + dis_ur.y) / 2
        self.finger_dis_dim["low"] = (dis_ll.y + dis_lr.y) / 2
        self.finger_dis_dim["left"] = (dis_ul.x + dis_ll.x) / 2
        self.finger_dis_dim["right"] = (dis_ur.x + dis_lr.x) / 2
        self.finger_dis_size[0] = self.finger_dis_dim["right"] - self.finger_dis_dim["left"]
        self.finger_dis_size[1] = self.finger_dis_dim["low"] - self.finger_dis_dim["up"]
        print(self.finger_dis_size)
        print("Complete test caribration")

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")
        # self.on_caribrationTest()
        self.setPointingMode(False)
        self.startorend_leap.emit(True)

    def on_disconnect(self, controller):
        print("Disconnected")
        self.startorend_leap.emit(False)

    def on_exit(self, controller):
        print("Exited")
        self.startorend_leap.emit(False)

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        for handid in list(self.preHands.keys()):
            if not frame.hand(handid).is_valid:
                # 現フレームに存在しない手のデータを削除
                del self.memoryHands[handid]
                del self.preHands[handid]

        # 手が認識されない時フィードバックを非表示
        if frame.hands.is_empty:
            self.hide_feedback.emit()

        # 認識した手の形状を識別する
        else:
            for hand in frame.hands:
                handlist = self.memoryHands.get(hand.id)
                prehand = self.preHands.get(hand.id)

                if handlist is None:   # 新規の手だったら追加
                    handlist = []
                    prehand = HandEnum.FREE.value  # １つ前の手形状にFREE状態をセット

                if len(handlist) == memorySize:   # 記憶サイズいっぱいだったらFirst out
                    handlist.pop(0)

                hand_state = self.predictor.handPredict(hand)  # 学習機で手形状識別
                # print(hand_state)
                handlist.append(hand_state)   # 手形状のメモリに新規追加
                # 識別手形状とメモリのて形状リストから現在の手形状を決定
                try:
                    currentStatus = statistics.mode(handlist)  # リストの最頻値を算出
                except:
                    currentStatus = hand_state
                # print(self.predictor.stateLabels[currentStatus])   # 識別結果を出力
                self.memoryHands[hand.id] = handlist  # 手形状のメモリを更新
                # print(self.isHolizon(hand))
                if prehand != currentStatus:
                    self.action(prehand, currentStatus, hand)
                    self.preHands[hand.id] = currentStatus  # １つ前の手形状を更新

    def isHolizon(self, hand):
        # 親指第一関節と人差し指の第二関節の位置を識別
        # TODO 45度を閾値としているが調査の必要あり
        thumb_pos = hand.fingers.finger_type(Finger.TYPE_THUMB)[0].joint_position(Finger.JOINT_DIP)
        index_pos = hand.fingers.finger_type(Finger.TYPE_INDEX)[0].joint_position(Finger.JOINT_PIP)
        dif_vec = Vector(index_pos.x - thumb_pos.x, index_pos.y - thumb_pos.y, 0)
        return dif_vec.y * dif_vec.y / dif_vec.x /dif_vec.x < 1

    def action(self, p_hand, n_hand, hand):
        if self.isHolizon(hand):
            direction = DirectionEnum.HORIZON.value
        else:
            direction = DirectionEnum.VERTICAL.value

        if n_hand == HandEnum.FREE.value:
            if list(self.preHands.values()).count(HandEnum.FREE.value) == len(self.preHands):
                self.hide_feedback.emit()
        
        elif n_hand == HandEnum.PINCH_IN.value:
            if p_hand == HandEnum.PINCH_OUT.value:
                print("削除関数呼び出し")
                self.action_operation.emit(ActionEnum.DELETE.value, direction)

            else:
                # print("挿入ステータス呼び出し")
                self.change_feedback.emit("挿入", "", direction)


        elif n_hand == HandEnum.PINCH_OUT.value:
            if p_hand == HandEnum.PINCH_IN.value:
                print("挿入関数呼び出し")
                self.action_operation.emit(ActionEnum.INSERT.value, direction)

            elif p_hand == HandEnum.REVERSE.value and direction == DirectionEnum.VERTICAL.value:
                print("降順ソート関数呼び出し")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.BACK.value)

            else:
                # print("削除ステータス呼び出し")
                self.change_feedback.emit("削除", "", direction)


        elif n_hand == HandEnum.REVERSE.value:
            if p_hand == HandEnum.PINCH_OUT.value and direction == DirectionEnum.VERTICAL.value:
                print("昇順ソート関数呼び出し")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.FRONT.value)
            else:
                # print("降順ソートステータス呼び出し")
                self.change_feedback.emit("ソート", "", direction)

        elif n_hand == HandEnum.PALM.value:
            if p_hand == HandEnum.GRIP.value:
                print("ペースト関数呼び出し")
                self.action_operation.emit(ActionEnum.PASTE.value, None)

            else:
                # print("コピー，カットステータス呼び出し")
                if len(self.preHands) > 1:
                    self.change_feedback.emit("コピー", "", DirectionEnum.VERTICAL.value)
                else:
                    self.change_feedback.emit("カット", "", DirectionEnum.VERTICAL.value)
        
        elif n_hand == HandEnum.GRIP.value:
            if p_hand == HandEnum.PALM.value:
                if list(self.preHands.values()).count(HandEnum.PALM.value) > 1:
                    print("コピー関数呼び出し")
                    self.action_operation.emit(ActionEnum.COPY.value, None)
                else:
                    print("カット関数呼び出し")
                    self.action_operation.emit(ActionEnum.CUT.value, None)

            else:
                # print("ペーストステータス呼び出し")
                self.change_feedback.emit("ペースト", "", DirectionEnum.VERTICAL.value)


    def setPointingMode(self, isMode):
        self.isPointingMode = isMode