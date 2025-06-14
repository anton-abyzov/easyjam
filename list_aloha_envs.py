#!/usr/bin/env python3
import gymnasium as gym
import gym_aloha

print("Available ALOHA Environments:")
print("=============================\n")

aloha_envs = [env_id for env_id in gym.envs.registry.keys() if 'aloha' in env_id.lower()]

for env_id in sorted(aloha_envs):
    print(f"- {env_id}")
    try:
        env = gym.make(env_id)
        print(f"  Action space: {env.action_space}")
        print(f"  Observation space: {env.observation_space}")
        env.close()
    except Exception as e:
        print(f"  Error creating environment: {e}")
    print()