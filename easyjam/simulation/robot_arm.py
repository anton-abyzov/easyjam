"""Simple robot arm simulation for guitar strumming"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches


@dataclass
class RobotConfig:
    """Configuration for the simulated robot arm"""
    n_joints: int = 6
    link_lengths: List[float] = None
    joint_limits: List[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.link_lengths is None:
            # Default link lengths similar to SO101
            self.link_lengths = [0.1, 0.15, 0.15, 0.1, 0.05, 0.05]
        
        if self.joint_limits is None:
            # Default joint limits in radians
            self.joint_limits = [
                (-np.pi, np.pi),      # shoulder_pan
                (-np.pi/2, np.pi/2),  # shoulder_lift
                (-np.pi/2, np.pi/2),  # elbow_flex
                (-np.pi, np.pi),      # wrist_roll
                (-np.pi/2, np.pi/2),  # wrist_flex
                (0, np.pi/2),         # gripper
            ]


class RobotArmSimulator:
    """Simple 2D robot arm simulator for guitar strumming"""
    
    def __init__(self, config: RobotConfig = None):
        self.config = config or RobotConfig()
        self.joint_angles = np.zeros(self.config.n_joints)
        self.target_angles = np.zeros(self.config.n_joints)
        self.velocity = np.zeros(self.config.n_joints)
        
        # Guitar position relative to robot base
        self.guitar_position = np.array([0.3, 0.0])
        self.guitar_width = 0.1
        self.guitar_height = 0.3
        
        # Strumming parameters
        self.strum_height = 0.15  # Height above guitar
        self.strum_depth = 0.05   # How deep to strum
        
    def forward_kinematics(self, angles=None):
        """Calculate end effector position given joint angles"""
        if angles is None:
            angles = self.joint_angles
            
        positions = [np.array([0, 0])]  # Base position
        
        # Simplified 2D forward kinematics
        cumulative_angle = 0
        for i in range(min(3, len(angles))):  # Use first 3 joints for 2D
            cumulative_angle += angles[i]
            dx = self.config.link_lengths[i] * np.cos(cumulative_angle)
            dy = self.config.link_lengths[i] * np.sin(cumulative_angle)
            new_pos = positions[-1] + np.array([dx, dy])
            positions.append(new_pos)
            
        return np.array(positions)
    
    def inverse_kinematics_2d(self, target_pos):
        """Simple 2-link IK for strumming motion"""
        # Use only first 2 links for simple 2D IK
        l1 = self.config.link_lengths[0]
        l2 = self.config.link_lengths[1]
        
        x, y = target_pos
        
        # Check if target is reachable
        dist = np.sqrt(x**2 + y**2)
        if dist > l1 + l2:
            # Scale down to reachable position
            scale = (l1 + l2) * 0.99 / dist
            x *= scale
            y *= scale
            dist = np.sqrt(x**2 + y**2)
        
        # Calculate angles using law of cosines
        cos_angle2 = (dist**2 - l1**2 - l2**2) / (2 * l1 * l2)
        cos_angle2 = np.clip(cos_angle2, -1, 1)
        
        angle2 = np.arccos(cos_angle2)
        angle1 = np.arctan2(y, x) - np.arctan2(l2 * np.sin(angle2), 
                                                l1 + l2 * np.cos(angle2))
        
        return np.array([angle1, angle2, 0, 0, 0, 0])
    
    def generate_strum_trajectory(self, strum_type='down', speed=1.0):
        """Generate trajectory for strumming motion"""
        trajectory = []
        
        # Starting position above guitar
        start_x = self.guitar_position[0]
        start_y = self.guitar_position[1] + self.strum_height
        
        # End position below guitar
        end_x = self.guitar_position[0]
        end_y = self.guitar_position[1] - self.strum_depth
        
        # Generate smooth trajectory
        n_points = int(20 / speed)
        
        if strum_type == 'down':
            for i in range(n_points):
                t = i / (n_points - 1)
                # Smooth acceleration/deceleration
                s = 0.5 - 0.5 * np.cos(np.pi * t)
                y = start_y + (end_y - start_y) * s
                trajectory.append([start_x, y])
                
        elif strum_type == 'up':
            for i in range(n_points):
                t = i / (n_points - 1)
                s = 0.5 - 0.5 * np.cos(np.pi * t)
                y = end_y + (start_y - end_y) * s
                trajectory.append([start_x, y])
                
        return trajectory
    
    def update(self, dt=0.01):
        """Update robot state"""
        # Simple PD control
        kp = 5.0
        kd = 0.5
        
        error = self.target_angles - self.joint_angles
        self.velocity = kp * error - kd * self.velocity
        self.joint_angles += self.velocity * dt
        
        # Apply joint limits
        for i in range(self.config.n_joints):
            self.joint_angles[i] = np.clip(
                self.joint_angles[i],
                self.config.joint_limits[i][0],
                self.config.joint_limits[i][1]
            )
    
    def visualize(self, ax=None):
        """Visualize the robot arm and guitar"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        ax.clear()
        
        # Draw guitar
        guitar_rect = patches.Rectangle(
            (self.guitar_position[0] - self.guitar_width/2, 
             self.guitar_position[1] - self.guitar_height/2),
            self.guitar_width, self.guitar_height,
            linewidth=2, edgecolor='brown', facecolor='tan'
        )
        ax.add_patch(guitar_rect)
        
        # Draw guitar strings
        n_strings = 6
        for i in range(n_strings):
            y = self.guitar_position[1] - self.guitar_height/2 + \
                (i + 0.5) * self.guitar_height / n_strings
            ax.plot([self.guitar_position[0] - self.guitar_width/2,
                    self.guitar_position[0] + self.guitar_width/2],
                   [y, y], 'k-', linewidth=1)
        
        # Draw robot arm
        positions = self.forward_kinematics()
        
        # Draw links
        for i in range(len(positions) - 1):
            ax.plot([positions[i][0], positions[i+1][0]],
                   [positions[i][1], positions[i+1][1]],
                   'b-', linewidth=3)
        
        # Draw joints
        for pos in positions:
            ax.plot(pos[0], pos[1], 'ro', markersize=8)
        
        # Draw end effector
        if len(positions) > 0:
            ax.plot(positions[-1][0], positions[-1][1], 'go', markersize=10)
        
        # Set axis properties
        ax.set_xlim(-0.2, 0.5)
        ax.set_ylim(-0.3, 0.4)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Robot Arm Guitar Strumming Simulation')
        
        return ax


def test_strumming_motion():
    """Test the strumming motion simulation"""
    robot = RobotArmSimulator()
    
    # Generate strumming pattern
    pattern = ['down', 'up', 'down', 'up']
    all_trajectories = []
    
    for strum in pattern:
        traj = robot.generate_strum_trajectory(strum, speed=2.0)
        all_trajectories.extend(traj)
    
    # Animate the strumming
    fig, ax = plt.subplots(figsize=(8, 8))
    
    def animate(frame):
        if frame < len(all_trajectories):
            target_pos = all_trajectories[frame]
            robot.target_angles = robot.inverse_kinematics_2d(target_pos)
        
        robot.update()
        robot.visualize(ax)
        
    anim = FuncAnimation(fig, animate, frames=len(all_trajectories) + 50,
                        interval=20, repeat=True)
    
    plt.show()
    
    return robot, anim


if __name__ == "__main__":
    test_strumming_motion()