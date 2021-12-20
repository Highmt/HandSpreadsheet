import pickle

import pandas as pd

from lib.LeapMotion.Leap import RAD_TO_DEG
from res.SSEnum import FeatureEnum
from src.HandScensing.HandListener import HandData

model_pass = '../../res/learningModel/'
ver = ''


pos_labels = ["x", "y", "z"]
rot_labels = ["pitch", "roll", "yaw"]
state_labels = ["FREE", "PINCH_IN", "PINCH_OUT", "REVERSE_PINCH_OUT", "OPEN", "GRIP"]
finger_labels = ['Thumb', 'Index', 'Pinky']

class Predictor():
    def __init__(self, alg: str):
        self.left_model = pickle.load(open('{}leftModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))
        self.right_model = pickle.load(open('{}rightModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))

    def handPredict(self, hand):
        df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
        ps = pd.Series(index=FeatureEnum.FEATURE_LIST.value)
        ps["position_x", "position_y", "position_z"] = hand.position
        ps["pitch", "roll", "yaw"] = hand.rotation[0:3]
        # Calculate the hand's pitch, roll, and yaw angles

        # Get fingers
        for finger_id in range(len(hand.fingers_pos)):
            for pos in range(3):
                ps[finger_labels[finger_id] + "_pos_" + pos_labels[pos]] = hand.fingers_pos[finger_id][pos]
                ps[finger_labels[finger_id] + "_dir_" + pos_labels[pos]] = hand.fingers_pos[finger_id][pos] - hand.position[pos]

        df = df.append(ps, ignore_index=True)
        df = df.drop(columns="Label")
        if hand.is_left:
            pred = self.left_model.predict(df.values)
        else:
            pred = self.right_model.predict(ps.values)
        # print(self.model.decision_function(self.df.values))　# SVCのみ
        # print(pred)
        return pred[0]