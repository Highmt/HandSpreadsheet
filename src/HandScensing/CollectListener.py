import copy
import sys
import time
from pathlib import Path

import pandas as pd
from datetime import datetime

from res.SSEnum import HandEnum, FeatureEnum
from src.HandScensing.HandListener import HandListener, Y_THRESHOLD
from src.UDP.MoCapData import MoCapData
from src.UDP.NatNetClient import NatNetClient

version = "test2"
# 　収集する手形状のラベル（）
labels = HandEnum.NAME_LIST.value
streaming_client = NatNetClient()
collect_data_num = 10000
finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]
output_dir = "../../res/data/{}".format(version)


class CollectListener(HandListener):
    def __init__(self):
        super().__init__()
        self.current_collect_id = 0
        self.enables = [False, False]
        self.dfs = []
        self.started = False

        # ディレクトリが存在しない場合作成
        dir = Path(output_dir)
        dir.mkdir(parents=True, exist_ok=True)
        self.reset_df()
        # TODO: change mode to 'x' for study
        self.dfs[0].to_csv("{}/leftData.csv".format(output_dir), mode='w')
        self.dfs[1].to_csv("{}/rightData.csv".format(output_dir), mode='w')

    def reset_df(self):
        self.dfs = [pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value), pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)]

    def frameListener(self, mocap_data: MoCapData):
        # 最初の数秒間のフレームをカットする
        if not self.started:
            return

        if self.judgeDataComplete(mocap_data=mocap_data):
            if self.need_calibration:
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)

            self.setHandData(mocap_data=mocap_data)
            for hand in self.hands_dict.values():
                lr_label, lr = ("left", 0) if hand.is_left else ("right", 1)
                # 収集する手に一致していない場合とその手の位置が閾値より低い場合スキップ
                if self.enables[lr] and hand.position[1] > Y_THRESHOLD:
                    ps = pd.Series(dtype=pd.Float64Dtype, index=FeatureEnum.FEATURE_LIST.value)
                    # Get the hand's normal vector and direction
                    # self.printHandData(hand)
                    print("{}: {}".format(lr_label, len(self.dfs[lr])))
                    ps["pitch", "roll", "yaw"] = hand.rotation[0:3]

                    # Get fingers
                    for finger_id in range(len(hand.fingers_pos)):
                        for pos in range(3):
                            ps[finger_labels[finger_id] + "_dir_" + pos_labels[pos]] = hand.fingers_pos[finger_id][
                                                                                           pos] - hand.position[pos]
                            ps[finger_labels[finger_id] + "_" + finger_labels[(finger_id + 1) % 3] + "_" + pos_labels[
                                pos]] = hand.fingers_pos[finger_id][pos] - hand.fingers_pos[(finger_id + 1) % 3][pos]

                    # 　データ収集が完了すると終了

                    self.dfs[lr] = self.dfs[lr].append(ps, ignore_index=True)
                    if (len(self.dfs[lr]) >= collect_data_num):
                        self.enables[lr] = False
                        self.data_save_pandas(lr=lr_label, data=copy.deepcopy(self.dfs[lr]))
                        print("Finished to collect {} shape {} hand data".format(labels[self.current_collect_id], lr_label))

            # 両手が閾値以下の位置にある時ラベルの再設定処理を回す
            if self.hands_dict['l'].position[1] <= Y_THRESHOLD and self.hands_dict['r'].position[1] <= Y_THRESHOLD:
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
                print(".")

        if not (self.enables[0] or self.enables[1]):
            self.streaming_client.stop()
            self.started = False
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

    # for lr in range(2):
    #     print("First, use left hand" if lr == 0 else "Next, use right hand")
    print("use both hand")
    for label_id in range(len(labels)):
        listener.reset_df()
        listener.current_collect_id = label_id
        print("Please make {} hand shape".format(labels[label_id]))
        print("Press Enter key to start")
        listener.enables = [True, True]
        sys.stdin.readline()
        listener.streaming_client.restart()
        time.sleep(0.5)
        print("-------GO--------")
        listener.started = True
        sys.stdin.readline()

    # Keep this process running until Enter is pressed
    # Remove the sample listener when done
    listener.streaming_client.shutdown()


if __name__ == "__main__":
    main()
