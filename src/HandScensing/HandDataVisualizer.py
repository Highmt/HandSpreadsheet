import copy
import os
import sys
import time

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt

from res.SSEnum import OperationEnum
from src.HandScensing.HandListener import HandData, CALIBRATION_THRESHOLD
from src.UDP.MoCapData import MoCapData

dif_memory_num = 3
lr_label = ['left', 'right']
data_pass = '../../res/data/study1/saved'

def fingerDifferencial(former_hand: HandData, hand: HandData):
    d = []
    for i in range(len(HandData().fingers_pos)):
        d.append(np.linalg.norm(former_hand.getFingerVec(i) - hand.getFingerVec(i)))
    a = sum(d) / len(d) # とりあえず平均値を返している
    return a

def fingerMoveNolm(y_vec: pd.DataFrame) -> np.ndarray:
    d = np.empty(1)
    former = HandData()
    current = HandData()
    former.loadPS(y_vec.iloc(0))
    for i, row in y_vec.iterrows():
        current.loadPS(y_vec.iloc(i))
        d = np.append(d, fingerDifferencial(former, current))
    return d

def convertHandDataList(data: pd.DataFrame) -> []:
    list = []
    for i, ps in data.iterrows():
        hand = HandData()
        hand.loadPS(ps)
        list.append(hand)
    return list

def main():
    # begin 被験者 ----------
    participant = 3
    participant_num = sum(not os.path.isfile(os.path.join(data_pass, name)) for name in os.listdir(data_pass))
    for participant in range(participant_num):
        participant_dir = "{}/data{}".format(data_pass, participant)
        # 被験者の数だけグラフ作成
        fig = plt.figure(figsize=(15, 9))
        plt.suptitle('Hand Y-Position (P{})'.format(participant))

        # 操作の数だけグラフを作成
        ax = [fig.add_subplot(330 + i + 1) for i in range(len(OperationEnum.OperationName_LIST_JP.value))]
        line = [[] for i in range(len(OperationEnum.OperationName_LIST_JP.value))] # 操作分つくる
        y_scale = 600

        # section ごと
        section_num = sum(not os.path.isfile(os.path.join(participant_dir, name)) for name in os.listdir(participant_dir))
        for sec in range(section_num):

            sec_dir = "{}/sec_{}".format(participant_dir, sec)
            read_data = [pd.DataFrame(), pd.DataFrame()]
            # TODO: split for operation
            time_df = pd.read_csv(sec_dir + '/timeData.csv', sep=',', index_col=0)
            time_df = time_df.reset_index(drop=True)
            time_df["operation"] = [OperationEnum.OperationGrid.value[int(p.action)][int(p.direction)] for i, p in time_df[["action", "direction"]].iterrows()]

            # 左右ごと
            for lr, lr_name in enumerate(lr_label):
                read_data[lr] = pd.read_csv(sec_dir + '/' + lr_name + 'Data.csv', sep=',', index_col=0)
                splited_data = read_data[lr].groupby('Label')

                for i in time_df["operation"].index:
                    # y 座標だけ追加
                    op = int(time_df.at[i, "operation"])

                    try:
                        target_vec = splited_data.get_group(i)
                    except:
                        print("p{} sec{} {}Hand: task{} - {}  memorization failed".format(participant, sec, lr_name, i, OperationEnum.OperationName_LIST.value[op]))
                        continue
                    target_vec = target_vec.reset_index(drop=True)
                    d_np = fingerMoveNolm(target_vec)
                    y_vec = target_vec['y']
                    time_vec = target_vec['timestamp']
                    s_time = time_vec[0]
                    n = 0
                    try:
                        while time_vec[n + 1] - s_time > 1 or y_vec[n] > CALIBRATION_THRESHOLD:
                            time_vec = time_vec.drop(n)
                            y_vec = y_vec.drop(n)
                            n = n + 1
                            s_time = time_vec[n]
                    except:
                        print("p{} sec{} {}Hand: task{} - {}   marker tracking failed".format(participant, sec, lr_name, i, OperationEnum.OperationName_LIST.value[op]))
                        continue
                    x_vec = time_vec - s_time
                    line[op].append(ax[op].plot(x_vec, y_vec, '-', alpha=0.8)[0])

                # handlist.append(convertHandDataList(read_data[lr]))

                # データごとに手の位置を計算
                # y_vec[lr].append([])
                # former_hand = HandData()
                # d_memory = np.zeros(dif_memory_num)
                # for hand in handlist[lr]:
                #     d = fingerDifferencial(former_hand, hand)
                #     d_memory = np.delete(np.append(d_memory, d), 0)
                #     y_vec[lr][3].append(sum(d_memory)/dif_memory_num)
                #     former_hand = copy.deepcopy(hand)
                #
                # line[lr].append(ax[lr].plot(x_vec[lr], y_vec[lr][3], 'o', alpha=0.8)[0])
                # legend.append(line_name[3])
                    ax[op].set_ylim(ymax=y_scale, ymin=-50)
                    # ax[lr].legend(["y"])


            # update plot label/title

        for i in range(len(ax)):
            ax[i].set_title(OperationEnum.OperationName_LIST.value[i])
        fig.tight_layout()
    # end 被験者 ------------------------

    plt.show()
    # use ggplot style for more sophisticated visuals
    # plt.style.use('ggplot')

if __name__ == "__main__":
    main()
