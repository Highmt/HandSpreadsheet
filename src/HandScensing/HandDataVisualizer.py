import copy
import sys
import time

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt

from src.HandScensing.HandListener import HandData
from src.UDP.MoCapData import MoCapData

version = "data1"
# 　収集する手形状のラベル（）

lr_label = ['left', 'right']
data_pass = '../../res/data/study1/saved/{}'.format(version)
def live_plotter(y_data, lines, pause_time=0.01):
    # after the figure, axis, and line are created, we only need to update the y-data
    for i in range(len(lines)):
        lines[i].set_ydata(y_data[i])
    # adjust limits if new data goes beyond bounds
    plt.draw()
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return lines


def fingerDifferencial(former_hand: HandData, hand: HandData):
    d = []
    for i in range(len(HandData().fingers_pos)):
        d.append(np.linalg.norm(former_hand.getFingerVec(i) - hand.getFingerVec(i)))
    a = sum(d) / len(d) # とりあえず平均値を返している
    return a

def convertHandDataList(data: pd.DataFrame) -> []:
    list = []
    for i, ps in data.iterrows():
        hand = HandData()
        hand.loadPS(ps)
        list.append(hand)
    return list

def main():
    # section ごと
    sec = 0
    dir = "{}/sec_{}".format(data_pass, sec)

    read_data = [pd.DataFrame(), pd.DataFrame()]
    # TODO: split for operation
    time_df = pd.read_csv(dir + '/timeData.csv', sep=',', index_col=0)
    handlist = []
    x_vec = []
    y_vec = [[], []]
    line = [[], []]

    fig = plt.figure(figsize=(15, 9))
    ax = [fig.add_subplot(211), fig.add_subplot(212)]
    y_scale = 600
    # create a variable for the line so we can later update it
    line_name = ["x", "y", "z", "d"]
    legend = []
    # 左右ごと
    for lr, lr_name in enumerate(lr_label):
        read_data[lr] = pd.read_csv(dir + '/' + lr_name + 'Data.csv', sep=',', index_col=0)
        handlist.append(convertHandDataList(read_data[lr]))

        x_vec.append(read_data[lr]["timestamp"])

        # 軸ごと
        for axis in range(len(line_name) - 1):
            y_vec[lr].append(read_data[lr][line_name[axis]])
            if axis in [1]:
                line[lr].append(ax[lr].plot(x_vec[lr], y_vec[lr][axis], '-', alpha=0.8)[0])
                legend.append(line_name[axis])

        # データごと
        y_vec[lr].append([])
        former_hand = HandData()
        for hand in handlist[lr]:
            d = fingerDifferencial(former_hand, hand)
            y_vec[lr][3].append(d)
            former_hand = copy.deepcopy(hand)

        line[lr].append(ax[lr].plot(x_vec[lr], y_vec[lr][3], '-', alpha=0.8)[0])
        legend.append(line_name[3])
        ax[lr].set_ylim(ymax=y_scale, ymin=-50)
        ax[lr].legend(legend)


    # update plot label/title
    plt.ylabel('Y Label')
    plt.title('Title: {}'.format('Realtime'))
    plt.show()
    # use ggplot style for more sophisticated visuals
    # plt.style.use('ggplot')


    dif_memory_num = 3
    dif_memory = [np.zeros(dif_memory_num), np.zeros(dif_memory_num)]

if __name__ == "__main__":
    main()
