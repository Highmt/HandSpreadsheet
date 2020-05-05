################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

from lib.LeapMotion.Leap import *
import sys

import pandas as pd
from datetime import datetime

from res.SSEnum import HandEnum

current = datetime.now().strftime('%Y%m%d%H%M')
#　収集する手形状のラベル（）
label = HandEnum.PINCH_OUT.value
names = HandEnum.NAME_LIST.value
collect_data_num = 2000
data_count = 0

hand_position_x = []
hand_position_y = []
hand_position_z = []
pitch_list = []
roll_list = []
yaw_list = []
arm_direction_x = []
arm_direction_y = []
arm_direction_z = []
wrist_position_x = []
wrist_position_y = []
wrist_position_z = []
elbow_position_x = []
elbow_position_y = []
elbow_position_z = []

Thumb_fin_meta_direction_x = []
Thumb_fin_meta_direction_y = []
Thumb_fin_meta_direction_z = []
Thumb_fin_prox_direction_x = []
Thumb_fin_prox_direction_y = []
Thumb_fin_prox_direction_z = []
Thumb_fin_inter_direction_x = []
Thumb_fin_inter_direction_y = []
Thumb_fin_inter_direction_z = []
Thumb_fin_dist_direction_x = []
Thumb_fin_dist_direction_y = []
Thumb_fin_dist_direction_z = []

Index_fin_meta_direction_x = []
Index_fin_meta_direction_y = []
Index_fin_meta_direction_z = []
Index_fin_prox_direction_x = []
Index_fin_prox_direction_y = []
Index_fin_prox_direction_z = []
Index_fin_inter_direction_x = []
Index_fin_inter_direction_y = []
Index_fin_inter_direction_z = []
Index_fin_dist_direction_x = []
Index_fin_dist_direction_y = []
Index_fin_dist_direction_z = []

Middle_fin_meta_direction_x = []
Middle_fin_meta_direction_y = []
Middle_fin_meta_direction_z = []
Middle_fin_prox_direction_x = []
Middle_fin_prox_direction_y = []
Middle_fin_prox_direction_z = []
Middle_fin_inter_direction_x = []
Middle_fin_inter_direction_y = []
Middle_fin_inter_direction_z = []
Middle_fin_dist_direction_x = []
Middle_fin_dist_direction_y = []
Middle_fin_dist_direction_z = []

Ring_fin_meta_direction_x = []
Ring_fin_meta_direction_y = []
Ring_fin_meta_direction_z = []
Ring_fin_prox_direction_x = []
Ring_fin_prox_direction_y = []
Ring_fin_prox_direction_z = []
Ring_fin_inter_direction_x = []
Ring_fin_inter_direction_y = []
Ring_fin_inter_direction_z = []
Ring_fin_dist_direction_x = []
Ring_fin_dist_direction_y = []
Ring_fin_dist_direction_z = []

Pinky_fin_meta_direction_x = []
Pinky_fin_meta_direction_y = []
Pinky_fin_meta_direction_z = []
Pinky_fin_prox_direction_x = []
Pinky_fin_prox_direction_y = []
Pinky_fin_prox_direction_z = []
Pinky_fin_inter_direction_x = []
Pinky_fin_inter_direction_y = []
Pinky_fin_inter_direction_z = []
Pinky_fin_dist_direction_x = []
Pinky_fin_dist_direction_y = []
Pinky_fin_dist_direction_z = []

label_list = []

