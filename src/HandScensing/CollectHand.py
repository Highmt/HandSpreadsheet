################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import copy
import sys

import pandas as pd
from datetime import datetime

from res.SSEnum import HandEnum, FeatureEnum
from src.HandScensing.HandListener import HandListener
from src.UDP.MoCapData import MoCapData
from src.UDP.NatNetClient import NatNetClient

version = "master"
#　収集する手形状のラベル（）
labels = HandEnum.NAME_LIST.value
streaming_client = NatNetClient()
collect_data_num = 2000
z_threshold = 30
finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]


class CollectListener(HandListener):
    def __init__(self):
        super().__init__()
        self.current_correct_id = 0
        self.enables = [False, False]
        self.dfs = [pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value), pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)]
        self.dfs[0].to_csv("../../res/data/leftData_{}.csv".format(version), mode='w')
        self.dfs[1].to_csv("../../res/data/rightData_{}.csv".format(version), mode='w')

    def reset_df(self):
        self.left_df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
        self.right_df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def frameListener(self, mocap_data: MoCapData):
        # Get the most recent frame and report some basic information
        if self.judgeDataComplete(mocap_data=mocap_data):
            self.setHandData(mocap_data=mocap_data)

            for hand in self.hands_dict.values():
                # 収集する手に一致していない場合とその手の位置が閾値より低い場合スキップ
                if (hand.is_left and self.left_enable or not hand.is_left and self.right_enable) and \
                        hand.position[2] < z_threshold:
                    continue

                print("timestamp: %d" %(mocap_data.suffix_data.timestamp))
                ps = pd.Series(index=FeatureEnum.FEATURE_LIST.value)
                # Get the hand's normal vector and direction

                ps["position_x", "position_y", "position_z"] = hand.position
                ps["pitch", "roll", "yaw"] = hand.rotation
                # Calculate the hand's pitch, roll, and yaw angles

                # Get fingers
                for finger_id in len(hand.fingers_pos):
                    for pos in range(3):
                        ps[finger_labels[finger_id] + "_pos_" + pos_labels[pos]] = hand.fingers_pos[pos]
                        ps[finger_labels[finger_id] + "dir" + pos_labels[pos]] = hand.fingers_pos[pos] - hand.position[pos]

                # 　データ収集が完了すると終了
                if hand.is_left:
                    self.dfs[0] = self.dfs[0].append(ps, ignore_index=True)
                    if (len(self.dfs[0]) >= collect_data_num):
                        self.enables[0] = False
                        self.data_save_pandas(lr="left", data=copy.deepcopy(self.dfs[0]))
                        print("Finished to correct {} shape {} hand data".format(labels[self.current_correct_id], "left"))
                else:
                    self.dfs[1] = self.dfs[1].append(ps, ignore_index=True)
                    if (len(self.dfs[1]) >= collect_data_num):
                        self.enables[1] = False
                        self.data_save_pandas(lr="right", data=copy.deepcopy(self.dfs[1]))
                        print("Finished to correct {} shape {} hand data".format(labels[self.current_correct_id], "right"))

        if not (self.enables[0] or self.enables[1]):
            self.streaming_client.stop()
            print("Finished to correct {} shape data\nPlease press Enter key for next".format(labels[self.current_correct_id]))

    def data_save_pandas(self, lr: str, data: pd.DataFrame):
        data["label"] = self.current_correct_id
        data.to_csv("../../res/data/{}Data_{}.csv".format(lr, version), mode='a', header=False)

def main():
    listener = CollectListener()
    listener.initOptiTrack()
    listener.do_calibration()
    listener.streaming_client.stop()
    listener.streaming_client.new_frame_listener = listener.frameListener

    # Have the sample listener receive events from the controller
    print("Press Enter to start collecting hand data")
    sys.stdin.readline()
    for label_id in range(len(labels)):
        listener.current_correct_id = label_id
        print("Please make {} hand shape".format(labels[label_id]))
        listener.enables[0] = True
        listener.enables[1] = True
        if label_id == HandEnum.FREE.value:
            print("First, use left hand")
            print("Press Enter key to start")
            listener.enables[0] = True
            listener.enables[1] = False
            sys.stdin.readline()
            listener.streaming_client.restart()
            sys.stdin.readline()

            print("Next, use right hand")
            print("Press Enter key to start")
            listener.enables[0] = False
            listener.enables[1] = True
            sys.stdin.readline()
            listener.streaming_client.restart()
            sys.stdin.readline()
        else:
            print("use both hands at same time")
            print("Press Enter key to start")
            sys.stdin.readline()
            listener.streaming_client.restart()
            sys.stdin.readline()


    # Keep this process running until Enter is pressed
    # Remove the sample listener when done
    streaming_client.shutdown()


if __name__ == "__main__":
    main()
