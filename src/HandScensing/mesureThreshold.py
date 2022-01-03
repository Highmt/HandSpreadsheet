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

def live_plotter(y_data, line, pause_time=0.01):
    # after the figure, axis, and line are created, we only need to update the y-data
    line['x'].set_ydata(y_data['x'])
    line['y'].set_ydata(y_data['y'])
    line['z'].set_ydata(y_data['z'])
    line['d'].set_ydata(y_data['d'])
    # adjust limits if new data goes beyond bounds
    plt.draw()
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line


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

y_vec = [{'x': np.random.randn(len(x_vec)),
          'y': np.random.randn(len(x_vec)),
          'z': np.random.randn(len(x_vec)),
          'd': np.random.randn(len(x_vec))},
         {'x': np.random.randn(len(x_vec)),
          'y': np.random.randn(len(x_vec)),
          'z': np.random.randn(len(x_vec)),
          'd': np.random.randn(len(x_vec))}]
line = [{'x': [], 'y': [], 'z': [], 'd': []},
        {'x': [], 'y': [], 'z': [], 'd': []}]

plt.ion()
fig = plt.figure(figsize=(10, 8))
ax = [fig.add_subplot(211), fig.add_subplot(212)]
y_scale = 500
# create a variable for the line so we can later update it
for lr in range(2):
    line[lr]['x'], = ax[lr].plot(x_vec, y_vec[lr]['x'], '-', alpha=0.8)
    line[lr]['y'], = ax[lr].plot(x_vec, y_vec[lr]['y'], '-', alpha=0.8)
    line[lr]['z'], = ax[lr].plot(x_vec, y_vec[lr]['z'], '-', alpha=0.8)
    line[lr]['d'], = ax[lr].plot(x_vec, y_vec[lr]['d'], '-', alpha=0.8)

    ax[lr].set_ylim(ymax=y_scale, ymin=-1*y_scale)
    ax[lr].legend(["x", "y", "z", "d"])
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
            # TODO: 指の動きの絶対値のグラフも同時出力＋データ格納
            for key, hand in listener.hands_dict.items():
                lr = 0 if hand.is_left else 1
                y_vec[lr]['x'][-1] = hand.position[0]
                y_vec[lr]['y'][-1] = hand.position[1]
                y_vec[lr]['z'][-1] = hand.position[2]
                y_vec[lr]['d'][-1] = d[key]
                line[lr] = live_plotter(y_data=y_vec[lr], line=line[lr])
                y_vec[lr]['x'] = np.append(y_vec[lr]['x'][1:], 0.0)
                y_vec[lr]['y'] = np.append(y_vec[lr]['y'][1:], 0.0)
                y_vec[lr]['z'] = np.append(y_vec[lr]['z'][1:], 0.0)
                y_vec[lr]['d'] = np.append(y_vec[lr]['d'][1:], 0.0)
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