class CollectListener(Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']


    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        global data_count, collect_data_num
        # Get the most recent frame and report some basic information

        #　データ収集が完了すると終了
        if(data_count >= collect_data_num):
            controller.remove_listener(self)
            print("\n\n\n\n\n\nPush Enter to Finish")
            data_save_pandas()
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:
            data_count = data_count + 1
            print("Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
                frame.id, frame.timestamp, len(frame.hands), len(frame.fingers)))
            handType = "Left hand" if hand.is_left else "Right hand"

            print("  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position))

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            pitch = direction.pitch * RAD_TO_DEG
            roll = normal.roll * RAD_TO_DEG
            yaw = direction.yaw * RAD_TO_DEG

            # Calculate the hand's pitch, roll, and yaw angles
            print("  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                pitch,
                roll,
                yaw))

            # Get arm bone
            arm = hand.arm
            print("  Arm direction: %s, wrist position: %s, elbow position: %s" % (
                arm.direction,
                arm.wrist_position,
                arm.elbow_position))

            # Get fingers

            for finger in hand.fingers:

                print("    %s finger, id: %d, length: %fmm, width: %fmm" % (
                    self.finger_names[finger.type],
                    finger.id,
                    finger.length,
                    finger.width))

                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    print("      Bone: %s, start: %s, end: %s, direction: %s" % (
                        self.bone_names[bone.type],
                        bone.prev_joint,
                        bone.next_joint,
                        bone.direction))

                    if self.finger_names[finger.type] == 'Thumb':
                        if self.bone_names[bone.type] == 'Metacarpal':
                            Thumb_fin_meta_direction_x.append(bone.direction.x)
                            Thumb_fin_meta_direction_y.append(bone.direction.y)
                            Thumb_fin_meta_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Proximal':
                            Thumb_fin_prox_direction_x.append(bone.direction.x)
                            Thumb_fin_prox_direction_y.append(bone.direction.y)
                            Thumb_fin_prox_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Intermediate':
                            Thumb_fin_inter_direction_x.append(bone.direction.x)
                            Thumb_fin_inter_direction_y.append(bone.direction.y)
                            Thumb_fin_inter_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Distal':
                            Thumb_fin_dist_direction_x.append(bone.direction.x)
                            Thumb_fin_dist_direction_y.append(bone.direction.y)
                            Thumb_fin_dist_direction_z.append(bone.direction.z)
                    if self.finger_names[finger.type] == 'Index':
                        if self.bone_names[bone.type] == 'Metacarpal':
                            Index_fin_meta_direction_x.append(bone.direction.x)
                            Index_fin_meta_direction_y.append(bone.direction.y)
                            Index_fin_meta_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Proximal':
                            Index_fin_prox_direction_x.append(bone.direction.x)
                            Index_fin_prox_direction_y.append(bone.direction.y)
                            Index_fin_prox_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Intermediate':
                            Index_fin_inter_direction_x.append(bone.direction.x)
                            Index_fin_inter_direction_y.append(bone.direction.y)
                            Index_fin_inter_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Distal':
                            Index_fin_dist_direction_x.append(bone.direction.x)
                            Index_fin_dist_direction_y.append(bone.direction.y)
                            Index_fin_dist_direction_z.append(bone.direction.z)
                    if self.finger_names[finger.type] == 'Middle':
                        if self.bone_names[bone.type] == 'Metacarpal':
                            Middle_fin_meta_direction_x.append(bone.direction.x)
                            Middle_fin_meta_direction_y.append(bone.direction.y)
                            Middle_fin_meta_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Proximal':
                            Middle_fin_prox_direction_x.append(bone.direction.x)
                            Middle_fin_prox_direction_y.append(bone.direction.y)
                            Middle_fin_prox_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Intermediate':
                            Middle_fin_inter_direction_x.append(bone.direction.x)
                            Middle_fin_inter_direction_y.append(bone.direction.y)
                            Middle_fin_inter_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Distal':
                            Middle_fin_dist_direction_x.append(bone.direction.x)
                            Middle_fin_dist_direction_y.append(bone.direction.y)
                            Middle_fin_dist_direction_z.append(bone.direction.z)
                    if self.finger_names[finger.type] == 'Ring':
                        if self.bone_names[bone.type] == 'Metacarpal':
                            Ring_fin_meta_direction_x.append(bone.direction.x)
                            Ring_fin_meta_direction_y.append(bone.direction.y)
                            Ring_fin_meta_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Proximal':
                            Ring_fin_prox_direction_x.append(bone.direction.x)
                            Ring_fin_prox_direction_y.append(bone.direction.y)
                            Ring_fin_prox_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Intermediate':
                            Ring_fin_inter_direction_x.append(bone.direction.x)
                            Ring_fin_inter_direction_y.append(bone.direction.y)
                            Ring_fin_inter_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Distal':
                            Ring_fin_dist_direction_x.append(bone.direction.x)
                            Ring_fin_dist_direction_y.append(bone.direction.y)
                            Ring_fin_dist_direction_z.append(bone.direction.z)
                    if self.finger_names[finger.type] == 'Pinky':
                        if self.bone_names[bone.type] == 'Metacarpal':
                            Pinky_fin_meta_direction_x.append(bone.direction.x)
                            Pinky_fin_meta_direction_y.append(bone.direction.y)
                            Pinky_fin_meta_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Proximal':
                            Pinky_fin_prox_direction_x.append(bone.direction.x)
                            Pinky_fin_prox_direction_y.append(bone.direction.y)
                            Pinky_fin_prox_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Intermediate':
                            Pinky_fin_inter_direction_x.append(bone.direction.x)
                            Pinky_fin_inter_direction_y.append(bone.direction.y)
                            Pinky_fin_inter_direction_z.append(bone.direction.z)
                        if self.bone_names[bone.type] == 'Distal':
                            Pinky_fin_dist_direction_x.append(bone.direction.x)
                            Pinky_fin_dist_direction_y.append(bone.direction.y)
                            Pinky_fin_dist_direction_z.append(bone.direction.z)

            hand_position_x.append(hand.palm_position.x)
            hand_position_y.append(hand.palm_position.y)
            hand_position_z.append(hand.palm_position.z)
            pitch_list.append(pitch)
            roll_list.append(roll)
            yaw_list.append(yaw)
            arm_direction_x.append(arm.direction.x)
            arm_direction_y.append(arm.direction.y)
            arm_direction_z.append(arm.direction.z)
            wrist_position_x.append(arm.wrist_position.x)
            wrist_position_y.append(arm.wrist_position.y)
            wrist_position_z.append(arm.wrist_position.z)
            elbow_position_x.append(arm.elbow_position.x)
            elbow_position_y.append(arm.elbow_position.y)
            elbow_position_z.append(arm.elbow_position.z)
            label_list.append(label)


        # if frame.hands.is_empty:
        #     print("no hand")

