################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import copy
import sys
from pathlib import Path

import pandas as pd
from datetime import datetime

from res.SSEnum import HandEnum, FeatureEnum
from src.HandScensing.HandListener import HandListener, Y_THRESHOLD
from src.UDP.MoCapData import MoCapData
from src.UDP.NatNetClient import NatNetClient

version = "test"
#　収集する手形状のラベル（）
labels = HandEnum.NAME_LIST.value
streaming_client = NatNetClient()
collect_data_num = 200
finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]
output_dir = "../../res/data/{}".format(version)

class CollectListener(HandListener):
    def __init__(self):
        super().__init__()
        self.current_collect_id = 0
        self.enables = [False, False]
        self.df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)

        # ディレクトリが存在しない場合作成
        dir = Path(output_dir)
        dir.mkdir(parents=True, exist_ok=True)
        # TODO: change mode to 'x' for study
        self.df.to_csv("{}/leftData.csv".format(output_dir), mode='w')
        self.df.to_csv("{}/rightData.csv".format(output_dir), mode='w')

    def reset_df(self):
        self.df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)

    def frameListener(self, mocap_data: MoCapData):
        # Get the most recent frame and report some basic information
        if self.judgeDataComplete(mocap_data=mocap_data):
            if self.is_markerlosted:
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)

            self.setHandData(mocap_data=mocap_data)
            for hand in self.hands_dict.values():

                # 収集する手に一致していない場合とその手の位置が閾値より低い場合スキップ
                if (self.enables[0] if hand.is_left else self.enables[1]) and hand.position[1] > Y_THRESHOLD:
                    ps = pd.Series(index=FeatureEnum.FEATURE_LIST.value)
                    # Get the hand's normal vector and direction
                    # self.printHandData(hand)
                    print(len(self.df))
                    ps["pitch", "roll", "yaw"] = hand.rotation[0:3]

                    # Get fingers
                    # TODO: 位置は除外
                    for finger_id in range(len(hand.fingers_pos)):
                        for pos in range(3):
                            ps[finger_labels[finger_id] + "_dir_" + pos_labels[pos]] = hand.fingers_pos[finger_id][pos] - hand.position[pos]
                            ps[finger_labels[finger_id] + "_" + finger_labels[(finger_id + 1) % 3] + "_" + pos_labels[pos]] = hand.fingers_pos[finger_id][pos] - hand.fingers_pos[(finger_id + 1) % 3][pos]

                    # 　データ収集が完了すると終了

                    self.df = self.df.append(ps, ignore_index=True)
                    if (len(self.df) >= collect_data_num):
                        (lr, i) = ("left", 0) if hand.is_left else ("right", 1)
                        self.enables[i] = False
                        self.data_save_pandas(lr=lr, data=copy.deepcopy(self.df))
                        print("Finished to correct {} shape {} hand data".format(labels[self.current_collect_id], lr))
                        self.reset_df()


            # 両手が閾値以下の位置にある時ラベルの再設定処理を回す
            if self.hands_dict['l'].position[1] <= Y_THRESHOLD and self.hands_dict['r'].position[1] <= Y_THRESHOLD:
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)
                print(".")

        else:
            self.is_markerlosted = True

        if not (self.enables[0] or self.enables[1]):
            self.streaming_client.stop()
            print("Saved data\nPlease press Enter key for next")

    def data_save_pandas(self, lr: str, data: pd.DataFrame):
        data["Label"] = self.current_collect_id
        data.to_csv("{}/{}Data.csv".format(output_dir, lr), mode='a', header=False)

    def setListener(self):
        self.streaming_client.new_frame_listener = self.frameListener

def main():
    listener = CollectListener()
    listener.initOptiTrack()
    listener.do_calibration()
    listener.streaming_client.stop()
    listener.setListener()

    # Have the sample listener receive events from the controller
    print("Press Enter to start collecting hand data session")
    sys.stdin.readline()
    print("First, use left hand")
    for label_id in range(len(labels)):
        listener.current_collect_id = label_id
        print("Please make {} hand shape".format(labels[label_id]))
        print("Press Enter key to start")
        listener.enables[0] = True
        listener.enables[1] = False
        sys.stdin.readline()
        listener.streaming_client.restart()
        sys.stdin.readline()

    print("Next, use right hand")
    for label_id in range(len(labels)):
        listener.current_collect_id = label_id
        print("Please make {} hand shape".format(labels[label_id]))
        print("Press Enter key to start")
        listener.enables[0] = False
        listener.enables[1] = True
        sys.stdin.readline()
        listener.streaming_client.restart()
        sys.stdin.readline()


    # Keep this process running until Enter is pressed
    # Remove the sample listener when done
    listener.streaming_client.shutdown()


if __name__ == "__main__":
    main()
