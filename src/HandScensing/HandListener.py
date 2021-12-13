import copy
import heapq
import statistics
import sys
import pyautogui

from src.HandScensing.Predictor import Predictor
from res.SSEnum import HandEnum, DirectionEnum, ActionEnum
from PyQt5 import QtCore

from src.UDP.MoCapData import MoCapData, RigidBody, MarkerSetData
from src.UDP.NatNetClient import NatNetClient
from src.UDP.PythonSample import print_configuration

DIS_SIZE = pyautogui.size()
memorySize = 30
z_threshold = 30


class HandData():
    def __init__(self):
        self.rb_id = 0
        self.hand_pos = [0, 0, 0]
        self.rot = [0, 0, 0, 0]
        self.finger_marker_dict = {}
        self.fingers_pos = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.thumb_pos = [0, 0, 0]
        self.index_pos = [0, 0, 0]
        self.pinky_pos = [0, 0, 0]

    def setPalm(self, rigid_body: RigidBody):
        self.hand_pos = rigid_body.pos
        self.rot = rigid_body.rot

    def setFingerMarkerDict(self, key, value):
        self.finger_marker_dict[key] = value

    def setFingerPos(self, marker_list):
        for marker in marker_list:
            if marker.id_num in self.finger_marker_dict.keys():
                self.fingers_pos[self.finger_marker_dict[marker.id_num]] = marker.pos

    def getFingerPos(self, id):
        return self.fingers_pos[self.finger_marker_dict[id]]

    # TODO: マーカーロストの処理