def data_save_pandas():
    df = pd.DataFrame({
        #"hand_position_x" : hand_position_x,
        #"hand_position_y" : hand_position_y,
        #"hand_position_z" : hand_position_z,
        #"pitch" : pitch_list,
        #"roll" : roll_list,
        #"yaw" : yaw_list,
        #"wrist_position_x" : wrist_position_x,
        #"wrist_position_y" : wrist_position_y,
        #"wrist_position_z" : wrist_position_z,
        #"elbow_position_x" : elbow_position_x,
        #"elbow_position_y" : elbow_position_y,
        #"elbow_position_z" : elbow_position_z,
        "arm_direction_x" : arm_direction_x,
        "arm_direction_y" : arm_direction_y,
        "arm_direction_z" : arm_direction_z,
        "Thumb_fin_meta_direction_x" : Thumb_fin_meta_direction_x,
        "Thumb_fin_meta_direction_y" : Thumb_fin_meta_direction_y,
        "Thumb_fin_meta_direction_z" : Thumb_fin_meta_direction_z,
        "Thumb_fin_prox_direction_x" : Thumb_fin_prox_direction_x,
        "Thumb_fin_prox_direction_y" : Thumb_fin_prox_direction_y,
        "Thumb_fin_prox_direction_z" : Thumb_fin_prox_direction_z,
        "Thumb_fin_inter_direction_x" : Thumb_fin_inter_direction_x,
        "Thumb_fin_inter_direction_y" : Thumb_fin_inter_direction_y,
        "Thumb_fin_inter_direction_z" : Thumb_fin_inter_direction_z,
        "Thumb_fin_dist_direction_x" : Thumb_fin_dist_direction_x,
        "Thumb_fin_dist_direction_y" : Thumb_fin_dist_direction_y,
        "Thumb_fin_dist_direction_z" : Thumb_fin_dist_direction_z,
        "Index_fin_meta_direction_x" : Index_fin_meta_direction_x,
        "Index_fin_meta_direction_y" : Index_fin_meta_direction_y,
        "Index_fin_meta_direction_z" : Index_fin_meta_direction_z,
        "Index_fin_prox_direction_x" : Index_fin_prox_direction_x,
        "Index_fin_prox_direction_y" : Index_fin_prox_direction_y,
        "Index_fin_prox_direction_z" : Index_fin_prox_direction_z,
        "Index_fin_inter_direction_x" : Index_fin_inter_direction_x,
        "Index_fin_inter_direction_y" : Index_fin_inter_direction_y,
        "Index_fin_inter_direction_z" : Index_fin_inter_direction_z,
        "Index_fin_dist_direction_x" : Index_fin_dist_direction_x,
        "Index_fin_dist_direction_y" : Index_fin_dist_direction_y,
        "Index_fin_dist_direction_z" : Index_fin_dist_direction_z,
        "Middle_fin_meta_direction_x" : Middle_fin_meta_direction_x,
        "Middle_fin_meta_direction_y" : Middle_fin_meta_direction_y,
        "Middle_fin_meta_direction_z" : Middle_fin_meta_direction_z,
        "Middle_fin_prox_direction_x" : Middle_fin_prox_direction_x,
        "Middle_fin_prox_direction_y" : Middle_fin_prox_direction_y,
        "Middle_fin_prox_direction_z" : Middle_fin_prox_direction_z,
        "Middle_fin_inter_direction_x" : Middle_fin_inter_direction_x,
        "Middle_fin_inter_direction_y" : Middle_fin_inter_direction_y,
        "Middle_fin_inter_direction_z" : Middle_fin_inter_direction_z,
        "Middle_fin_dist_direction_x" : Middle_fin_dist_direction_x,
        "Middle_fin_dist_direction_y" : Middle_fin_dist_direction_y,
        "Middle_fin_dist_direction_z" : Middle_fin_dist_direction_z,
        "Ring_fin_meta_direction_x" : Ring_fin_meta_direction_x,
        "Ring_fin_meta_direction_y" : Ring_fin_meta_direction_y,
        "Ring_fin_meta_direction_z" : Ring_fin_meta_direction_z,
        "Ring_fin_prox_direction_x" : Ring_fin_prox_direction_x,
        "Ring_fin_prox_direction_y" : Ring_fin_prox_direction_y,
        "Ring_fin_prox_direction_z" : Ring_fin_prox_direction_z,
        "Ring_fin_inter_direction_x" : Ring_fin_inter_direction_x,
        "Ring_fin_inter_direction_y" : Ring_fin_inter_direction_y,
        "Ring_fin_inter_direction_z" : Ring_fin_inter_direction_z,
        "Ring_fin_dist_direction_x" : Ring_fin_dist_direction_x,
        "Ring_fin_dist_direction_y" : Ring_fin_dist_direction_y,
        "Ring_fin_dist_direction_z" : Ring_fin_dist_direction_z,
        "Pinky_fin_meta_direction_x" : Pinky_fin_meta_direction_x,
        "Pinky_fin_meta_direction_y" : Pinky_fin_meta_direction_y,
        "Pinky_fin_meta_direction_z" : Pinky_fin_meta_direction_z,
        "Pinky_fin_prox_direction_x" : Pinky_fin_prox_direction_x,
        "Pinky_fin_prox_direction_y" : Pinky_fin_prox_direction_y,
        "Pinky_fin_prox_direction_z" : Pinky_fin_prox_direction_z,
        "Pinky_fin_inter_direction_x" : Pinky_fin_inter_direction_x,
        "Pinky_fin_inter_direction_y" : Pinky_fin_inter_direction_y,
        "Pinky_fin_inter_direction_z" : Pinky_fin_inter_direction_z,
        "Pinky_fin_dist_direction_x" : Pinky_fin_dist_direction_x,
        "Pinky_fin_dist_direction_y" : Pinky_fin_dist_direction_y,
        "Pinky_fin_dist_direction_z" : Pinky_fin_dist_direction_z,
        "label" : label_list,
    })
    df.to_csv("../../res/data/{0}_{1}.csv".format(label, names.pop(label)))

def main():
    # Create a sample listener and controller
    listener = CollectListener()
    controller = Controller()

    # Have the sample listener receive events from the controller
    print("Press Enter to start collecting hand data")
    print("Press Enter again to quit...")
    sys.stdin.readline()
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed

    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()