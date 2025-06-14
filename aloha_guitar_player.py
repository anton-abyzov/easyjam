#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha
import numpy as np
import cv2
import time
import math

class AlohaGuitarPlayer:
    def __init__(self):
        self.env = gym.make('gym_aloha/AlohaTransferCube-v0', render_mode='rgb_array')
        self.env.reset()
        
        # Guitar playing parameters
        self.strum_frequency = 2.0  # Hz
        self.strum_amplitude = 0.3
        self.chord_positions = {
            'G': {'fret_hand': [0.2, -0.3, 0.4, 0.1, 0.0, 0.0], 'name': 'G Major'},
            'C': {'fret_hand': [0.1, -0.2, 0.5, 0.2, 0.1, 0.0], 'name': 'C Major'},
            'D': {'fret_hand': [0.3, -0.4, 0.3, 0.0, -0.1, 0.0], 'name': 'D Major'},
            'Em': {'fret_hand': [0.0, -0.1, 0.6, 0.3, 0.2, 0.0], 'name': 'E Minor'},
            'Am': {'fret_hand': [0.1, -0.2, 0.5, 0.1, 0.0, 0.0], 'name': 'A Minor'}
        }
        self.current_chord = 'G'
        self.time_step = 0
        
    def get_guitar_action(self, t):
        """Generate action for guitar playing"""
        action = np.zeros(14)
        
        # LEFT ARM - Fretting hand (joints 0-6)
        # Position arm to hold chord
        chord_data = self.chord_positions[self.current_chord]
        fret_positions = chord_data['fret_hand']
        
        # Shoulder and elbow positioning for fretting
        action[0] = fret_positions[0]  # Shoulder pan
        action[1] = fret_positions[1]  # Shoulder lift
        action[2] = fret_positions[2]  # Elbow
        action[3] = fret_positions[3]  # Wrist 1
        action[4] = fret_positions[4]  # Wrist 2
        action[5] = fret_positions[5]  # Wrist 3
        action[6] = 0.8  # Gripper closed (pressing strings)
        
        # RIGHT ARM - Strumming hand (joints 7-13)
        # Create strumming motion
        strum_phase = 2 * math.pi * self.strum_frequency * t
        
        # Strumming motion
        action[7] = 0.3  # Shoulder pan (position over strings)
        action[8] = -0.5  # Shoulder lift (lower to guitar body)
        action[9] = 0.4  # Elbow bent
        
        # Wrist motion for strumming
        action[10] = self.strum_amplitude * math.sin(strum_phase)  # Wrist 1 (main strum)
        action[11] = 0.1 * math.sin(strum_phase * 2)  # Wrist 2 (slight variation)
        action[12] = 0.0  # Wrist 3
        action[13] = -0.5  # Gripper (holding pick position)
        
        return action
    
    def get_chord_progression(self, beat):
        """Simple chord progression: G - C - G - D"""
        progression = ['G', 'C', 'G', 'D', 'Em', 'C', 'Am', 'D']
        chord_index = (beat // 4) % len(progression)
        return progression[chord_index]
    
    def run_visualization(self):
        print("ALOHA Robot Guitar Player")
        print("=" * 50)
        print("Playing chord progression: G - C - G - D - Em - C - Am - D")
        print("Press 'q' to quit, 'r' to reset")
        print()
        
        steps = 0
        start_time = time.time()
        beat_counter = 0
        last_beat_time = start_time
        
        while True:
            current_time = time.time() - start_time
            
            # Update chord every 2 seconds (4 beats)
            if current_time - last_beat_time >= 2.0:
                beat_counter += 4
                last_beat_time = current_time
                self.current_chord = self.get_chord_progression(beat_counter)
                print(f"Chord: {self.chord_positions[self.current_chord]['name']}")
            
            # Get guitar playing action
            action = self.get_guitar_action(current_time)
            
            # Step environment
            observation, reward, terminated, truncated, info = self.env.step(action)
            
            # Render
            img = self.env.render()
            
            if img is not None:
                display_img = np.array(img, dtype=np.uint8)
                
                # Create info overlay
                info_height = 150
                info_img = np.ones((info_height, display_img.shape[1], 3), dtype=np.uint8) * 255
                
                # Add text
                cv2.putText(info_img, "ALOHA Guitar Player", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                cv2.putText(info_img, f"Current Chord: {self.chord_positions[self.current_chord]['name']}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 128, 0), 2)
                cv2.putText(info_img, f"Beat: {beat_counter % 16 + 1}/16", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(info_img, "Left Arm: Fretting | Right Arm: Strumming", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (64, 64, 64), 1)
                
                # Draw a simple guitar representation
                guitar_x = display_img.shape[1] - 200
                cv2.rectangle(info_img, (guitar_x, 20), (guitar_x + 150, 100), (139, 69, 19), -1)
                cv2.rectangle(info_img, (guitar_x + 30, 40), (guitar_x + 120, 80), (222, 184, 135), 2)
                
                # Draw strings
                for i in range(6):
                    y = 45 + i * 7
                    cv2.line(info_img, (guitar_x + 30, y), (guitar_x + 120, y), (0, 0, 0), 1)
                
                # Stack images
                combined = np.vstack([display_img, info_img])
                
                cv2.imshow('ALOHA Guitar Player', combined)
                
                key = cv2.waitKey(30) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.env.reset()
                    steps = 0
                    start_time = time.time()
                    beat_counter = 0
                    print("Reset!")
            
            steps += 1
            
            if terminated or truncated:
                self.env.reset()
        
        cv2.destroyAllWindows()
        self.env.close()

def create_strumming_pattern_demo():
    """Demonstrate different strumming patterns"""
    player = AlohaGuitarPlayer()
    
    print("\nStrumming Pattern Demo")
    print("1. Down strokes only")
    print("2. Down-Up pattern")
    print("3. Folk pattern (D-D-U-U-D-U)")
    print("4. Reggae pattern (U-U-U-U)")
    
    player.run_visualization()

if __name__ == "__main__":
    # Create and run the guitar player
    player = AlohaGuitarPlayer()
    player.run_visualization()