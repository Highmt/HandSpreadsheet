import copy
import os
import sys
import time

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt

from res.SSEnum import OperationEnum
from src.HandScensing.HandListener import HandData, CALIBRATION_THRESHOLD, ACTION_THRESHOLD
import japanize_matplotlib
from src.UDP.MoCapData import MoCapData

dif_memory_num = 3
lr_label = ['left', 'right']
data_pass = '../../res/data/study1/saved'

def fingerDifferencial(former_hand: HandData, hand: HandData):
    d = []
    for i in range(len(HandData().fingers_pos)):
        d.append(np.linalg.norm(former_hand.getFingerVec(i) - hand.getFingerVec(i)))
    a = sum(d) / len(d)  # とりあえず平均値を返している
    return a

def fingerMoveNolm(df: pd.DataFrame) -> np.ndarray:
    d = np.empty(0)
    former = HandData()
    current = HandData()
    former.loadPS(df.iloc[0])
    for i, row in df.iterrows():
        current.loadPS(df.iloc[i])
        if current.timestamp - former.timestamp > 0.1:
            print(current.timestamp - former.timestamp)
            d = np.append(d, 0)
        else:
            # d = np.append(d, fingerDifferencial(former, current))
            d = np.append(d, np.linalg.norm(former.getFingerVec(1) - current.getFingerVec(1)))
        former.loadPS(df.iloc[i])
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
    e_record = 0
    e_gestuer = 0

    ###### 被験者の数だけウィンドウを作成 ###########
    # fig = plt.figure(figsize=(15, 9))
    # plt.suptitle('Hand Y-Position')
    # # 操作の数だけグラフを作成
    # ax = [fig.add_subplot(330 + i + 1) for i in range(len(OperationEnum.OperationName_LIST_JP.value))]
    # line = [[] for i in range(len(OperationEnum.OperationName_LIST_JP.value))] # 操作分つくる
    ###########################

    u_scale = 400


    participant_num = sum(not os.path.isfile(os.path.join(data_pass, name)) for name in os.listdir(data_pass))
    for participant in range(participant_num):
        participant = participant + 1
        print("----- p{} -----".format(participant))
        participant_dir = "{}/data{}".format(data_pass, participant)

        ############ 被験者の数だけウィンドウを作成 #########
        fig = plt.figure(figsize=(15, 9))
        plt.suptitle('Hand Y-Position (P{})'.format(participant))
        # 操作の数だけグラフを作成
        ax = [fig.add_subplot(330 + i + 1) for i in range(len(OperationEnum.OperationName_LIST_JP.value))]
        line = [[] for i in range(len(OperationEnum.OperationName_LIST_JP.value))]  # 操作分つくる
        #####################
        
        # section ごと
        section_num = sum(not os.path.isfile(os.path.join(participant_dir, name)) for name in os.listdir(participant_dir))
        for sec in range(section_num):
            print("     ----- sec {} -----".format(sec))

            sec_dir = "{}/sec_{}".format(participant_dir, sec)
            read_data = [pd.DataFrame(), pd.DataFrame()]

            time_df = pd.read_csv(sec_dir + '/timeData.csv', sep=',', index_col=0)
            time_df = time_df.reset_index(drop=True)
            time_df["operation"] = [OperationEnum.OperationGrid.value[int(p.action)][int(p.direction)] for i, p in time_df[["action", "direction"]].iterrows()]

            # 左右ごと
            for lr, lr_name in enumerate(lr_label):
                read_data[lr] = pd.read_csv(sec_dir + '/' + lr_name + 'Data.csv', sep=',', index_col=0)
                splited_data = read_data[lr].groupby('Label')
                # タスクごと
                for i in time_df["operation"].index:
                    op = int(time_df.at[i, "operation"])

                    try:
                        target_vec = splited_data.get_group(i)
                    except:
                        e_record = e_record + 1
                        continue

                    target_vec = target_vec.reset_index(drop=True)
                    s_row = 0

                    # 未使用の手をスキップ
                    while target_vec.loc[s_row, 'y'] > CALIBRATION_THRESHOLD:
                        s_row = s_row + 1
                    if target_vec['y'].values.max() - target_vec.loc[s_row, 'y'] < ACTION_THRESHOLD:
                        continue

                    try:
                        target_vec = filterData(target_vec)
                    except:
                        e_gestuer = e_gestuer + 1
                        # print("p{} sec{} {}Hand: task{} - {}   marker tracking failed".format(participant, sec, lr_name, i, OperationEnum.OperationName_LIST.value[op]))
                        continue

                    y_vec = target_vec['y'].values
                    # y_vec = fingerMoveNolm(target_vec)
                    x_vec = target_vec['timestamp'].values
                    x_vec = x_vec - x_vec[0]
                    e_time = x_vec.max()

                    if e_time < 1.5 and e_time > 0.3:
                        line[op].append(ax[op].plot(x_vec, y_vec, '-', alpha=0.8)[0])
                    else:
                        e_record = e_record + 1



        # update plot label/title
        for i in range(len(ax)):
            print("     {}: {}".format(OperationEnum.OperationName_LIST_JP.value[i], len(line[i])))
            ax[i].axhspan(0, ACTION_THRESHOLD, facecolor="blue", alpha=0.3)
            ax[i].set_title(OperationEnum.OperationName_LIST_JP.value[i])
            ax[i].set_ylim(ymax=u_scale, ymin=0)
            ax[i].set_xlim(xmax=1.4, xmin=0)
            ax[i].set_xlabel("時間 [s]")
            ax[i].set_ylabel("手のｙ座標 [mm]")
        fig.tight_layout()

        plt.savefig('{}/study1_p{}.png'.format(data_pass, participant))
    # end 被験者 ------------------------

    print("excepted data count: gesture- {}, record- {}".format(e_gestuer, e_record))
    plt.show()
    # use ggplot style for more sophisticated visuals
    # plt.style.use('ggplot')


def filterData(target_vec):
    target_vec = target_vec.reset_index(drop=True)
    s_row = 0
    # 最初を整える
    while target_vec.loc[s_row + 10, 'y'] - target_vec.loc[s_row, 'y'] < CALIBRATION_THRESHOLD or target_vec.loc[
        s_row, 'y'] > CALIBRATION_THRESHOLD:
        s_row = s_row + 1
    target_vec = target_vec[s_row:]
    # 最後を整える
    e_row = -1
    while target_vec.iloc[e_row]['timestamp'] - target_vec.iloc[e_row - 1]['timestamp'] > 0.01 or \
            target_vec.iloc[e_row]['y'] - target_vec.iloc[e_row - 20]['y'] < 20:
        e_row = e_row - 1
    target_vec = target_vec[:e_row]
    target_vec = target_vec.reset_index(drop=True)
    return target_vec


if __name__ == "__main__":
    main()
