import pickle

import pandas as pd

from lib.LeapMotion.Leap import RAD_TO_DEG


class Predictor():
    def __init__(self, alg: str):
        self.model = pickle.load(open('../../res/learningModel/HandDetectModel_{}_a0.pkl'.format(alg), 'rb'))
        self.finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        self.bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
        self.stateLabels = ["FREE", "PINCH_IN", "PINCH_OUT", "REVERSE_PINCH_OUT", "PALM", "GRIP"]
        self.df = self.create_emptypandas()
        self.dfs = self.create_emptypandas()

    def handPredict(self, hand):
        # handType = "Left hand" if hand.is_left else "Right hand"

        # print("  %s, id %d, position: %s" % (
        #     handType, hand.id, hand.palm_position))

        # Get the hand's normal vector and direction
        normal = hand.palm_normal
        direction = hand.direction

        pitch = direction.pitch * RAD_TO_DEG
        roll = normal.roll * RAD_TO_DEG
        yaw = direction.yaw * RAD_TO_DEG

        # Calculate the hand's pitch, roll, and yaw angles
        # print("  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
        #     pitch,
        #     roll,
        #     yaw))

        # Get arm bone
        arm = hand.arm
        # print("  Arm direction: %s, wrist position: %s, elbow position: %s" % (
        #     arm.direction,
        #     arm.wrist_position,
        #     arm.elbow_position))

        # Get fingers

        for finger in hand.fingers:
            # print("    %s finger, id: %d, length: %fmm, width: %fmm" % (
            #     self.finger_names[finger.type],
            #     finger.id,
            #     finger.length,
            #     finger.width))

            # Get bones
            for b in range(0, 4):
                bone = finger.bone(b)
                # print("      Bone: %s, start: %s, end: %s, direction: %s" % (
                #     self.bone_names[bone.type],
                #     bone.prev_joint,
                #     bone.next_joint,
                #     bone.direction))

                if self.finger_names[finger.type] == 'Thumb':
                    if self.bone_names[bone.type] == 'Metacarpal':
                        self.df.at[0, "Thumb_fin_meta_direction_x"] = bone.direction.x
                        self.df.at[0, "Thumb_fin_meta_direction_y"] = bone.direction.y
                        self.df.at[0, "Thumb_fin_meta_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Proximal':
                        self.df.at[0, "Thumb_fin_prox_direction_x"] = bone.direction.x
                        self.df.at[0, "Thumb_fin_prox_direction_y"] = bone.direction.y
                        self.df.at[0, "Thumb_fin_prox_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Intermediate':
                        self.df.at[0, "Thumb_fin_inter_direction_x"] = bone.direction.x
                        self.df.at[0, "Thumb_fin_inter_direction_y"] = bone.direction.y
                        self.df.at[0, "Thumb_fin_inter_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Distal':
                        self.df.at[0, "Thumb_fin_dist_direction_x"] = bone.direction.x
                        self.df.at[0, "Thumb_fin_dist_direction_y"] = bone.direction.y
                        self.df.at[0, "Thumb_fin_dist_direction_z"] = bone.direction.z
                if self.finger_names[finger.type] == 'Index':
                    if self.bone_names[bone.type] == 'Metacarpal':
                        self.df.at[0, "Index_fin_meta_direction_x"] = bone.direction.x
                        self.df.at[0, "Index_fin_meta_direction_y"] = bone.direction.y
                        self.df.at[0, "Index_fin_meta_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Proximal':
                        self.df.at[0, "Index_fin_prox_direction_x"] = bone.direction.x
                        self.df.at[0, "Index_fin_prox_direction_y"] = bone.direction.y
                        self.df.at[0, "Index_fin_prox_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Intermediate':
                        self.df.at[0, "Index_fin_inter_direction_x"] = bone.direction.x
                        self.df.at[0, "Index_fin_inter_direction_y"] = bone.direction.y
                        self.df.at[0, "Index_fin_inter_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Distal':
                        self.df.at[0, "Index_fin_dist_direction_x"] = bone.direction.x
                        self.df.at[0, "Index_fin_dist_direction_y"] = bone.direction.y
                        self.df.at[0, "Index_fin_dist_direction_z"] = bone.direction.z
                if self.finger_names[finger.type] == 'Middle':
                    if self.bone_names[bone.type] == 'Metacarpal':
                        self.df.at[0, "Middle_fin_meta_direction_x"] = bone.direction.x
                        self.df.at[0, "Middle_fin_meta_direction_y"] = bone.direction.y
                        self.df.at[0, "Middle_fin_meta_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Proximal':
                        self.df.at[0, "Middle_fin_prox_direction_x"] = bone.direction.x
                        self.df.at[0, "Middle_fin_prox_direction_y"] = bone.direction.y
                        self.df.at[0, "Middle_fin_prox_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Intermediate':
                        self.df.at[0, "Middle_fin_inter_direction_x"] = bone.direction.x
                        self.df.at[0, "Middle_fin_inter_direction_y"] = bone.direction.y
                        self.df.at[0, "Middle_fin_inter_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Distal':
                        self.df.at[0, "Middle_fin_dist_direction_x"] = bone.direction.x
                        self.df.at[0, "Middle_fin_dist_direction_y"] = bone.direction.y
                        self.df.at[0, "Middle_fin_dist_direction_z"] = bone.direction.z
                if self.finger_names[finger.type] == 'Ring':
                    if self.bone_names[bone.type] == 'Metacarpal':
                        self.df.at[0, "Ring_fin_meta_direction_x"] = bone.direction.x
                        self.df.at[0, "Ring_fin_meta_direction_y"] = bone.direction.y
                        self.df.at[0, "Ring_fin_meta_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Proximal':
                        self.df.at[0, "Ring_fin_prox_direction_x"] = bone.direction.x
                        self.df.at[0, "Ring_fin_prox_direction_y"] = bone.direction.y
                        self.df.at[0, "Ring_fin_prox_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Intermediate':
                        self.df.at[0, "Ring_fin_inter_direction_x"] = bone.direction.x
                        self.df.at[0, "Ring_fin_inter_direction_y"] = bone.direction.y
                        self.df.at[0, "Ring_fin_inter_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Distal':
                        self.df.at[0, "Ring_fin_dist_direction_x"] = bone.direction.x
                        self.df.at[0, "Ring_fin_dist_direction_y"] = bone.direction.y
                        self.df.at[0, "Ring_fin_dist_direction_z"] = bone.direction.z
                if self.finger_names[finger.type] == 'Pinky':
                    if self.bone_names[bone.type] == 'Metacarpal':
                        self.df.at[0, "Pinky_fin_meta_direction_x"] = bone.direction.x
                        self.df.at[0, "Pinky_fin_meta_direction_y"] = bone.direction.y
                        self.df.at[0, "Pinky_fin_meta_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Proximal':
                        self.df.at[0, "Pinky_fin_prox_direction_x"] = bone.direction.x
                        self.df.at[0, "Pinky_fin_prox_direction_y"] = bone.direction.y
                        self.df.at[0, "Pinky_fin_prox_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Intermediate':
                        self.df.at[0, "Pinky_fin_inter_direction_x"] = bone.direction.x
                        self.df.at[0, "Pinky_fin_inter_direction_y"] = bone.direction.y
                        self.df.at[0, "Pinky_fin_inter_direction_z"] = bone.direction.z
                    if self.bone_names[bone.type] == 'Distal':
                        self.df.at[0, "Pinky_fin_dist_direction_x"] = bone.direction.x
                        self.df.at[0, "Pinky_fin_dist_direction_y"] = bone.direction.y
                        self.df.at[0, "Pinky_fin_dist_direction_z"] = bone.direction.z

        # self.df.at[0, "hand_position_x"] = hand.palm_position.x
        # self.df.at[0, "hand_position_y"] = hand.palm_position.y
        # self.df.at[0, "hand_position_z"] = hand.palm_position.z
        # self.df.at[0, "pitch_list"] = pitch
        # self.df.at[0, "roll_list"] = roll
        # self.df.at[0, "yaw_list"] = yaw
        self.df.at[0, "arm_direction_x"] = arm.direction.x
        self.df.at[0, "arm_direction_y"] = arm.direction.y
        self.df.at[0, "arm_direction_z"] = arm.direction.z
        # self.df.at[0, "wrist_position_x"] = arm.wrist_position.x
        # self.df.at[0, "wrist_position_y"] = arm.wrist_position.y
        # self.df.at[0, "wrist_position_z"] = arm.wrist_position.z
        # self.df.at[0, "elbow_position_x"] = arm.elbow_position.x
        # self.df.at[0, "elbow_position_y"] = arm.elbow_position.y
        # self.df.at[0, "elbow_position_z"] = arm.elbow_position.z
        self.dfs = pd.concat([self.dfs, self.df], ignore_index=True)
        pred = self.model.predict(self.df.values)
        # print(self.model.decision_function(self.df.values))　# SVCのみ
        # print(pred)
        return pred[0]

    def create_emptypandas(self):
        return pd.DataFrame(index=[0], columns=[
            # "hand_position_x",
            # "hand_position_y",
            # "hand_position_z",
            # "pitch",
            # "roll",
            # "yaw",
            # "wrist_position_x",
            # "wrist_position_y",
            # "wrist_position_z",
            # "elbow_position_x",
            # "elbow_position_y",
            # "elbow_position_z",
            "arm_direction_x",
            "arm_direction_y",
            "arm_direction_z",
            "Thumb_fin_meta_direction_x",
            "Thumb_fin_meta_direction_y",
            "Thumb_fin_meta_direction_z",
            "Thumb_fin_prox_direction_x",
            "Thumb_fin_prox_direction_y",
            "Thumb_fin_prox_direction_z",
            "Thumb_fin_inter_direction_x",
            "Thumb_fin_inter_direction_y",
            "Thumb_fin_inter_direction_z",
            "Thumb_fin_dist_direction_x",
            "Thumb_fin_dist_direction_y",
            "Thumb_fin_dist_direction_z",
            "Index_fin_meta_direction_x",
            "Index_fin_meta_direction_y",
            "Index_fin_meta_direction_z",
            "Index_fin_prox_direction_x",
            "Index_fin_prox_direction_y",
            "Index_fin_prox_direction_z",
            "Index_fin_inter_direction_x",
            "Index_fin_inter_direction_y",
            "Index_fin_inter_direction_z",
            "Index_fin_dist_direction_x",
            "Index_fin_dist_direction_y",
            "Index_fin_dist_direction_z",
            "Middle_fin_meta_direction_x",
            "Middle_fin_meta_direction_y",
            "Middle_fin_meta_direction_z",
            "Middle_fin_prox_direction_x",
            "Middle_fin_prox_direction_y",
            "Middle_fin_prox_direction_z",
            "Middle_fin_inter_direction_x",
            "Middle_fin_inter_direction_y",
            "Middle_fin_inter_direction_z",
            "Middle_fin_dist_direction_x",
            "Middle_fin_dist_direction_y",
            "Middle_fin_dist_direction_z",
            "Ring_fin_meta_direction_x",
            "Ring_fin_meta_direction_y",
            "Ring_fin_meta_direction_z",
            "Ring_fin_prox_direction_x",
            "Ring_fin_prox_direction_y",
            "Ring_fin_prox_direction_z",
            "Ring_fin_inter_direction_x",
            "Ring_fin_inter_direction_y",
            "Ring_fin_inter_direction_z",
            "Ring_fin_dist_direction_x",
            "Ring_fin_dist_direction_y",
            "Ring_fin_dist_direction_z",
            "Pinky_fin_meta_direction_x",
            "Pinky_fin_meta_direction_y",
            "Pinky_fin_meta_direction_z",
            "Pinky_fin_prox_direction_x",
            "Pinky_fin_prox_direction_y",
            "Pinky_fin_prox_direction_z",
            "Pinky_fin_inter_direction_x",
            "Pinky_fin_inter_direction_y",
            "Pinky_fin_inter_direction_z",
            "Pinky_fin_dist_direction_x",
            "Pinky_fin_dist_direction_y",
            "Pinky_fin_dist_direction_z"
        ])