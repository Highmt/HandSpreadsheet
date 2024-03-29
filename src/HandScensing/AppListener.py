import copy
import heapq
import statistics
import sys
import pyautogui

from src.HandScensing.HandListener import HandListener, HandData
from src.HandScensing.Predictor import Predictor
from res.SSEnum import HandEnum, DirectionEnum, ActionEnum
from PyQt5 import QtCore

from src.UDP.MoCapData import MoCapData

DIS_SIZE = pyautogui.size()
memorySize = 20
ver = "p0"


class AppListener(QtCore.QThread, HandListener):
    show_feedback = QtCore.pyqtSignal()  # フィードバック非表示シグナル
    hide_feedback = QtCore.pyqtSignal()  # フィードバック表示シグナル
    change_feedback = QtCore.pyqtSignal(str, str, int)  # フィードバック内容変換シグナル
    action_operation = QtCore.pyqtSignal(int, int)  # 操作実行シグナル
    start_end_opti = QtCore.pyqtSignal(bool)  # ハンドトラッキングの開始終了

    def __init__(self):
        super().__init__()
        self.isPointingMode = False
        self.predictor = Predictor(alg="KNN", ver=ver)  # 学習モデル
        self.memoryHands = {}
        self.formerStatus = {}
        self.formerHands = {}
        self.resetHand()

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")
        # self.on_caribrationTest()
        self.setPointingMode(False)
        self.start_end_opti.emit(True)

    def on_disconnect(self, controller):
        print("Disconnected")
        self.start_end_opti.emit(False)

    def on_exit(self, controller):
        print("Exited")
        self.start_end_opti.emit(False)

    def judgeCalibrate(self):
        # a = False
        # for key in self.hands_dict.keys():
        #     if self.hands_dict[key].position[1] - self.formerHands[key].position[1]
        return True

    def frameListener(self, mocap_data: MoCapData):
        if self.judgeDataComplete(mocap_data):
            if self.need_calibration:
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
            # フレームデータから手のデータを抽出
            self.setHandData(mocap_data)

            # 左右両方の手の位置が閾値より低い時フィードバックを非表示+マーカ再設定+resetHand
            if self.hands_dict['l'].position[1] <= self.calibration_threshold and self.hands_dict['r'].position[1] <= self.calibration_threshold and self.judgeCalibrate():
                self.hide_feedback.emit()
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)

            # 認識した手の形状を識別する
            self.formerHands = copy.deepcopy(self.hands_dict)
            for key in self.hands_dict.keys():
                formerStatus: int = self.formerStatus.get(key)

                self.memoryHands[key].pop(0)
                if self.judgeValidHand(key):
                    hand_state = HandEnum.FREE.value
                    self.formerStatus[key] = hand_state
                    self.memoryHands[key].append(hand_state)
                else:
                    hand_state = self.predictor.handPredict(hand=self.hands_dict.get(key))  # 学習機で手形状識別
                    self.memoryHands[key].append(hand_state)  # 手形状のメモリに新規追加

                    # 識別手形状とメモリの手形状リストから現在の手形状を決定
                    try:
                        currentStatus = statistics.mode(self.memoryHands[key])  # リストの最頻値を算出
                    except:
                        currentStatus = formerStatus
                    # print("predict status: {}, current status: {}".format(hand_state, currentStatus))
                    # print(self.memoryHands[key])
                    if formerStatus != currentStatus:
                        self.action(formerStatus, currentStatus, self.hands_dict.get(key))
                        self.formerStatus[key] = currentStatus  # １つ前の手形状を更新

            if self.formerStatus['l'] == HandEnum.FREE.value and self.formerStatus['r'] == HandEnum.FREE.value:
                self.hide_feedback.emit()


    def isHolizon(self, hand: HandData):
        # 親指第一関節と人差し指の第二関節の位置を識別
        # TODO 45度を閾値としているが調査の必要あり
        thumb_pos = hand.fingers_pos[0]
        index_pos = hand.fingers_pos[1]
        dif_vec = [index_pos[0] - thumb_pos[0], index_pos[1] - thumb_pos[1]]
        return dif_vec[1] * dif_vec[1] / dif_vec[0] / dif_vec[0] < 1

    def action(self, formerS: int, currentS: int, hand: HandData):
        if self.isHolizon(hand):
            direction = DirectionEnum.HORIZON.value
        else:
            direction = DirectionEnum.VERTICAL.value

        if currentS == HandEnum.PINCH_IN.value:
            if formerS == HandEnum.PINCH_OUT.value:
                print("削除関数実行")
                self.action_operation.emit(ActionEnum.DELETE.value, direction)

            else:
                # print("挿入前状態に遷移")
                self.change_feedback.emit("Pinch In", "", direction)


        elif currentS == HandEnum.PINCH_OUT.value:
            if formerS == HandEnum.PINCH_IN.value:
                print("挿入関数実行")
                self.action_operation.emit(ActionEnum.INSERT.value, direction)

            elif formerS == HandEnum.REVERSE.value and direction == DirectionEnum.VERTICAL.value:
                print("降順ソート関数実行")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.BACK.value)

            else:
                # print("削除前状態に遷移")
                self.change_feedback.emit("Pinch Out", "", direction)


        elif currentS == HandEnum.REVERSE.value:
            if formerS == HandEnum.PINCH_OUT.value and direction == DirectionEnum.VERTICAL.value:
                print("昇順ソート関数実行")
                self.action_operation.emit(ActionEnum.SORT.value, DirectionEnum.FRONT.value)
            else:
                # print("降順ソート前状態に遷移")
                self.change_feedback.emit("Reverse", "", direction)

        elif currentS == HandEnum.OPEN.value:
            if formerS == HandEnum.GRIP.value:
                print("ペースト関数実行")
                self.action_operation.emit(ActionEnum.PASTE.value, DirectionEnum.NONE.value)

            else:
                # print("コピー，カット前状態に遷移")
                if self.getHand('l').position[1] > self.action_threshold and self.getHand('r').position[1] > self.action_threshold:
                    self.change_feedback.emit("Both Open", "", DirectionEnum.VERTICAL.value)
                else:
                    self.change_feedback.emit("One Open", "", DirectionEnum.VERTICAL.value)

        elif currentS == HandEnum.GRIP.value:
            if formerS == HandEnum.OPEN.value:
                if list(self.formerStatus.values()).count(HandEnum.OPEN.value) > 1:
                    print("コピー関数実行")
                    self.action_operation.emit(ActionEnum.COPY.value, DirectionEnum.NONE.value)
                else:
                    print("カット関数実行")
                    self.action_operation.emit(ActionEnum.CUT.value, DirectionEnum.NONE.value)

            else:
                # print("ペースト前状態に遷移")
                self.change_feedback.emit("Grip", "", DirectionEnum.VERTICAL.value)

    def setPointingMode(self, isMode):
        self.isPointingMode = isMode

    def resetHand(self):
        handlist = []
        for i in range(memorySize):
            handlist.append(HandEnum.FREE.value)
        self.memoryHands = {'l': copy.copy(handlist), 'r': copy.copy(handlist)}
        self.formerStatus = {'l': HandEnum.FREE.value, 'r': HandEnum.FREE.value}

    def setListener(self):
        self.streaming_client.new_frame_listener = self.frameListener
