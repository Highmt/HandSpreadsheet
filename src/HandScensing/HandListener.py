import copy
import sys
import pyautogui


from src.UDP.MoCapData import MoCapData, RigidBody
from src.UDP.NatNetClient import NatNetClient

DIS_SIZE = pyautogui.size()
Y_THRESHOLD = 0.2
def print_configuration(natnet_client: NatNetClient):
    print("Connection Configuration:")
    print("  Client:          %s"% natnet_client.local_ip_address)
    print("  Server:          %s"% natnet_client.server_ip_address)
    print("  Command Port:    %d"% natnet_client.command_port)
    print("  Data Port:       %d"% natnet_client.data_port)

    if natnet_client.use_multicast:
        print("  Using Multicast")
        print("  Multicast Group: %s"% natnet_client.multicast_address)
    else:
        print("  Using Unicast")

    #NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" %(application_name))
    print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1], \
                                             nat_net_requested_version[2], nat_net_requested_version[3]))
    #print("command_socket = %s"%(str(natnet_client.command_socket)))
    #print("data_socket    = %s"%(str(natnet_client.data_socket)))

class HandData:
    def __init__(self, is_left: bool = None):
        self.rb_id = 0
        self.is_left = is_left
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]
        self.finger_marker_dict = {}
        self.fingers_pos = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]


    def setPalm(self, rigid_body: RigidBody):
        self.position = rigid_body.pos
        self.rotation = rigid_body.rot

    def setFingerMarkerDict(self, key, value):
        self.finger_marker_dict[key] = value

    def setFingerPos(self, marker_list, offset):
        for marker in marker_list:
            if marker.id_num in self.finger_marker_dict.keys():
                for axis in range(len(offset)):
                    self.fingers_pos[self.finger_marker_dict[marker.id_num]][axis] = marker.pos[axis] - offset[axis]

    def getFingerPos(self, finger_id: int):
        return self.fingers_pos[self.finger_marker_dict[finger_id]]

    # TODO: マーカーロストの処理

class HandListener:
    def __init__(self):
        self.finger_dis_dim = {"up": 0, "low": 0, "left": 0, "right": 0}
        self.finger_dis_size = [0, 0]
        self.current_mocap_data: MoCapData = None
        self.hands_dict = {'l': HandData(is_left=False), 'r': HandData(is_left=False)}
        self.hand_offset = [0.0, 0.0, 0.0]

    def initOptiTrack(self):
        optionsDict = {}
        optionsDict["clientAddress"] = "172.16.0.80"
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


    def calibrationListener(self, mocap_data: MoCapData):
        self.current_mocap_data = mocap_data

    def getCurrentData(self) -> HandData:
        while not self.judgeDataComplete(self.current_mocap_data):
            print("Sorry, the system is not ready\nPush Enter key again\n")
            sys.stdin.readline()
        return copy.deepcopy(self.current_mocap_data)

    def judgeDataComplete(self, mocap_data: MoCapData):
        return mocap_data.rigid_body_data.get_rigid_body_count() < 3 and \
               mocap_data.marker_set_data.unlabeled_markers.get_num_points() == len(HandData().fingers_pos) * 2

    def do_calibration(self):
        print("Do caribration")
        self.streaming_client.new_frame_listener = self.calibrationListener

        print("Please stay hand on home position\nPush Enter key\n")
        sys.stdin.readline()
        mocap_data = self.getCurrentData()
        self.settingRigidbodyID(mocap_data)
        self.settingUnlabeledMarkerID(mocap_data)

        # offsetを設定
        for axis in range(len(self.hand_offset)):
            self.hand_offset[axis] = (self.hands_dict['l'].position[axis] + self.hands_dict['r'].position[axis]) / 2

        print("Complete both hands setting calibration!")

        # self.settingScrean()
        print("\nComplete caribration")

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

    def setHandData(self, mocap_data: MoCapData):
        for body in mocap_data.rigid_body_data.rigid_body_list:
            if self.hands_dict['l'].rb_id == body.id_num:
                self.hands_dict['l'].setPalm(body)
            elif self.hands_dict['r'].rb_id == body.id_num:
                self.hands_dict['r'].setPalm(body)

        marker_list = mocap_data.marker_set_data.unlabeled_markers.marker_list
        self.hands_dict['l'].setFingerPos(marker_list=copy.copy(marker_list), offset=self.hand_offset)
        self.hands_dict['r'].setFingerPos(marker_list=copy.copy(marker_list), offset=self.hand_offset)
