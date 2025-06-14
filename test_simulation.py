"""Test the robot arm simulation independently"""

import sys
sys.path.append('.')

from easyjam.simulation.robot_arm import test_strumming_motion

if __name__ == "__main__":
    print("Testing robot arm strumming simulation...")
    print("Close the matplotlib window to exit.")
    robot, anim = test_strumming_motion()