class HandListener(QtCore.QThread):
    show_feedback = QtCore.pyqtSignal()  # フィードバック非表示シグナル
    hide_feedback = QtCore.pyqtSignal()  # フィードバック表示シグナル
    change_feedback = QtCore.pyqtSignal(str, str, int)  # フィードバック内容変換シグナル
    action_operation = QtCore.pyqtSignal(int, int)  # 操作実行シグナル
    startorend_leap = QtCore.pyqtSignal(bool)  # ハンドトラッキングの開始終了

    def __init__(self):
        super(HandListener, self).__init__()
        self.finger_dis_dim = {"up": 0, "low": 0, "left": 0, "right": 0}
        self.finger_dis_size = [0, 0]
        self.isPointingMode = False
        self.predictor = Predictor("KNN")  # 学習モデル
        self.current_mocap_data: MoCapData = None
        self.hands_dict = {'l': HandData(), 'r': HandData()}
        handlist = []
        for i in range(memorySize):
            handlist.append(HandEnum.FREE.value)

        self.memoryHands = {'l': copy.copy(handlist), 'r': copy.copy(handlist)}
        self.preHands = {'l': HandEnum.FREE.value, 'r': HandEnum.FREE.value}

    def initOptiTrack(self):
        optionsDict = {}
        optionsDict["clientAddress"] = "172.16.0.8"
        optionsDict["serverAddress"] = "172.16.0.100"
        optionsDict["use_multicast"] = False

        self.streaming_client = NatNetClient()
        self.streaming_client.set_client_address(optionsDict["clientAddress"])
        self.streaming_client.set_server_address(optionsDict["serverAddress"])
        self.streaming_client.set_use_multicast(optionsDict["use_multicast"])
        print_configuration(self.streaming_client)

        is_running = self.streaming_client.run()
        if not is_running:
            print("ERROR: Could not start streaming client.")
            try:
                sys.exit(1)
            except SystemExit:
                print("...")
            finally:
                print("exiting")

        if self.streaming_client.connected() is False:
            print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
            try:
                sys.exit(2)
            except SystemExit:
                print("...")
            finally:
                print("exiting")

        self.do_calibration()
        self.streaming_client.new_frame_listener = self.frameListener

    def calibrationListener(self, mocap_data: MoCapData):
        self.current_mocap_data = mocap_data

    def getCurrentData(self):
        while not self.judgeDataComplete(self.current_mocap_data):
            print("Sorry, the system is not ready\nPush Enter key again\n")
            sys.stdin.readline()
        return copy.deepcopy(self.getCurrentData())

    def judgeDataComplete(self, mocap_data: MoCapData):
        return mocap_data.rigid_body_data.get_rigid_body_count() < 2 and \
               mocap_data.marker_set_data.unlabeled_markers.get_num_points() == len(HandData().fingers_pos) * 2

    def do_calibration(self):
        print("Do caribration")
        self.streaming_client.new_frame_listener = self.calibrationListener

        print("Please stay hand on home position\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.settingRigidbodyID(mocap_data)
        self.settingUnlabeledMarkerID(mocap_data)
        print("Complete both hands setting calibration!")

        self.settingScrean()
        print("\nComplete caribration")

        self.streaming_client.new_frame_listener = self.frameListener
        sys.stdin.readline()

    def settingScrean(self):
        # 画面領域を決定
        print("\nNext, screan size caribration")
        print("Point to upper-left on display\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.setHandData(mocap_data)
        # TODO: 左右どちらの手にするかは要チェック基本左手
        dis_ul = self.hands_dict['l'].fingers_pos[1]
        print(dis_ul)

        print("Point to lower-left on display\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.setHandData(mocap_data)
        # TODO: 左右どちらの手にするかは要チェック
        dis_ll = self.hands_dict['l'].fingers_pos[1]
        print(dis_ll)

        print("Point to upper-right on display\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.setHandData(mocap_data)
        # TODO: 左右どちらの手にするかは要チェック
        dis_lr = self.hands_dict['l'].fingers_pos[1]
        print(dis_lr)

        print("Point to lower-right on display\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.setHandData(mocap_data)
        # TODO: 左右どちらの手にするかは要チェック
        dis_ur = self.hands_dict['l'].fingers_pos[1]
        print(dis_ur)

        # 四隅の値の平均を上下左右の値とする
        self.finger_dis_dim["up"] = (dis_ul[1] + dis_ur[1]) / 2
        self.finger_dis_dim["low"] = (dis_ll[1] + dis_lr[1]) / 2
        self.finger_dis_dim["left"] = (dis_ul[0] + dis_ll[0]) / 2
        self.finger_dis_dim["right"] = (dis_ur[0] + dis_lr[0]) / 2
        self.finger_dis_size[0] = self.finger_dis_dim["right"] - self.finger_dis_dim["left"]
        self.finger_dis_size[1] = self.finger_dis_dim["low"] - self.finger_dis_dim["up"]
        print(self.finger_dis_size)

    def settingUnlabeledMarkerID(self, mocap_data):
        # unlabeledMarkerのlabelを登録する <HandData().finger_marker_dict[id] -> finger_pos.key>
        marker_pos_x_list = []
        marker_list = mocap_data.marker_set_data.unlabeled_markers.marker_list
        for marker in marker_list:
            marker_pos_x_list.append(marker.pos[0])
        sorted_list = sorted(marker_pos_x_list)
        for key in range(len(marker_pos_x_list)):
            for id in range(len(marker_pos_x_list)):
                if sorted_list[key] == (marker_pos_x_list[id]):
                    if key < len(HandData().fingers_pos):
                        self.hands_dict['l'].finger_marker_dict[id] = abs(key - len(HandData().fingers_pos) + 1)
                        # self.hands_dict['l'].fingers_pos[key] = marker_list[id]
                    else:
                        self.hands_dict['r'].finger_marker_dict[id] = key - len(HandData().fingers_pos)
                        # self.hands_dict['r'].fingers_pos[key-len(HandData().fingers_pos)] = marker_list[id]

    def settingRigidbodyID(self, mocap_data):
        # rigidbodyIDを登録 < type_hands[rididbody.num_id] = 'l'>
        if mocap_data.rigid_body_data.rigid_body_list[0].pos[0] < mocap_data.rigid_body_data.rigid_body_list[1].pos[1]:
            self.hands_dict['l'].rb_id = mocap_data.rigid_body_data.rigid_body_list[0].id_num
            self.hands_dict['r'].rb_id = mocap_data.rigid_body_data.rigid_body_list[1].id_num
        else:
            self.hands_dict['l'].rb_id = mocap_data.rigid_body_data.rigid_body_list[1].id_num
            self.hands_dict['r'].rb_id = mocap_data.rigid_body_data.rigid_body_list[0].id_num

    def on_caribrationTest(self):
        dis_ul = [-120, 215, 0]
        dis_ll = [-130, 90, 0]
        dis_lr = [130, 90, 0]
        dis_ur = [120, 215, 0]

        self.finger_dis_dim["up"] = (dis_ul[1] + dis_ur[1]) / 2
        self.finger_dis_dim["low"] = (dis_ll[1] + dis_lr[1]) / 2
        self.finger_dis_dim["left"] = (dis_ul[0] + dis_ll[0]) / 2
        self.finger_dis_dim["right"] = (dis_ur[0] + dis_lr[0]) / 2
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

    def setHandData(self, mocap_data: MoCapData):
        for body in mocap_data.rigid_body_data.rigid_body_list:
            if self.hands_dict['l'].rb_id == body.id_num:
                self.hands_dict['l'].setPalm(body)
            elif self.hands_dict['r'].rb_id == body.id_num:
                self.hands_dict['r'].setPalm(body)

        marker_list = mocap_data.marker_set_data.unlabeled_markers.marker_list
        self.hands_dict['l'].setFingerPos(marker_list=copy.copy(marker_list))
        self.hands_dict['r'].setFingerPos(marker_list=copy.copy(marker_list))

    # TODO: This function has to be fixed for Opti version
    def frameListener(self, mocap_data: MoCapData):
        if self.judgeDataComplete(mocap_data):
            # フレームデータから手のデータを抽出
            self.setHandData(mocap_data)

            # 左右両方の手の位置が閾値より低い時フィードバックを非表示
            if self.hands_dict['l'].hand_pos[2] < z_threshold and self.hands_dict['r'].hand_pos[2] < z_threshold:
                self.hide_feedback.emit()
                return

            # 認識した手の形状を識別する
            for key in self.hands_dict.keys():
                handlist = self.memoryHands.get(key)
                prehand = self.preHands.get(key)

                handlist.pop(0)

                if self.hands_dict.get(key).hand_pos[2] < z_threshold:
                    hand_state = HandEnum.FREE.value
                else:
                    hand_state = self.predictor.handPredict(self.hands_dict.get(key))  # 学習機で手形状識別
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

        elif n_hand == HandEnum.PALM.value:
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
            if p_hand == HandEnum.PALM.value:
                if list(self.preHands.values()).count(HandEnum.PALM.value) > 1:
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
        for handid in list(self.preHands.keys()):
            del self.memoryHands[handid]
            del self.preHands[handid]  # １つ前の手形状にFREE状態をセット
