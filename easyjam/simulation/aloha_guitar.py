"""ALOHA robot simulation for guitar strumming"""

import numpy as np
import gymnasium as gym
from typing import Dict, Optional, Tuple, List
import logging

# Try to import ALOHA environment
try:
    from gym_aloha import AlohaEnv
    ALOHA_AVAILABLE = True
except ImportError:
    ALOHA_AVAILABLE = False
    logging.warning("ALOHA environment not available. Install with: pip install gym-aloha")

class AlohaGuitarEnv:
    """ALOHA robot environment adapted for guitar strumming"""
    
    def __init__(self, render_mode: str = "human", camera_names: List[str] = None):
        self.render_mode = render_mode
        self.camera_names = camera_names or ["cam_high", "cam_low", "cam_left_wrist", "cam_right_wrist"]
        
        if ALOHA_AVAILABLE:
            # Initialize ALOHA environment
            self.env = gym.make(
                "aloha-v0",
                obs_type="pixels",
                render_mode=render_mode,
                camera_names=self.camera_names,
            )
            
            # Guitar position in ALOHA workspace
            self.guitar_position = np.array([0.3, 0.0, 0.1])  # x, y, z
            self.guitar_orientation = np.array([0, 0, 0])  # roll, pitch, yaw
            
            # Strumming parameters
            self.strum_height = 0.05  # Height above strings
            self.strum_depth = 0.03   # How deep to strum
            self.strum_width = 0.1    # Width of strumming motion
            
        else:
            self.env = None
            
        self.current_action = None
        self.is_strumming = False
        
    def reset(self):
        """Reset the environment"""
        if self.env:
            obs, info = self.env.reset()
            # Position robot arms for guitar playing
            self._position_for_guitar()
            return obs, info
        return None, {}
    
    def _position_for_guitar(self):
        """Position the robot arms for guitar playing"""
        # Left arm holds guitar neck (chord hand)
        # Right arm does strumming
        if self.env:
            # Move to initial position
            initial_action = np.zeros(14)  # 7 DOF per arm
            
            # Left arm - chord position
            initial_action[0:7] = [0.2, -0.3, 0.2, -1.5, 0.0, 1.0, 0.0]
            
            # Right arm - strumming position
            initial_action[7:14] = [0.3, 0.1, 0.15, -1.2, 0.0, 0.8, 0.0]
            
            for _ in range(50):  # Move to position over several steps
                self.env.step(initial_action)
    
    def generate_strum_action(self, strum_type: str = 'down', 
                            pattern_phase: float = 0.0) -> np.ndarray:
        """Generate action for strumming motion"""
        action = np.zeros(14)
        
        # Keep left arm (chord hand) relatively still
        action[0:7] = [0.2, -0.3, 0.2, -1.5, 0.0, 1.0, 0.0]
        
        # Right arm strumming motion
        base_pos = [0.3, 0.1, 0.15, -1.2, 0.0, 0.8, 0.0]
        
        if strum_type == 'down':
            # Downward strum
            z_offset = -self.strum_depth * pattern_phase
            wrist_angle = 0.2 * np.sin(pattern_phase * np.pi)
        elif strum_type == 'up':
            # Upward strum
            z_offset = self.strum_depth * (1 - pattern_phase)
            wrist_angle = -0.2 * np.sin(pattern_phase * np.pi)
        else:  # rest
            z_offset = self.strum_height
            wrist_angle = 0
        
        # Apply motion to right arm
        action[7] = base_pos[0]  # x
        action[8] = base_pos[1]  # y
        action[9] = base_pos[2] + z_offset  # z with strum motion
        action[10] = base_pos[3] + wrist_angle  # wrist rotation
        action[11] = base_pos[4]
        action[12] = base_pos[5]
        action[13] = base_pos[6]
        
        return action
    
    def step(self, action: np.ndarray):
        """Step the environment"""
        if self.env:
            return self.env.step(action)
        return None, 0, False, False, {}
    
    def render(self):
        """Render the environment"""
        if self.env:
            return self.env.render()
        return None
    
    def close(self):
        """Close the environment"""
        if self.env:
            self.env.close()


class GuitarStrummingSimulation:
    """High-level guitar strumming simulation using ALOHA"""
    
    def __init__(self, render_mode: str = "human"):
        self.env = AlohaGuitarEnv(render_mode=render_mode)
        self.current_pattern_phase = 0.0
        self.pattern_speed = 0.05  # Phase increment per step
        
    def reset(self):
        """Reset simulation"""
        return self.env.reset()
    
    def perform_strum(self, strum_type: str):
        """Perform a complete strum motion"""
        # Reset phase for new strum
        self.current_pattern_phase = 0.0
        
        # Execute strum over multiple steps for smooth motion
        while self.current_pattern_phase < 1.0:
            action = self.env.generate_strum_action(strum_type, self.current_pattern_phase)
            obs, reward, terminated, truncated, info = self.env.step(action)
            
            if self.env.render_mode == "human":
                self.env.render()
            
            self.current_pattern_phase += self.pattern_speed
            
            if terminated or truncated:
                break
                
        return obs
    
    def play_pattern(self, pattern: List[str], tempo_bpm: int = 120):
        """Play a strumming pattern"""
        import time
        
        beat_duration = 60.0 / tempo_bpm
        
        for strum in pattern:
            if strum in ['down', 'up']:
                self.perform_strum(strum)
            elif strum == 'rest':
                # Hold position
                time.sleep(beat_duration)
            
            # Small pause between strums
            time.sleep(beat_duration * 0.1)
    
    def close(self):
        """Close simulation"""
        self.env.close()


def test_aloha_guitar():
    """Test the ALOHA guitar simulation"""
    if not ALOHA_AVAILABLE:
        print("ALOHA environment not available. Please install with:")
        print("pip install gym-aloha")
        return
    
    print("Starting ALOHA Guitar Simulation...")
    sim = GuitarStrummingSimulation(render_mode="human")
    
    # Reset environment
    sim.reset()
    
    # Play a simple pattern
    pattern = ['down', 'up', 'down', 'up', 'rest', 'down', 'down', 'up']
    
    print("Playing strumming pattern...")
    sim.play_pattern(pattern, tempo_bpm=100)
    
    print("Simulation complete!")
    sim.close()


if __name__ == "__main__":
    test_aloha_guitar()