# ALOHA Robot Control & Reinforcement Learning Explanation

## 1. How the Robot Moves - Current Implementation

### Direct Control (What we're using now)
The current code uses **direct kinematic control** - we manually specify joint positions:

```python
def get_strumming_action(self, pattern_value, progress):
    action = np.zeros(14)  # 14 joints total
    
    # Direct position control for each joint:
    action[7] = 0.2   # Shoulder pan angle
    action[8] = -0.6  # Shoulder lift angle
    action[9] = 0.7   # Elbow bend angle
    action[10] = pattern_value * 0.4 * strum_curve  # Wrist motion
```

**Key Points:**
- Each action value (-1.0 to 1.0) directly controls a joint position
- We use mathematical functions (sine waves) to create smooth motions
- No learning involved - pure programmatic control

### The 14 Degrees of Freedom
```
Left Arm (joints 0-6):     Right Arm (joints 7-13):
├── Shoulder Pan           ├── Shoulder Pan
├── Shoulder Lift          ├── Shoulder Lift
├── Elbow                  ├── Elbow
├── Wrist 1                ├── Wrist 1
├── Wrist 2                ├── Wrist 2
├── Wrist 3                ├── Wrist 3
└── Gripper                └── Gripper
```

## 2. Adding Reinforcement Learning

### Current gym-aloha Environment
The gym-aloha package provides:
- **State/Observation**: Camera images (480x640x3)
- **Action Space**: 14 continuous values [-1, 1]
- **Reward Function**: Task-specific (e.g., cube transfer task)

### How to Train with RL

```python
import gymnasium as gym
import gym_aloha
from stable_baselines3 import PPO

# Create custom reward function for guitar strumming
class GuitarStrummingEnv(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.target_rhythm = [1, 0, 1, 0, 1, 0, 1, 0]
        self.beat_index = 0
        
    def step(self, action):
        obs, _, terminated, truncated, info = self.env.step(action)
        
        # Custom reward based on:
        # 1. Correct strumming timing
        # 2. Smooth motion
        # 3. Proper wrist angle
        reward = self.calculate_strumming_reward(action)
        
        return obs, reward, terminated, truncated, info
    
    def calculate_strumming_reward(self, action):
        # Reward components:
        timing_reward = self.check_timing()
        smoothness_reward = self.check_smoothness(action)
        position_reward = self.check_position(action)
        
        return timing_reward + smoothness_reward + position_reward

# Train the model
env = GuitarStrummingEnv(gym.make('gym_aloha/AlohaTransferCube-v0'))
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)
```

## 3. Different Learning Approaches

### A. Imitation Learning (Recommended for Guitar)
```python
# Record expert demonstrations
demonstrations = []
for episode in range(100):
    obs = env.reset()
    for step in range(1000):
        # Expert policy (our programmed strumming)
        action = get_expert_strumming_action(step)
        next_obs, reward, done, info = env.step(action)
        demonstrations.append((obs, action))
        obs = next_obs

# Train using behavior cloning
from imitation.algorithms import bc
bc_trainer = bc.BC(
    observation_space=env.observation_space,
    action_space=env.action_space,
    demonstrations=demonstrations,
)
bc_trainer.train(n_epochs=100)
```

### B. Reinforcement Learning from Scratch
```python
# Define reward function for good strumming
def strumming_reward(obs, action, info):
    rewards = {}
    
    # Rhythm accuracy (most important)
    rewards['rhythm'] = calculate_rhythm_score(action, target_beat)
    
    # Smoothness (avoid jerky motions)
    rewards['smoothness'] = -np.sum(np.abs(np.diff(action[7:13])))
    
    # Energy efficiency
    rewards['efficiency'] = -np.sum(np.abs(action[7:13]))
    
    # Stay in valid strumming zone
    if is_in_strumming_zone(action):
        rewards['position'] = 1.0
    else:
        rewards['position'] = -5.0
    
    return sum(rewards.values())
```

### C. Hybrid Approach (Best Results)
1. Start with programmed motions
2. Use imitation learning to create base policy
3. Fine-tune with RL for specific patterns

## 4. Training Pipeline

```python
# Complete training example
class AlohaGuitarTrainer:
    def __init__(self):
        self.env = gym.make('gym_aloha/AlohaTransferCube-v0')
        self.model = None
        
    def collect_demonstrations(self, num_episodes=50):
        """Collect expert demonstrations"""
        demos = []
        for _ in range(num_episodes):
            obs = self.env.reset()
            for t in range(1000):
                # Use our programmed controller
                action = self.get_expert_action(t)
                next_obs, _, done, _ = self.env.step(action)
                demos.append({
                    'obs': obs,
                    'action': action,
                    'next_obs': next_obs
                })
                obs = next_obs
                if done:
                    break
        return demos
    
    def train_imitation(self, demos):
        """Train using behavior cloning"""
        # Implementation here
        pass
    
    def train_rl(self, pretrained_model=None):
        """Fine-tune with reinforcement learning"""
        if pretrained_model:
            model = PPO.load(pretrained_model)
        else:
            model = PPO("MlpPolicy", self.env)
        
        model.learn(total_timesteps=500000)
        return model
```

## 5. Why We're Not Using RL Yet

1. **Complexity**: Direct control is simpler for rhythmic patterns
2. **No Guitar in Environment**: The default ALOHA environment doesn't have a guitar
3. **Reward Design**: Defining "good strumming" mathematically is challenging
4. **Training Time**: RL would take hours/days to learn basic strumming

## 6. How to Add RL Training

To add reinforcement learning:

1. **Create Custom Environment**:
   ```python
   class AlohaGuitarEnv(gym.Env):
       def __init__(self):
           super().__init__()
           self.action_space = gym.spaces.Box(-1, 1, (14,))
           self.observation_space = gym.spaces.Box(0, 255, (480, 640, 3))
           
       def step(self, action):
           # Implement guitar-specific rewards
           pass
   ```

2. **Define Reward Function**:
   - Timing accuracy: +1 for hitting beat, -1 for missing
   - Smoothness: Penalize jerky motions
   - String contact: Reward when in strumming zone
   - Pattern completion: Bonus for full pattern

3. **Train Model**:
   ```python
   model = PPO("CnnPolicy", AlohaGuitarEnv(), 
               learning_rate=3e-4,
               n_steps=2048,
               batch_size=64)
   model.learn(total_timesteps=1000000)
   ```

## Summary

**Current Approach**: Direct kinematic control with mathematical functions
**RL Potential**: Could learn complex patterns and adapt to different guitars
**Best Practice**: Start with programmed motions, use imitation learning, then fine-tune with RL

The key insight is that RL is powerful but not always necessary. For rhythmic tasks like strumming, direct control often works better than learned policies.