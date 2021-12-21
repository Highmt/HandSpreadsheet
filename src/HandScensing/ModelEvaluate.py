import csv

import sys
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
training_data = np.empty([0, 7])
model = "KNN"
collect_data_num = 1000


# for result
# curl -X POST -H "Content-Type: application/json" -d '{"45":{"x":-117,"y":-472,"z":-29},"47":{"x":-987,"y":-49,"z":-1524},"label":6}' localhost:8080



class TestListener(HandListener):
    def __init__(self):
        super(TestListener, self).__init__()
        self.true_label = 0
        self.data_count = 0
        self.predictor = Predictor(model)
        self.pred_list = [[], []]
        self.true_list = [[], []]
        self.lr = 0

    def resetList(self):
        self.pred_list = [[], []]
        self.true_list = [[], []]

    def frameListener(self, mocap_data: MoCapData):
        if self.judgeDataComplete(mocap_data):
            if self.is_markerlosted:
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)
            # フレームデータから手のデータを抽出
            self.setHandData(mocap_data)

            # 左右両方の手の位置が閾値より低い時マーカ再設定
            if self.hands_dict['l'].position[1] <= Y_THRESHOLD and self.hands_dict['r'].position[1] <= Y_THRESHOLD:
                self.settingUnlabeledMarkerID(mocap_data=mocap_data)
                return

            for key in self.hands_dict.keys():
                if self.hands_dict.get(key).position[1] > Y_THRESHOLD:
                    self.data_count = self.data_count + 1
                    pred = self.predictor.handPredict(hand=self.hands_dict.get(key))  # 学習機で手形状識別
                    self.pred_list[self.lr].append(pred)
                    self.true_list[self.lr].append(self.true_label)
                    print(pred)

            #　データ収集が完了すると終了
            if(self.data_count >= collect_data_num):
                print("\n\n\n\n\n\nPush Enter to Finish")
                self.streaming_client.stop()

        else:
            self.is_markerlosted = True

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
    try:
        for i in range(2):
            listener.lr = i
            listener.resetList()
            for true_label in range(len(labels)):
                listener.true_label = true_label
                print("Press Enter to start sensing hand")
                print("Please make {} hand".format(labels[true_label]))
                listener.data_count = 0
                sys.stdin.readline()
                listener.streaming_client.restart()
                sys.stdin.readline()

            c_matrix = confusion_matrix(listener.true_list[i], listener.pred_list[i])
            print(c_matrix)
            cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
            sum = int(listener.true_list[i].__len__()) / int(labels.__len__())  # 各ラベルの数
            fig, ax = plt.subplots(figsize=(8, 7))
            sns.heatmap(cm_pd / sum, annot=True, cmap="Blues", fmt='.4g', ax=ax)  # 正規化したものを表示
            plt.savefig('../../res/learningResult/testCM_{}.png'.format(model))
            with open('../../res/learningResult/testCM_{}.csv'.format(model), 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(c_matrix)
            print(classification_report(listener.true_list[i], listener.pred_list[i]))
            print("正答率 = ", metrics.accuracy_score(listener.true_list[i], listener.pred_list[i]))
            plt.show()

    except:
        print("Error")

    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
