import statistics
import sys
import pyautogui

from src.LeapMotion.Leap import Listener, Vector
from src.Predictor import Predictor
from src.SSEnum import HandEnum, DirectionEnum
from PyQt5 import QtCore

DIS_SIZE = pyautogui.size()
memorySize = 2

class handListener(QtCore.QThread, Listener):
    show_feedback = QtCore.pyqtSignal()  # フィードバック非表示シグナル
    hide_feedback = QtCore.pyqtSignal()  # フィードバック表示シグナル
    change_feedback = QtCore.pyqtSignal(str, str, int)  # フィードバック内容変換シグナル
    action_operation = QtCore.pyqtSignal()   # 操作実行シグナル
    startorend_leap = QtCore.pyqtSignal(bool)  # ハンドトラッキングの開始終了

    def __init__(self):
        super(handListener, self).__init__()
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

        if frame.hands.is_empty:
            self.hide_feedback.emit()
        else:
            for hand in frame.hands:
                handlist = self.memoryHands.get(hand.id)
                prehand = self.preHands.get(hand.id)
                if handlist is None:   # 新規の手だったら追加
                    handlist = []
                    prehand = HandEnum.FREE.value
                if len(handlist) == memorySize:   # 記憶サイズいっぱいだったらFirst out
                    handlist.pop(0)
                hand_state = self.predictor.handPredict(hand)
                print(hand_state)
                handlist.append(hand_state)   # 手形状のメモリに新規追加
                # 判定手形状を識別
                try:
                    currentStatus = statistics.mode(handlist)  # リストの最頻値を算出
                except:
                    currentStatus = hand_state
                # print(self.predictor.stateLabels[currentStatus])   # 識別結果を出力
                self.memoryHands[hand.id] = handlist  # 手形状のメモリを更新
                if prehand != currentStatus:
                    self.action(prehand, currentStatus)
                    self.preHands[hand.id] = currentStatus  # １つ前の手形状を更新


    def action(self, pre, next):
        # TODO ジェスチャ識別によるself.app.関数の呼び出しを実装
        if next == HandEnum.FREE.value:
            if list(self.preHands.values()).count(HandEnum.FREE.value) == len(self.preHands):
                self.hide_feedback.emit()
        
        elif next == HandEnum.PINCH_IN.value:
            if pre == HandEnum.PINCH_OUT.value:
                print("削除関数呼び出し")

            else:
                print("挿入ステータス呼び出し")
                self.change_feedback.emit("挿入", "下に寄せる", DirectionEnum.HORIZON.value)

            
        elif next == HandEnum.PINCH_OUT.value:
            if pre == HandEnum.PINCH_IN.value:
                print("挿入関数呼び出し")

            elif pre == HandEnum.REVERSE.value:
                print("降順ソート関数呼び出し")

            else:
                print("削除ステータス呼び出し")
                self.change_feedback.emit("削除", "縦に寄せる", DirectionEnum.VERTICAL.value)

        elif next == HandEnum.REVERSE.value:
            if pre == HandEnum.PINCH_OUT.value:
                print("昇順ソート関数呼び出し")

            else:
                print("降順ソート呼び出し")

        
        elif next == HandEnum.PALM.value:
            if pre == HandEnum.GRIP.value:
                print("ペースト関数呼び出し")

            else:
                print("コピー，カットステータス呼び出し")

        
        elif next == HandEnum.GRIP.value:
            if pre == HandEnum.PALM.value:
                if list(self.preHands.values()).count(HandEnum.PALM.value) > 1:
                    print("コピー関数呼び出し")

                else:
                    print("カット関数呼び出し")

            else:
                print("ペーストステータス呼び出し")






    def setPointingMode(self, isMode):
        self.isPointingMode = isMode
