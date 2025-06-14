#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha
import numpy as np

# Create environment
env = gym.make('gym_aloha/AlohaTransferCube-v0')
env.reset()

print("ALOHA Robot Analysis")
print("=" * 50)

# Action space analysis
print(f"\nAction Space: {env.action_space}")
print(f"Action dimension: {env.action_space.shape[0]}")
print(f"Action range: [{env.action_space.low[0]}, {env.action_space.high[0]}]")

# The ALOHA has 14 DOF (degrees of freedom)
# Typically: 7 DOF per arm (2 arms = 14 total)
print("\nRobot Configuration (14 DOF):")
print("Left Arm (7 DOF):")
print("  - Shoulder Pan (joint 0)")
print("  - Shoulder Lift (joint 1)")
print("  - Elbow (joint 2)")
print("  - Wrist 1 (joint 3)")
print("  - Wrist 2 (joint 4)")
print("  - Wrist 3 (joint 5)")
print("  - Gripper (joint 6)")
print("\nRight Arm (7 DOF):")
print("  - Shoulder Pan (joint 7)")
print("  - Shoulder Lift (joint 8)")
print("  - Elbow (joint 9)")
print("  - Wrist 1 (joint 10)")
print("  - Wrist 2 (joint 11)")
print("  - Wrist 3 (joint 12)")
print("  - Gripper (joint 13)")

env.close()