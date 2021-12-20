import copy
import heapq
import statistics
import sys
import pyautogui

from src.HandScensing.HandListener import HandListener, HandData, Y_THRESHOLD
from src.HandScensing.Predictor import Predictor
from res.SSEnum import HandEnum, DirectionEnum, ActionEnum
from PyQt5 import QtCore

from src.UDP.MoCapData import MoCapData, RigidBody, MarkerSetData
from src.UDP.NatNetClient import NatNetClient
from src.UDP.PythonSample import print_configuration

DIS_SIZE = pyautogui.size()
memorySize = 30


class AppListener(QtCore.QThread, HandListener):
    show_feedback = QtCore.pyqtSignal()  # フィードバック非表示シグナル
    hide_feedback = QtCore.pyqtSignal()  # フィードバック表示シグナル
    change_feedback = QtCore.pyqtSignal(str, str, int)  # フィードバック内容変換シグナル
    action_operation = QtCore.pyqtSignal(int, int)  # 操作実行シグナル
    startorend_leap = QtCore.pyqtSignal(bool)  # ハンドトラッキングの開始終了

    def __init__(self):
        super().__init__()
        self.isPointingMode = False
        self.predictor = Predictor("KNN")  # 学習モデル
        self.memoryHands = {}
        self.preHands = {}
        self.resetHand()

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

    def frameListener(self, mocap_data: MoCapData):
        if self.judgeDataComplete(mocap_data):
            if self.is_markerlosted:
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)
            # フレームデータから手のデータを抽出
            self.setHandData(mocap_data)

            # 左右両方の手の位置が閾値より低い時フィードバックを非表示かつマーカ再設定
            if self.hands_dict['l'].position[1] <= Y_THRESHOLD and self.hands_dict['r'].position[1] <= Y_THRESHOLD:
                self.hide_feedback.emit()
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)
                return

            # 認識した手の形状を識別する
            for key in self.hands_dict.keys():
                handlist = self.memoryHands.get(key)
                prehand: int = self.preHands.get(key)

                handlist.pop(0)

                if self.hands_dict.get(key).position[1] < Y_THRESHOLD:
                    hand_state = HandEnum.FREE.value
                else:
                    hand_state = self.predictor.handPredict(hand=self.hands_dict.get(key))  # 学習機で手形状識別
                # print(hand_state)
                handlist.append(hand_state)  # 手形状のメモリに新規追加
                self.memoryHands[key] = handlist  # 手形状のメモリを更新

                # 識別手形状とメモリの手形状リストから現在の手形状を決定
                try:
                    currentStatus = statistics.mode(handlist)  # リストの最頻値を算出
                except:
                    currentStatus = prehand
                # print(self.predictor.stateLabels[currentStatus])   # 識別結果を出力
                if prehand != currentStatus:
                    self.action(prehand, currentStatus, self.hands_dict.get(key))
                    self.preHands[key] = currentStatus  # １つ前の手形状を更新
                    # 両手が閾値以下の位置にある時ラベルの再設定処理を回す
        else:
            self.is_markerlosted = True

    def isHolizon(self, hand: HandData):
        # 親指第一関節と人差し指の第二関節の位置を識別
        # TODO 45度を閾値としているが調査の必要あり
        thumb_pos = hand.fingers_pos[0]
        index_pos = hand.fingers_pos[1]
        dif_vec = [index_pos[0] - thumb_pos[0], index_pos[1] - thumb_pos[1]]
        return dif_vec[1] * dif_vec[1] / dif_vec[0] / dif_vec[0] < 1

    def action(self, p_hand: int, n_hand: int, hand: HandData):
        if self.isHolizon(hand):
            direction = DirectionEnum.HORIZON.value
        else:
            direction = DirectionEnum.VERTICAL.value

        if n_hand == HandEnum.FREE.value:
            # if list(self.preHands.values()).count(HandEnum.FREE.value) == len(self.preHands):  //　絶対入らない
            self.hide_feedback.emit()
            return

        elif n_hand == HandEnum.PINCH_IN.value:
            if p_hand == HandEnum.PINCH_OUT.value:
                print("削除関数実行")
                self.action_operation.emit(ActionEnum.DELETE.value, direction)

            else:
                # print("挿入前状態に遷移")
                self.change_feedback.emit("Pinch In", "", direction)


        elif n_hand == HandEnum.PINCH_OUT.value:
            if p_hand == HandEnum.PINCH_IN.value:
                print("挿入関数実行")
                self.action_operation.emit(ActionEnum.INSERT.value, direction)

            elif p_hand == HandEnum.REVERSE.value and direction == DirectionEnum.VERTICAL.value:
                print("降順ソート関数実行")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.BACK.value)

            else:
                # print("削除前状態に遷移")
                self.change_feedback.emit("Pinch Out", "", direction)


        elif n_hand == HandEnum.REVERSE.value:
            if p_hand == HandEnum.PINCH_OUT.value and direction == DirectionEnum.VERTICAL.value:
                print("昇順ソート関数実行")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.FRONT.value)
            else:
                # print("降順ソート前状態に遷移")
                self.change_feedback.emit("Reverse", "", direction)

        elif n_hand == HandEnum.OPEN.value:
            if p_hand == HandEnum.GRIP.value:
                print("ペースト関数実行")
                self.action_operation.emit(ActionEnum.PASTE.value, DirectionEnum.NONE.value)

            else:
                # print("コピー，カット前状態に遷移")
                if len(self.preHands) > 1:
                    self.change_feedback.emit("Both Palm", "", DirectionEnum.VERTICAL.value)
                else:
                    self.change_feedback.emit("One Palm", "", DirectionEnum.VERTICAL.value)

        elif n_hand == HandEnum.GRIP.value:
            if p_hand == HandEnum.OPEN.value:
                if list(self.preHands.values()).count(HandEnum.OPEN.value) > 1:
                    print("コピー関数実行")
                    self.action_operation.emit(ActionEnum.COPY.value, DirectionEnum.NONE.value)
                else:
                    print("カット関数実行")
                    self.action_operation.emit(ActionEnum.CUT.value, DirectionEnum.NONE.value)

            else:
                # print("ペースト前状態に遷移")
                self.change_feedback.emit("Grip", "", DirectionEnum.VERTICAL.value)

        self.resetHand()

    def setPointingMode(self, isMode):
        self.isPointingMode = isMode

    def resetHand(self):
        handlist = []
        for i in range(memorySize):
            handlist.append(HandEnum.FREE.value)
        self.memoryHands = {'l': copy.copy(handlist), 'r': copy.copy(handlist)}
        self.preHands = {'l': HandEnum.FREE.value, 'r': HandEnum.FREE.value}
