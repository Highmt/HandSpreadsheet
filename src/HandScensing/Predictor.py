import pickle
import pandas as pd
from res.SSEnum import FeatureEnum
from src.HandScensing.HandListener import HandData

model_pass = '../../res/learningModel/'

pos_labels = ["x", "y", "z"]
finger_labels = ['Thumb', 'Index', 'Pinky']

class Predictor():
    def __init__(self, alg: str, ver: str):
        self.left_model = pickle.load(open('{}leftModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))
        self.right_model = pickle.load(open('{}rightModel_{}_{}.pkl'.format(model_pass, alg, ver), 'rb'))

    def handPredict(self, hand: HandData):
        df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
        ps = pd.Series(dtype=pd.Float64Dtype, index=FeatureEnum.FEATURE_LIST.value)
        ps["pitch", "roll", "yaw"] = hand.rotation[0:3]

        # Get fingers
        for finger_id in range(len(hand.fingers_pos)):
            for pos in range(3):
                ps[finger_labels[finger_id] + "_dir_" + pos_labels[pos]] = hand.getFingerVec(finger_type=finger_id)[0]
                ps[finger_labels[finger_id] + "_" + finger_labels[(finger_id + 1) % 3] + "_" + pos_labels[pos]] = hand.fingers_pos[finger_id][pos] - hand.fingers_pos[(finger_id + 1) % 3][pos]

        df = df.append(ps, ignore_index=True)
        df = df.drop(columns="Label")
        if hand.is_left:
            pred = self.left_model.predict(df.values)
        else:
            pred = self.right_model.predict(df.values)
        return pred[0]