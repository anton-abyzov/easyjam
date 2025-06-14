#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha
import numpy as np
import cv2
import time

def visualize_aloha_opencv():
    """Simple visualization using OpenCV"""
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
    
    print(f"Action space: {env.action_space}")
    
    print("\nRunning visualization...")
    print("Press 'q' to quit, 'r' to reset environment")
    
    steps = 0
    total_reward = 0
    
    while True:
        # Random action
        action = env.action_space.sample()
        
        # Step the environment
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        # Get the rendered image
        img = env.render()
        
        if img is not None:
            # Create a copy and ensure it's the right format
            display_img = np.array(img, dtype=np.uint8)
            
            # Create info overlay on a separate image to avoid format issues
            info_height = 100
            info_img = np.ones((info_height, display_img.shape[1], 3), dtype=np.uint8) * 255
            
            # Add text to info image
            cv2.putText(info_img, f"Step: {steps}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(info_img, f"Reward: {reward:.3f} (Total: {total_reward:.3f})", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(info_img, "Press 'q' to quit, 'r' to reset", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Stack the images vertically
            combined = np.vstack([display_img, info_img])
            
            # Show the combined image
            cv2.imshow('ALOHA Robot Simulation', combined)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                observation, info = env.reset()
                steps = 0
                total_reward = 0
                print("Environment reset!")
        
        steps += 1
        
        if terminated or truncated:
            observation, info = env.reset()
            print(f"Episode ended after {steps} steps. Total reward: {total_reward:.3f}")
            steps = 0
            total_reward = 0
    
    cv2.destroyAllWindows()
    env.close()
    print("Visualization closed.")

def visualize_with_mujoco_native():
    """Use MuJoCo's native viewer through dm_control"""
    print("\nUsing native MuJoCo visualization...")
    import mujoco
    
    # Create environment
    env = gym.make('gym_aloha/AlohaTransferCube-v0')
    observation, info = env.reset()
    
    # Access the underlying MuJoCo model and data
    # For gym-aloha environments, we need to access the dm_control physics
    if hasattr(env.unwrapped, 'task'):
        # This is a dm_control environment wrapped by gym
        physics = env.unwrapped.task.physics
        model = physics.model._model
        data = physics.data._data
    elif hasattr(env.unwrapped, 'physics'):
        physics = env.unwrapped.physics
        model = physics.model._model
        data = physics.data._data
    elif hasattr(env.unwrapped, 'model') and hasattr(env.unwrapped, 'data'):
        model = env.unwrapped.model
        data = env.unwrapped.data
    else:
        print("Could not access MuJoCo model. Trying alternative viewer...")
        return visualize_simple_3d(env)
    
    print("\nMuJoCo Viewer Controls:")
    print("- Mouse drag: Rotate camera")
    print("- Right mouse drag: Pan camera") 
    print("- Scroll: Zoom in/out")
    print("- Press ESC to close viewer")
    
    with mujoco.viewer.launch_passive(model, data) as viewer:
        start_time = time.time()
        
        while viewer.is_running():
            step_start = time.time()
            
            # Random action
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                observation, info = env.reset()
            
            # Sync the viewer
            viewer.sync()
            
            # Control the simulation speed
            time_until_next_step = 1.0/60.0 - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
    
    env.close()

def visualize_simple_3d(env):
    """Simple 3D visualization fallback"""
    print("\nUsing simple render mode...")
    print("Controls: Press 'q' to quit")
    
    steps = 0
    while True:
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        
        # Try to render the environment
        frame = env.render()
        
        if frame is not None and isinstance(frame, np.ndarray):
            # Display the frame
            cv2.imshow('ALOHA Environment', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        steps += 1
        if steps % 100 == 0:
            print(f"Steps: {steps}")
        
        if terminated or truncated:
            env.reset()
    
    cv2.destroyAllWindows()
    env.close()

if __name__ == "__main__":
    print("ALOHA Robot 3D Model Visualization")
    print("==================================")
    print("\nAvailable visualization options:")
    print("1. OpenCV window visualization (2D camera view)")
    print("2. MuJoCo native 3D viewer (interactive 3D)")
    print("3. Explore environment structure")
    
    choice = input("\nSelect option (1, 2, or 3): ")
    
    if choice == "1":
        visualize_aloha_opencv()
    elif choice == "2":
        visualize_with_mujoco_native()
    elif choice == "3":
        # Explore the environment structure
        print("\nExploring environment structure...")
        env = gym.make('gym_aloha/AlohaTransferCube-v0')
        env.reset()
        
        print("\nEnvironment attributes:")
        for attr in dir(env.unwrapped):
            if not attr.startswith('_'):
                print(f"  - {attr}")
        
        print("\nTrying to access underlying components...")
        if hasattr(env.unwrapped, 'task'):
            print("  Found: task attribute (dm_control environment)")
        if hasattr(env.unwrapped, 'physics'):
            print("  Found: physics attribute")
        if hasattr(env.unwrapped, 'model'):
            print("  Found: model attribute")
            
        env.close()
    else:
        print("Invalid choice. Running OpenCV visualization...")
        visualize_aloha_opencv()