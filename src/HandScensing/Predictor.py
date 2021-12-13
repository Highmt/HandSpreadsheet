import pickle

import pandas as pd

from lib.LeapMotion.Leap import RAD_TO_DEG
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

    def handPredict(self, hand: HandData, isLeft: bool):

        for finger_id in len(hand.fingers_pos):
                if finger_id == 0:
                    for i in range(3):
                        self.df.at[0, self.finger_labels[finger_id] + "_pos_" + self.pos_labels[i]] = hand.fingers_pos[i]
                        self.df.at[0, self.finger_labels[finger_id] + "dir" + self.pos_labels[i]] = hand.fingers_pos[i] - hand.position[i]

        for i in range(3):
            self.df.at[0, self.pos_labels[i]] = hand.position[i]
            self.df.at[0, self.rot_labels[i]] = hand.rotation[i]


        self.dfs = pd.concat([self.dfs, self.df], ignore_index=True)

        if isLeft:
            pred = self.left_model.predict(self.df.values)
        else:
            pred = self.right_model.predict(self.df.values)
        # print(self.model.decision_function(self.df.values))　# SVCのみ
        # print(pred)
        return pred[0]

    def create_emptypandas(self):
        return pd.DataFrame(index=[0], columns=[
            "position_x",
            "position_y",
            "position_z",
            "pitch",
            "roll",
            "yaw",
            "Thumb_pos_x",
            "Thumb_pos_y",
            "Thumb_pos_z",
            "Index_pos_x",
            "Index_pos_y",
            "Index_pos_z",
            "Pinky_pos_x",
            "Pinky_pos_y",
            "Pinky_pos_z",
            "Thumb_dir_x",
            "Thumb_dir_y",
            "Thumb_dir_z",
            "Index_dir_x",
            "Index_dir_y",
            "Index_dir_z",
            "Pinky_dir_x",
            "Pinky_dir_y",
            "Pinky_dir_z",
        ])