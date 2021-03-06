import csv

import sys
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

from lib.LeapMotion.Leap import Controller, Listener
from res.SSEnum import HandEnum
from src.HandScensing.Predictor import Predictor

np.set_printoptions(suppress=True)
training_data = np.empty([0, 7])
model = "KNN_a0"
predictor = Predictor(model)
collect_data_num = 1000
pred_list = []
true_list = []


# for result
# curl -X POST -H "Content-Type: application/json" -d '{"45":{"x":-117,"y":-472,"z":-29},"47":{"x":-987,"y":-49,"z":-1524},"label":6}' localhost:8080



class TestListener(Listener):
    def __init__(self):
        super(TestListener, self).__init__()
        self.true_label = 0
        self.data_count = 0

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        #　データ収集が完了すると終了
        if(self.data_count >= collect_data_num):
            controller.remove_listener(self)
            print("\n\n\n\n\n\nPush Enter to Finish")

        for hand in frame.hands:
            self.data_count = self.data_count + 1
            pred = predictor.handPredict(hand)
            pred_list.append(pred)
            true_list.append(self.true_label)
            print(pred)
            # print(predictor.dfs)

def main():
    # Create a sample listener and controller
    listener = TestListener()
    controller = Controller()

    # Have the sample listener receive events from the controller

    labels = HandEnum.NAME_LIST.value
    # Keep this process running until Enter is pressed
    for true_label in range(0, len(labels)):
        listener.true_label = true_label
        print("Press Enter to start sensing hand")
        print("Please make {} hand".format(labels.__getitem__(true_label)))
        print("Press Enter again to next when stop")
        sys.stdin.readline()
        listener.data_count = 0
        controller.add_listener(listener)
        sys.stdin.readline()


    c_matrix = confusion_matrix(true_list, pred_list)
    print(c_matrix)
    cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
    sum = int(true_list.__len__()) / int(labels.__len__())  # 各ラベルの数
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(cm_pd / sum, annot=True, cmap="Blues", fmt='.4g', ax=ax)  # 正規化したものを表示
    plt.savefig('../../res/learningResult/testCM_{}.png'.format(model))
    with open('../../res/learningResult/testCM_{}.csv'.format(model), 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(c_matrix)
    print(classification_report(true_list, pred_list))
    print("正答率 = ", metrics.accuracy_score(true_list, pred_list))


if __name__ == "__main__":
    main()
