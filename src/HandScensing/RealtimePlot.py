################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import copy
import sys
import time

import numpy as np
import pandas as pd
from datetime import datetime

from matplotlib import pyplot as plt

from src.HandScensing.HandListener import HandListener
from src.UDP.MoCapData import MoCapData
from src.UDP.NatNetClient import NatNetClient

version = "master"
#　収集する手形状のラベル（）
streaming_client = NatNetClient()
collect_data_num = 2000
finger_labels = ['Thumb', 'Index', 'Pinky']
pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]

def live_plotter(x_vec, y1_data, line1, identifier='', pause_time=0.001):
    # after the figure, axis, and line are created, we only need to update the y-data
    line1['x'].set_ydata(y1_data['x'])
    line1['y'].set_ydata(y1_data['y'])
    line1['z'].set_ydata(y1_data['z'])
    # adjust limits if new data goes beyond bounds
    plt.draw()
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line1

x_vec = np.linspace(0, 1, 100 + 1)[0:-1]
y_vec = {
    'x': np.random.randn(len(x_vec)),
    'y': np.random.randn(len(x_vec)),
    'z': np.random.randn(len(x_vec))
}
line1 = {'x': [], 'y': [], 'z': []}

plt.ion()
fig = plt.figure(figsize=(13, 6))
ax = fig.add_subplot(111)
# create a variable for the line so we can later update it
line1['x'], = ax.plot(x_vec, y_vec['x'], '-', alpha=0.8)
line1['y'], = ax.plot(x_vec, y_vec['y'], '-o', alpha=0.8)
line1['z'], = ax.plot(x_vec, y_vec['z'], '--', alpha=0.8)
plt.ylim([-3000, 3000])
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
try:
    while True:
        mocap_data = listener.getCurrentData()
        if listener.judgeDataComplete(mocap_data=mocap_data):
            listener.setHandData(mocap_data=mocap_data)
            for hand in listener.hands_dict.values():
                y_vec['x'][-1] = hand.position[0]
                y_vec['y'][-1] = hand.position[1]
                y_vec['z'][-1] = hand.position[2]
                line1 = live_plotter(x_vec, y_vec, line1)
                y_vec['x'] = np.append(y_vec['x'][1:], 0.0)
                y_vec['y'] = np.append(y_vec['y'][1:], 0.0)
                y_vec['z'] = np.append(y_vec['z'][1:], 0.0)
            time.sleep(0.05)
except KeyboardInterrupt:
    print("\n\nexit...")
    sys.exit()
finally:
    listener.streaming_client.shutdown()

