import csv

import sys
import time

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

from res.SSEnum import HandEnum
from src.HandScensing.HandListener import HandListener, Y_THRESHOLD
from src.HandScensing.Predictor import Predictor
from src.UDP.MoCapData import MoCapData

np.set_printoptions(suppress=True)

# "KNN", "SVC" or "NN"
model = "NN"
ver = "test2"
collect_data_num = 500
lr = ["left", "right"]


# for result
# curl -X POST -H "Content-Type: application/json" -d '{"45":{"x":-117,"y":-472,"z":-29},"47":{"x":-987,"y":-49,"z":-1524},"label":6}' localhost:8080


class TestListener(HandListener):
    def __init__(self):
        super(TestListener, self).__init__()
        self.true_label = 0
        self.data_count = 0
        self.predictor = Predictor(alg=model, ver=ver)
        self.pred_list = [[], []]
        self.true_list = [[], []]
        self.lr = 0
        self.started = False

    def resetList(self):
        self.pred_list = [[], []]
        self.true_list = [[], []]

    def frameListener(self, mocap_data: MoCapData):
        # 　データ収集が完了すると終了
        if (self.data_count >= collect_data_num):
            print("\n\n\n\n\n\nPush Enter to Finish")
            self.started = False
            self.streaming_client.stop()
            return

        # 最初の数秒間のフレームをカットする
        if not self.started:
            return

        if self.judgeDataComplete(mocap_data):
            if self.need_calibration:
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
            # フレームデータから手のデータを抽出
            self.setHandData(mocap_data)

            # 左右両方の手の位置が閾値より低い時マーカ再設定
            if self.hands_dict['l'].position[1] <= Y_THRESHOLD and self.hands_dict['r'].position[1] <= Y_THRESHOLD:
                self.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
                return

            for key in self.hands_dict.keys():
                if self.hands_dict.get(key).position[1] > Y_THRESHOLD and self.data_count < collect_data_num:
                    self.data_count = self.data_count + 1
                    pred = self.predictor.handPredict(hand=self.hands_dict.get(key))  # 学習機で手形状識別
                    self.pred_list[self.lr].append(pred)
                    self.true_list[self.lr].append(self.true_label)
                    print(pred)

    def setListener(self):
        self.streaming_client.new_frame_listener = self.frameListener


def main():
    # Create a sample listener and controller
    listener = TestListener()
    listener.initOptiTrack()
    listener.do_calibration()
    listener.streaming_client.stop()
    listener.setListener()

    # Have the sample listener receive events from the controller

    labels = HandEnum.NAME_LIST.value
    # Keep this process running until Enter is pressed
    fig = plt.figure(figsize=(10, 5))
    ax = [fig.add_subplot(121), fig.add_subplot(122)]
    try:
        for i in range(2):
            listener.lr = i
            listener.resetList()
            for true_label in range(len(labels)):
                listener.true_label = true_label
                print("Press Enter to start sensing hand")
                print("Please make {} shape with {} hand".format(labels[true_label], lr[i]))
                listener.data_count = 0
                sys.stdin.readline()
                listener.streaming_client.restart()
                time.sleep(0.5)
                print("------GO-------")
                listener.started = True
                sys.stdin.readline()

            c_matrix = confusion_matrix(listener.true_list[i], listener.pred_list[i])
            print(c_matrix)
            cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
            sum = int(listener.true_list[i].__len__()) / int(labels.__len__())  # 各ラベルの数
            sns.heatmap(cm_pd / sum, annot=True, cmap="Blues", fmt='.4g', ax=ax[i])  # 正規化したものを表示
            with open('../../res/learningResult/{}testCM_{}.csv'.format(lr[i], model), 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(c_matrix)
            print(classification_report(listener.true_list[i], listener.pred_list[i]))
            print("正答率 = {}\n\n".format(metrics.accuracy_score(listener.true_list[i], listener.pred_list[i])))

        try:
            # TODO: グラフの見た目修正（タイトル，軸目盛りなど）
            plt.savefig('../../res/learningResult/testCM_{}.png'.format(model))
            plt.show()
        except KeyboardInterrupt:
            print("terminate normally")

        finally:
            sys.exit(0)

    except:
        print("Error")
        sys.exit(1)

    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
