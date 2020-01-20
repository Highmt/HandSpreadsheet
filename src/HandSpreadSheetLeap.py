import sys
import pyautogui

from src.LeapMotion.Leap import *

DIS_SIZE = pyautogui.size()


class handListener(Listener):
    def __init__(self, app):
        super(handListener, self).__init__()
        self.finger_dis_dim = {"up": 0, "low": 0, "left": 0, "right": 0}
        self.finger_dis_size = [0, 0]
        self.app = app
        self.overlayGraphics = self.app.getOverlayGrahics()
        self.isPointingMode = False


    def on_caribration(self, controller):
        print("Do caribration")
        print("Point upper-left on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ul = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ul)

        print("Point lower-left on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ll = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ll)

        print("Point upper-right on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_lr = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_lr)

        print("Point lower-right on display")
        sys.stdin.readline()
        frame = controller.frame()
        fingers = frame.fingers
        while fingers.is_empty:
            print("Non fingers so tyr again")
            sys.stdin.readline()
            frame = controller.frame()
            fingers = frame.fingers
        f_finger = fingers.frontmost
        dis_ur = f_finger.joint_position(f_finger.JOINT_TIP)
        print(dis_ur)

        # 四隅の値の平均を上下左右の値とする
        self.finger_dis_dim["up"] = (dis_ul.y + dis_ur.y) / 2
        self.finger_dis_dim["low"] = (dis_ll.y + dis_lr.y) / 2
        self.finger_dis_dim["left"] = (dis_ul.x + dis_ll.x) / 2
        self.finger_dis_dim["right"] = (dis_ur.x + dis_lr.x) / 2
        self.finger_dis_size[0] = self.finger_dis_dim["right"] - self.finger_dis_dim["left"]
        self.finger_dis_size[1] = self.finger_dis_dim["low"] - self.finger_dis_dim["up"]
        print(self.finger_dis_size)

        print("\nComplete caribration")
        sys.stdin.readline()


    def on_caribrationTest(self,controller):
        dis_ul = Vector(-120, 215, 0)
        dis_ll = Vector(-130, 90, 0)
        dis_lr = Vector(130, 90, 0)
        dis_ur = Vector(120, 215, 0)

        self.finger_dis_dim["up"] = (dis_ul.y + dis_ur.y) / 2
        self.finger_dis_dim["low"] = (dis_ll.y + dis_lr.y) / 2
        self.finger_dis_dim["left"] = (dis_ul.x + dis_ll.x) / 2
        self.finger_dis_dim["right"] = (dis_ur.x + dis_lr.x) / 2
        self.finger_dis_size[0] = self.finger_dis_dim["right"] - self.finger_dis_dim["left"]
        self.finger_dis_size[1] = self.finger_dis_dim["low"] - self.finger_dis_dim["up"]
        print(self.finger_dis_size)
        print("Complete test caribration")



    def on_init(self, controller):
        print("Initialized")


    def on_connect(self, controller):
        print("Connected")
        self.on_caribrationTest(controller)
        self.setPointingMode(False)
        self.app.changeLeap(True)

    def on_disconnect(self, controller):
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")
        self.app.changeLeap(False)

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        hands = frame.hands



        if not hands.is_empty:
            fingers = hands[0].fingers
            # palm  open
            if(hands[0].grab_strength == 0) :
                  print("open")

            if not fingers.is_empty:

                if(hands[0].pinch_strength == 1):
                    print("pinch")


            self.mouse_move(self, fingers)


            #ウインドウ内でターゲットマーカーを動かす
    def mouse_move(self,fingers):
        print("display size: ", self.finger_dis_size)
        f_finger = fingers.frontmost
        finger_pos = f_finger.joint_position(f_finger.JOINT_TIP)
        print("finger_pos: ", finger_pos)

        move_pos = [
            (finger_pos.x - self.finger_dis_dim["left"]) / self.finger_dis_size[0] * DIS_SIZE[0],
            (finger_pos.y - self.finger_dis_dim["up"]) / self.finger_dis_size[1] * DIS_SIZE[1]]

        # マウス動かす
        pyautogui.moveTo(move_pos[0], move_pos[1])

        # print("Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d" % ( frame.id, frame.timestamp, numHands, len(frame.fingers), len(frame.tools)))

        # if numHands >= 1:
        #     # Get the first hand
        #     hand = hands[0]
        #
        #     # Check if the hand has any fingers
        #     fingers = hand.fingers
        #     numFingers = len(fingers)
        #     if numFingers >= 1:
        #         # Calculate the hand's average finger tip position
        #         pos = Vector()
        #         for finger in fingers:
        #             pos += finger.tip_position
        #
        #         pos = pos.__div__(numFingers)
        #         print("Hand has", numFingers, "fingers with average tip position", pos)
        #
        #     # Get the palm position
        #     palm = hand.palm_position
        #     print("Palm position:", palm)
        #
        #     # Get the palm normal vector  and direction
        #     normal = hand.palm_normal
        #     direction = hand.direction
        #
        #     # Calculate the hand's pitch, roll, and yaw angles
        #     print("Pitch: %f degrees,  Roll: %f degrees,  Yaw: %f degrees" % (
        #         direction.pitch * RAD_TO_DEG,
        #         normal.roll * RAD_TO_DEG,
        #         direction.yaw * RAD_TO_DEG))
        #
        #     print("Hand curvature radius: %f mm" % hand.sphere_radius)

    def setPointingMode(self, isMode):
        self.isPointingMode = isMode

    def singleJesture(self):
        # TODO 片手ジェスチャ認識
        pass

    def bothJesture(self):
        # TODO 両手ジェスチャ認識
        pass

def main():
    # Create a sample listener and controller
    listener = handListener()
    controller = Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print("Press Enter to quit...")
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
