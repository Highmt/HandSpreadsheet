import pickle

import pandas as pd

from lib.LeapMotion.Leap import RAD_TO_DEG
from res.SSEnum import FeatureEnum
from src.HandScensing.HandListener import HandData

model_pass = '../../res/learningModel/'
ver = 'a0'
class Predictor():
    def __init__(self, alg: str):
        self.left_model = pickle.load(open('{}LeftModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))
        self.right_model = pickle.load(open('{}RightModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))
        self.finger_labels = ['Thumb', 'Index', 'Pinky']
        self.state_labels = ["FREE", "PINCH_IN", "PINCH_OUT", "REVERSE_PINCH_OUT", "PALM", "GRIP"]
        self.pos_labels = ["x", "y", "z"]
        self.rot_labels = ["pitch", "roll", "yaw"]
        self.df = self.create_emptypandas()
        self.dfs = self.create_emptypandas()

    def handPredict(self, hand):

        for finger_id in len(hand.fingers_pos):
            for pos in range(3):
                self.df.at[0, self.finger_labels[finger_id] + "_pos_" + self.pos_labels[pos]] = hand.fingers_pos[pos]
                self.df.at[0, self.finger_labels[finger_id] + "dir" + self.pos_labels[pos]] = hand.fingers_pos[pos] - hand.position[pos]

        for pos in range(3):
            self.df.at[0, self.pos_labels[pos]] = hand.position[pos]
            self.df.at[0, self.rot_labels[pos]] = hand.rotation[pos]


        self.dfs = pd.concat([self.dfs, self.df], ignore_index=True)

        if hand.is_left:
            pred = self.left_model.predict(self.df.values)
        else:
            pred = self.right_model.predict(self.df.values)
        # print(self.model.decision_function(self.df.values))　# SVCのみ
        # print(pred)
        return pred[0]

    def create_emptypandas(self):
        return pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)