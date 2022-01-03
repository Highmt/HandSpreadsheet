import copy
import sys
import time

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt

from src.HandScensing.HandListener import HandListener, HandData
from src.UDP.MoCapData import MoCapData
from src.UDP.NatNetClient import NatNetClient

version = "master"
# 　収集する手形状のラベル（）
streaming_client = NatNetClient()
collect_data_num = 2000
finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]
Y_THRESHOLD = 20

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


def fingerDifferencial(former_hands, hands_dict):
    a = {}
    for key in former_hands.keys():
        d = []
        for i in range(len(HandData().fingers_pos)):
            d.append(np.linalg.norm(former_hands[key].getFingerVec(i) - hands_dict[key].getFingerVec(i)))
        a[key] = sum(d) / len(d)  # とりあえず平均値を返している
        print(a[key])
    return a


x_vec = np.linspace(0, 1, 100 + 1)[0:-1]

y_vec = [[], []]
line = [[], []]

plt.ion()
fig = plt.figure(figsize=(10, 8))
ax = [fig.add_subplot(211), fig.add_subplot(212)]
y_scale = 500
# create a variable for the line so we can later update it
legend = ["x", "y", "z", "d"]
for lr in range(2):
    for axis in range(len(legend)):
        y_vec[lr].append(np.random.randn(len(x_vec)))
        line[lr].append(ax[lr].plot(x_vec, y_vec[lr][axis], '-', alpha=0.8)[0])

    ax[lr].set_ylim(ymax=y_scale, ymin=-1*y_scale)
    ax[lr].legend(legend)
# update plot label/title
plt.ylabel('Y Label')
plt.title('Title: {}'.format('Realtime'))
plt.show()
# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

listener = HandListener()
listener.initOptiTrack()
listener.do_calibration()
listener.streaming_client.stop()

# Have the sample listener receive events from the controller
print("Press Enter to start plot hand position session")
sys.stdin.readline()
listener.streaming_client.restart()

mocap_data: MoCapData = listener.getCurrentData()
if listener.judgeDataComplete(mocap_data=mocap_data):
    # if listener.need_calibration:
    #     listener.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
    listener.setHandData(mocap_data=mocap_data)
former_hands = copy.deepcopy(listener.hands_dict)

dif_memory_num = 3
dif_memory = [np.zeros(dif_memory_num), np.zeros(dif_memory_num)]
try:
    while True:
        mocap_data: MoCapData = listener.getCurrentData()
        if listener.judgeDataComplete(mocap_data=mocap_data):
            # if listener.need_calibration:
            #     listener.calibrateUnlabeledMarkerID(mocap_data=mocap_data)
            listener.setHandData(mocap_data=mocap_data)

            # 両手が閾値以下の位置にある時ラベルの再設定処理を回す
            if listener.hands_dict['l'].position[1] <= Y_THRESHOLD and listener.hands_dict['r'].position[1] <= Y_THRESHOLD:
                listener.calibrateUnlabeledMarkerID(mocap_data=mocap_data)

            d = fingerDifferencial(former_hands, listener.hands_dict)
            # TODO: データ格納
            for key, hand in listener.hands_dict.items():
                lr = 0 if hand.is_left else 1
                dif_memory[lr] = np.delete(np.append(dif_memory[lr], d[key]), 0)
                for axis in range(3):
                    y_vec[lr][axis][-1] = hand.position[axis]
                y_vec[lr][3][-1] = sum(dif_memory[lr])
                line[lr] = live_plotter(y_data=y_vec[lr], lines=line[lr])
                for axis in range(len(y_vec[lr])):
                    y_vec[lr][axis] = np.append(y_vec[lr][axis][1:], 0.0)
            former_hands = copy.deepcopy(listener.hands_dict)
            time.sleep(0.01)
        else:
            # # print(".")
            time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\nexit...")
    sys.exit()
finally:
    listener.streaming_client.shutdown()
