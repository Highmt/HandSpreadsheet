import copy
import math
import sys
import time

import pandas as pd
import pyautogui
import numpy as np
from scipy.spatial.transform import Rotation

from res.SSEnum import FeatureEnum
from src.UDP.MoCapData import MoCapData, RigidBody
from src.UDP.NatNetClient import NatNetClient

finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
DIS_SIZE = pyautogui.size()
Y_THRESHOLD = 100.0  # マーカーキャリブレーションを行う閾値
Y_ACTION_THRESHOLD = 150.0
# TODO: マーカーキャリブレーションの閾値とジェスチャ実行の閾値を分ける
# Y_THRESHOLD < y < Y_ACTION_THRESHOLDの間で手を変える

def print_configuration(natnet_client: NatNetClient):
    print("Connection Configuration:")
    print("  Client:          %s" % natnet_client.local_ip_address)
    print("  Server:          %s" % natnet_client.server_ip_address)
    print("  Command Port:    %d" % natnet_client.command_port)
    print("  Data Port:       %d" % natnet_client.data_port)

    if natnet_client.use_multicast:
        print("  Using Multicast")
        print("  Multicast Group: %s" % natnet_client.multicast_address)
    else:
        print("  Using Unicast")

    # NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" % (application_name))
    print("    NatNetVersion  %d %d %d %d" % (
    nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print(
        "    ServerVersion  %d %d %d %d" % (server_version[0], server_version[1], server_version[2], server_version[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d" % (nat_net_requested_version[0], nat_net_requested_version[1], \
                                              nat_net_requested_version[2], nat_net_requested_version[3]))
    # print("command_socket = %s"%(str(natnet_client.command_socket)))
    # print("data_socket    = %s"%(str(natnet_client.data_socket)))

class HandData:
    def __init__(self, is_left: bool = None):
        self.rb_id = 0
        self.is_left = is_left
        self.position = np.array([0.0, 0.0, 0.0])
        self.position_offset = np.array([0.0, 0.0, 0.0])
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.rotation_offset = np.array([0.0, 0.0, 0.0, 0.0])
        self.fingers_pos = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        self.timestamp = 0.0

    def setHand(self, rigid_body: RigidBody):
        rot = Rotation.from_quat(rigid_body.rot).as_rotvec()
        self.position = (np.array(rigid_body.pos) - self.position_offset) * 1000
        self.rotation = rot - self.rotation_offset

    def setFingerPos(self, finger_type, marker_pos):
        for axis in range(len(self.position)):
            self.fingers_pos[finger_type][axis] = (marker_pos[axis] - self.position_offset[axis]) * 1000

    def getFingerVec(self, finger_type: int) -> np.ndarray:
        return self.fingers_pos[finger_type] - self.position

    def setOffset(self, position, rotation):
        # offsetを設定
        self.position_offset = np.array(position)
        self.rotation_offset = Rotation.from_quat(rotation).as_rotvec()

    def convertPS(self):
        ps = pd.Series(dtype=pd.Float64Dtype, index=FeatureEnum.COLLECT_LIST.value)
        ps["timestamp"] = self.timestamp
        ps["x", "y", "z"] = self.position
        ps["pitch", "roll", "yaw"] = self.rotation

        # Get fingers
        for finger_id in range(len(self.fingers_pos)):
            for pos in range(3):
                ps[finger_labels[finger_id] + "_pos_" + pos_labels[pos]] = self.getFingerVec(finger_type=finger_id)[pos]
        return ps

    def loadPS(self, ps: pd.Series):
        self.timestamp = ps[["timestamp"]].values
        self.position = ps[["x", "y", "z"]].values
        self.rotation = ps[["pitch", "roll", "yaw"]].values
        # Get fingers
        for finger_id in range(len(self.fingers_pos)):
            for pos in range(3):
                self.fingers_pos[finger_id][pos] = ps[finger_labels[finger_id] + "_pos_" + pos_labels[pos]]

class HandListener:
    def __init__(self):
        self.finger_dis_dim = {"up": 0, "low": 0, "left": 0, "right": 0}
        self.finger_dis_size = [0, 0]
        self.current_mocap_data: MoCapData = None
        self.hands_dict = {'l': HandData(is_left=True), 'r': HandData(is_left=False)}
        self.marker_label_list = [-1] * (HandData().fingers_pos.__len__() * 2)
        self.need_calibration = True
        self.is_resetted = False
        self.start_timestamp = -1

    def initOptiTrack(self):
        optionsDict = {}
        optionsDict["clientAddress"] = "172.17.1.102"
        optionsDict["serverAddress"] = "172.17.1.101"
        optionsDict["use_multicast"] = False

        self.streaming_client = NatNetClient()
        self.streaming_client.set_client_address(optionsDict["clientAddress"])
        self.streaming_client.set_server_address(optionsDict["serverAddress"])
        self.streaming_client.set_use_multicast(optionsDict["use_multicast"])
        # print_configuration(self.streaming_client)

        is_running = self.streaming_client.run()
        if not is_running:
            print("ERROR: Could not start streaming client.")
            print("system end.")
            sys.exit(1)
            # try:
            #     sys.exit(1)
            # except SystemExit:
            #     print("...")
            # finally:
            #     print("exiting")

        time.sleep(1)
        if self.streaming_client.connected() is False:
            print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
            print("system end.")
            sys.exit(1)
            # try:
            #     sys.exit(1)
            # except SystemExit:
            #     print("...")
            # finally:
            #     print("exiting")

    def getHand(self, key) -> HandData:
        if isinstance(key, str):
            return self.hands_dict[key]
        else:
            i = ['l', 'r'][key]
            return self.hands_dict[i]

    def calibrationListener(self, mocap_data: MoCapData):
        self.current_mocap_data = mocap_data

    def getEnoughData(self) -> MoCapData:
        data = self.getCurrentData()
        while not self.judgeDataComplete(data):
            print("Sorry, the system is not ready\nPush Enter key again\n")
            sys.stdin.readline()
            data = self.getCurrentData()
        return data

    def getCurrentData(self) -> MoCapData:
        return copy.deepcopy(self.current_mocap_data)

    # 手の数が2かつ指のマーカーの数が6
    def judgeDataComplete(self, mocap_data: MoCapData):
        try:
            judge = mocap_data.rigid_body_data.get_rigid_body_count() == 2 and mocap_data.rigid_body_data.getRigidbody(
                0).tracking_valid and mocap_data.rigid_body_data.getRigidbody(
                0).tracking_valid and mocap_data.marker_set_data.unlabeled_markers.get_num_points() == len(
                HandData().fingers_pos) * 2

            if not judge:
                # 直前までマーカがロストしておらず，かつロストしているマーカーの数が1つの時，復帰後のマーカーラベルを設定し，マーカーをロストしていないこととする．
                if not self.is_resetted and not self.need_calibration and mocap_data.marker_set_data.unlabeled_markers.get_num_points() == len(
                        HandData().fingers_pos) * 2 - 1:
                    self.is_resetted = True
                    lost_finger = self.searchLostFinger(mocap_data.marker_set_data.unlabeled_markers.marker_list)
                    for i in range(len(self.marker_label_list)):
                        if self.marker_label_list[i] > self.marker_label_list[lost_finger]:
                            self.marker_label_list[i] = self.marker_label_list[i] - 1
                    self.marker_label_list[lost_finger] = finger_labels.__len__() * 2

                elif mocap_data.marker_set_data.unlabeled_markers.get_num_points() < len(HandData().fingers_pos) * 2 - 1:
                    self.need_calibration = True
            else:
                self.is_resetted = False
        except AttributeError:
            judge = False
        return judge

    # ロストしたマーカーの指のラベルを返す
    def searchLostFinger(self, marker_list) -> int:
        # search_list = [-1] * finger_labels.__len__() * 2
        mal = [-1] * (finger_labels.__len__() * 2)  # marker_assign_list
        for i, id in enumerate(self.marker_label_list):
            mal[id - 1] = i

        for marker in marker_list:
            marker_pos = np.array(marker.pos)
            origin_finger = mal[marker.id_num - 1]
            if origin_finger < len(finger_labels):
                hand_pos = np.array(self.hands_dict['l'].fingers_pos[origin_finger])
                marker_pos = marker_pos - np.array(self.hands_dict['l'].position_offset)
            else:
                hand_pos = np.array(self.hands_dict['r'].fingers_pos[origin_finger - len(finger_labels)])
                marker_pos = marker_pos - np.array(self.hands_dict['r'].position_offset)
            marker_pos = marker_pos * 1000
            origin_dist = math.dist(hand_pos, marker_pos)

            marker_pos = np.array(marker.pos)
            venv_finger = mal[marker.id_num]
            if venv_finger < len(finger_labels):
                hand_pos = np.array(self.hands_dict['l'].fingers_pos[venv_finger])
                marker_pos = marker_pos - np.array(self.hands_dict['l'].position_offset)
            else:
                hand_pos = np.array(self.hands_dict['r'].fingers_pos[venv_finger - len(finger_labels)])
                marker_pos = marker_pos - np.array(self.hands_dict['r'].position_offset)

            marker_pos = marker_pos * 1000
            venv_dist = math.dist(hand_pos, marker_pos)

            if origin_dist > venv_dist:
                return origin_finger

        return len(self.marker_label_list) - 1

    def printHandData(self, hand: HandData):
        tab = "  "
        print("\n----------hand data----------")
        print("hand type: {}".format("Left" if hand.is_left else "Right"))
        print("{}pos: {}, {}, {}".format(tab, hand.position[0], hand.position[1], hand.position[2]))
        print(
            "{}rot: {}, {}, {}, {}".format(tab, hand.rotation[0], hand.rotation[1], hand.rotation[2], hand.rotation[3]))
        print("{}finger:".format(tab))
        print("{}thumb: {}, {}, {}".format(tab * 2, hand.fingers_pos[0][0], hand.fingers_pos[0][1],
                                           hand.fingers_pos[0][2]))
        print("{}index: {}, {}, {}".format(tab * 2, hand.fingers_pos[1][0], hand.fingers_pos[1][1],
                                           hand.fingers_pos[1][2]))
        print("{}pinky: {}, {}, {}".format(tab * 2, hand.fingers_pos[2][0], hand.fingers_pos[2][1],
                                           hand.fingers_pos[2][2]))

    def do_calibration(self):
        print("Do caribration")
        self.streaming_client.new_frame_listener = self.calibrationListener
        print("Please stay hand on home position\nPush Enter key")
        sys.stdin.readline()
        mocap_data = self.getEnoughData()
        self.settingRigidbody(mocap_data)
        self.calibrateUnlabeledMarkerID(mocap_data)

        print("Complete both hands setting calibration!")

        # self.settingScrean()
        print("\nComplete caribration")

    def setStartTimestamp(self, mocap_data: MoCapData = None):
        if mocap_data is not None:
            self.start_timestamp = mocap_data.suffix_data.timestamp
        else:
            self.start_timestamp = self.getCurrentData().suffix_data.timestamp

    def settingScrean(self):
        # 画面領域を決定
        print("\nNext, screan size caribration")
        print("Point to upper-left on display\nPush Enter key")
        sys.stdin.readline()
        mocap_data = self.getEnoughData()
        self.setHandData(mocap_data)
        # TODO: 左右どちらの手にするかは要チェック基本左手
        dis_ul = self.hands_dict['l'].fingers_pos[1]
        print(dis_ul)

        print("Point to lower-left on display\nPush Enter key")
        sys.stdin.readline()
        mocap_data = self.getEnoughData()
        self.setHandData(mocap_data)
        dis_ll = self.hands_dict['l'].fingers_pos[1]
        print(dis_ll)

        print("Point to upper-right on display\nPush Enter key")
        sys.stdin.readline()
        mocap_data = self.getEnoughData()
        self.setHandData(mocap_data)
        dis_lr = self.hands_dict['l'].fingers_pos[1]
        print(dis_lr)

        print("Point to lower-right on display\nPush Enter key")
        sys.stdin.readline()
        mocap_data = self.getEnoughData()
        self.setHandData(mocap_data)
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

    def calibrateUnlabeledMarkerID(self, mocap_data: MoCapData):
        if mocap_data.marker_set_data.unlabeled_markers.get_num_points() == len(HandData().fingers_pos) * 2:
            self.marker_label_list = [-1] * (HandData().fingers_pos.__len__() * 2)
            marker_pos_x_list = []
            marker_list = mocap_data.marker_set_data.unlabeled_markers.marker_list
            for marker in marker_list:
                marker_pos_x_list.append(marker.pos[0])
            sorted_list = sorted(marker_pos_x_list)
            # print("\n------ hand finger label -------")
            for key in range(len(marker_pos_x_list)):
                for id in range(len(marker_pos_x_list)):
                    if sorted_list[key] == (marker_pos_x_list[id]):
                        if key < len(HandData().fingers_pos):
                            # print(" left {}: {}".format(finger_labels[abs(key - len(HandData().fingers_pos) + 1)], id+1))
                            self.marker_label_list[abs(key - len(HandData().fingers_pos) + 1)] = id + 1
                        else:
                            # print("right {}: {}".format(finger_labels[key % len(HandData().fingers_pos)], id+1))
                            self.marker_label_list[key] = id + 1
            self.need_calibration = False

    def settingRigidbody(self, mocap_data: MoCapData):
        # rigidbodyIDを登録 < type_hands[rididbody.num_id] = 'l'>
        leftHand: RigidBody = mocap_data.rigid_body_data.getRigidbody(0)
        rightHand: RigidBody = mocap_data.rigid_body_data.getRigidbody(1)
        if leftHand.pos[0] > rightHand.pos[0]:
            leftHand, rightHand = rightHand, leftHand

        self.hands_dict['l'].rb_id = leftHand.id_num
        self.hands_dict['l'].setOffset(leftHand.pos, leftHand.rot)
        self.hands_dict['r'].rb_id = rightHand.id_num
        self.hands_dict['r'].setOffset(rightHand.pos, rightHand.rot)

    def setHandData(self, mocap_data: MoCapData):
        if self.start_timestamp < 0:
            self.setStartTimestamp(mocap_data=mocap_data)
        self.hands_dict['l'].timestamp = mocap_data.suffix_data.timestamp - self.start_timestamp
        self.hands_dict['r'].timestamp = mocap_data.suffix_data.timestamp - self.start_timestamp
        for body in mocap_data.rigid_body_data.rigid_body_list:
            if self.hands_dict['l'].rb_id == body.id_num:
                self.hands_dict['l'].setHand(body)
            elif self.hands_dict['r'].rb_id == body.id_num:
                self.hands_dict['r'].setHand(body)

        marker_list = mocap_data.marker_set_data.unlabeled_markers.marker_list
        for i, id in enumerate(self.marker_label_list):
            if i < len(finger_labels):
                self.hands_dict['l'].setFingerPos(finger_type=i, marker_pos=marker_list[id - 1].pos)
            else:
                self.hands_dict['r'].setFingerPos(finger_type=i - len(finger_labels),
                                                  marker_pos=marker_list[id - 1].pos)
                
    def restart(self):
        self.streaming_client.restart()
        self.start_timestamp = -1
        
    def stop(self):
        self.streaming_client.stop()
        
    def shutdown(self):
        self.streaming_client.shutdown()
        time.sleep(0.2)
        print("OptiTrack exit safely")
    