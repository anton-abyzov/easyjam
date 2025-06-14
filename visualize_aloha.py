#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha
import numpy as np
import cv2
import time

def visualize_aloha_3d():
    print("Creating ALOHA environment...")
    env = gym.make('gym_aloha/AlohaTransferCube-v0', render_mode='rgb_array')
    
    print("Resetting environment...")
    observation, info = env.reset()
    
    print("\nEnvironment info:")
    if isinstance(observation, dict):
        print("Observation is a dictionary with keys:", list(observation.keys()))
        for key, value in observation.items():
            if hasattr(value, 'shape'):
                print(f"  {key} shape: {value.shape}")
    else:
        print(f"Observation shape: {observation.shape}")
    print(f"Action space: {env.action_space}")
    
    print("\nRunning visualization...")
    print("Press 'q' to quit, 'r' to reset environment")
    
    steps = 0
    while True:
        action = env.action_space.sample()
        
        observation, reward, terminated, truncated, info = env.step(action)
        
        img = env.render()
        
        if img is not None:
            # Ensure image is in the correct format
            if isinstance(img, np.ndarray):
                # Convert to uint8 if needed
                if img.dtype != np.uint8:
                    img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
                
                # Make a copy to ensure it's writable
                img = img.copy()
                
                cv2.putText(img, f"Step: {steps}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, f"Reward: {reward:.3f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                cv2.imshow('ALOHA Robot 3D Model', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                observation, info = env.reset()
                steps = 0
                print("Environment reset!")
        
        steps += 1
        
        if terminated or truncated:
            observation, info = env.reset()
            steps = 0
            print(f"Episode ended. Resetting...")
    
    cv2.destroyAllWindows()
    env.close()
    print("Visualization closed.")

def visualize_with_mujoco_viewer():
    print("\nUsing MuJoCo viewer for 3D visualization...")
    import mujoco
    import mujoco.viewer
    
    env = gym.make('gym_aloha/AlohaTransferCube-v0', obs_type='pixels', render_mode='rgb_array')
    observation, info = env.reset()
    
    viewer_launched = False
    
    print("\nMuJoCo Viewer Controls:")
    print("- Mouse drag: Rotate camera")
    print("- Right mouse drag: Pan camera")
    print("- Scroll: Zoom in/out")
    print("- Ctrl+A: Show/hide axes")
    print("- Ctrl+G: Show/hide grid")
    print("- Press ESC to close viewer")
    
    with mujoco.viewer.launch_passive(env.unwrapped._model, env.unwrapped._data) as viewer:
        viewer_launched = True
        start_time = time.time()
        
        while viewer.is_running():
            step_start = time.time()
            
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                observation, info = env.reset()
            
            viewer.sync()
            
            time_until_next_step = env.unwrapped._model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
    
    env.close()

if __name__ == "__main__":
    print("ALOHA Robot 3D Model Visualization")
    print("==================================")
    print("\nAvailable visualization options:")
    print("1. OpenCV window visualization")
    print("2. MuJoCo interactive 3D viewer")
    
    choice = input("\nSelect visualization method (1 or 2): ")
    
    if choice == "1":
        visualize_aloha_3d()
    elif choice == "2":
        visualize_with_mujoco_viewer()
    else:
        print("Invalid choice. Running OpenCV visualization by default...")
        visualize_aloha_3d()