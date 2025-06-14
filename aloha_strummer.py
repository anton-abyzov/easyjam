#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha
import numpy as np
import cv2
import time
import math

class AlohaStrummer:
    def __init__(self):
        self.env = gym.make('gym_aloha/AlohaTransferCube-v0', render_mode='rgb_array')
        self.env.reset()
        
        # Strumming patterns (1 = down, -1 = up, 0 = rest)
        self.patterns = {
            'basic_down': {
                'pattern': [1, 0, 1, 0, 1, 0, 1, 0],
                'name': 'Basic Down Strokes',
                'bpm': 120
            },
            'down_up': {
                'pattern': [1, -1, 1, -1, 1, -1, 1, -1],
                'name': 'Down-Up Pattern',
                'bpm': 120
            },
            'folk': {
                'pattern': [1, 0, 1, -1, 0, -1, 1, -1],
                'name': 'Folk Pattern (D-D-U--U-D-U)',
                'bpm': 100
            },
            'reggae': {
                'pattern': [0, -1, 0, -1, 0, -1, 0, -1],
                'name': 'Reggae Up-Strokes',
                'bpm': 90
            },
            'rock': {
                'pattern': [1, 0, 1, 1, -1, 1, -1, 0],
                'name': 'Rock Pattern',
                'bpm': 140
            },
            'slow_ballad': {
                'pattern': [1, 0, 0, 0, -1, 0, 1, 0],
                'name': 'Slow Ballad',
                'bpm': 70
            }
        }
        
        self.current_pattern = 'basic_down'
        self.pattern_index = 0
        self.last_beat_time = time.time()
        
    def get_strumming_action(self, pattern_value, progress):
        """Generate smooth strumming motion for right arm"""
        action = np.zeros(14)
        
        # LEFT ARM - Keep stationary (human plays chords)
        action[0:7] = 0.0  # All left arm joints neutral
        
        # RIGHT ARM - Strumming motion (joints 7-13)
        # Position arm in strumming position
        action[7] = 0.2   # Shoulder pan (slight angle)
        action[8] = -0.6  # Shoulder lift (lowered to guitar level)
        action[9] = 0.7   # Elbow (bent appropriately)
        
        # Strumming motion in wrist
        if pattern_value != 0:  # If there's a strum
            # Create smooth strumming motion
            strum_curve = math.sin(progress * math.pi)
            
            # Wrist rotation for strum
            action[10] = pattern_value * 0.4 * strum_curve  # Main strum motion
            action[11] = pattern_value * 0.1 * strum_curve  # Secondary wrist motion
            action[12] = 0.05 * math.sin(progress * 2 * math.pi)  # Slight variation
            
        else:  # Rest position
            action[10] = 0.0
            action[11] = 0.0
            action[12] = 0.0
        
        # Gripper in pick-holding position
        action[13] = -0.3
        
        return action
    
    def run_strummer(self):
        print("ALOHA Robot Strummer")
        print("=" * 50)
        print("Right arm strumming patterns - Left arm free for human player")
        print("\nControls:")
        print("  'q' - Quit")
        print("  'r' - Reset")
        print("  '1-6' - Select strumming pattern")
        print()
        
        # List patterns
        for i, (key, pattern) in enumerate(self.patterns.items(), 1):
            print(f"  {i}. {pattern['name']} ({pattern['bpm']} BPM)")
        print()
        
        steps = 0
        
        while True:
            current_time = time.time()
            pattern_data = self.patterns[self.current_pattern]
            
            # Calculate beat timing
            beat_duration = 60.0 / pattern_data['bpm'] / 2  # 8th notes
            
            # Check if it's time for next beat
            if current_time - self.last_beat_time >= beat_duration:
                self.pattern_index = (self.pattern_index + 1) % len(pattern_data['pattern'])
                self.last_beat_time = current_time
            
            # Calculate progress within current beat (0 to 1)
            beat_progress = (current_time - self.last_beat_time) / beat_duration
            
            # Get current strum direction
            current_strum = pattern_data['pattern'][self.pattern_index]
            
            # Generate action
            action = self.get_strumming_action(current_strum, beat_progress)
            
            # Step environment
            observation, reward, terminated, truncated, info = self.env.step(action)
            
            # Render
            img = self.env.render()
            
            if img is not None:
                display_img = np.array(img, dtype=np.uint8)
                
                # Create info overlay
                info_height = 200
                info_img = np.ones((info_height, display_img.shape[1], 3), dtype=np.uint8) * 240
                
                # Title
                cv2.putText(info_img, "ALOHA Strummer - Right Arm Only", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                
                # Current pattern
                cv2.putText(info_img, f"Pattern: {pattern_data['name']}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 128, 0), 2)
                cv2.putText(info_img, f"BPM: {pattern_data['bpm']}", (10, 85), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                
                # Pattern visualization
                pattern_y = 120
                cv2.putText(info_img, "Pattern: ", (10, pattern_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                
                # Draw pattern
                for i, strum in enumerate(pattern_data['pattern']):
                    x = 100 + i * 40
                    color = (0, 255, 0) if i == self.pattern_index else (128, 128, 128)
                    
                    if strum == 1:  # Down
                        cv2.arrowedLine(info_img, (x, pattern_y - 20), (x, pattern_y + 10), color, 2)
                    elif strum == -1:  # Up
                        cv2.arrowedLine(info_img, (x, pattern_y + 10), (x, pattern_y - 20), color, 2)
                    else:  # Rest
                        cv2.circle(info_img, (x, pattern_y - 5), 3, color, -1)
                
                # Instructions
                cv2.putText(info_img, "Press 1-6 to change pattern", (10, 160), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (64, 64, 64), 1)
                cv2.putText(info_img, "Left arm free for chord playing", (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (64, 64, 64), 1)
                
                # Stack images
                combined = np.vstack([display_img, info_img])
                
                cv2.imshow('ALOHA Strummer', combined)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.env.reset()
                    steps = 0
                    self.pattern_index = 0
                    print("Reset!")
                elif ord('1') <= key <= ord('6'):
                    pattern_keys = list(self.patterns.keys())
                    pattern_idx = key - ord('1')
                    if pattern_idx < len(pattern_keys):
                        self.current_pattern = pattern_keys[pattern_idx]
                        self.pattern_index = 0
                        print(f"Switched to: {self.patterns[self.current_pattern]['name']}")
            
            steps += 1
            
            if terminated or truncated:
                self.env.reset()
        
        cv2.destroyAllWindows()
        self.env.close()

if __name__ == "__main__":
    strummer = AlohaStrummer()
    strummer.run_strummer()