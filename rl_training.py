"""
Module for training and evaluating a Reinforcement Learning (RL) agent
using Proximal Policy Optimization (PPO) in a custom environment.
"""

import os
import pygame
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback


from source.rl.custom_env import CustomEnv
from source.utils.sound_manager import SoundManager

from source.core.settings import SHARED_ACTION_MAP


# Directory paths for saving models and tensorboard logs
models_dir = "data/rl_models"
log_dir = "data/logs"
model_name = "ppo_agent"
model_path = f"{models_dir}/{model_name}.zip"


# Ensure the required directories exist before starting
if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def train() -> None:
    """
    Initializes a headless training environment and trains a PPO model.
    Loads an existing model if one is found, otherwise creates a new one.
    """
    print("RL model training")

    # 1. Environment Setup (Headless)
    SoundManager.init(enable_audio=False)
    SoundManager.load_all_sounds()

    env = CustomEnv(render_mode=None)

    # Callback to periodically save the model during long training sessions
    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=models_dir, name_prefix="ppo_agent_checkpoint"
    )

    # 2. Load or Create Model
    if os.path.exists(model_path):
        print(f"Found existing model: {model_path}")
        print("Continuing the training...")

        # Load existing model and attach the environment and logger
        model = PPO.load(model_path, env=env, tensorboard_log=log_dir, device="cpu")
        reset_timesteps = False
    else:
        print("Model not found, creating new...")
        # Initialize a new PPO model with a Multi-Layer Perceptron (MLP) policy
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            tensorboard_log=log_dir,
            ent_coef=0.01,
            learning_rate=0.0003,
            n_steps=2048,
            batch_size=64,
            device="cpu",
        )
        reset_timesteps = True

    # 3. Execution
    print("Starting training. This may take a few hours. Press CTRL+C to stop safely.")
    try:
        model.learn(
            total_timesteps=100_000,
            reset_num_timesteps=reset_timesteps,
            callback=checkpoint_callback,
        )
    except KeyboardInterrupt:
        print("\nTraining interrupted. Saving...")

    # Save the final model state
    model.save(model_path)
    print("Model saved.")


def watch():
    """
    Initializes a human-rendered environment and watches a trained PPO model play.
    Allows the user to exit safely by pressing the ESC key.
    """
    print("Spectating (ESC for escape) ---")

    if not os.path.exists(model_path):
        print("Model doesnt exist, train first.")
        return

    # Initialize audio for the visual presentation
    SoundManager.init(enable_audio=True)
    SoundManager.load_all_sounds()
    SoundManager.set_master_volume(0.4)

    # Render mode is set to human to display the Pygame window
    env = CustomEnv(render_mode="human")
    model = PPO.load(model_path, device="cpu")

    last_action = None
    last_state = None
    last_reward = 0

    obs, _ = env.reset()
    running = True
    while running:
        # Handle Pygame window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_x:
                    env.debug_mode = not env.debug_mode

        if not running:
            break

        # Predict the next action based on the current observation
        action, _states = model.predict(obs)

        # Step the environment forward based on the agent's action
        obs, reward, terminated, truncated, info = env.step(action)

        current_action = SHARED_ACTION_MAP[int(env.agent.current_action)]
        current_state = env.agent.current_state_name
        current_reward = reward

        if (
            current_action != last_action
            or current_state != last_state
            or current_reward != last_reward
        ):
            print(
                f"action: {current_action:>12},\t state: {current_state:>12},\t reward: {current_reward:.2f}"
            )
            last_action = current_action
            last_state = current_state
            last_reward = current_reward

        # Reset the environment if the episode finishes# Reset the environment if the episode finishes
        if terminated or truncated:
            obs, _ = env.reset()

    # Cleanup after closing the window
    pygame.quit()
    print("Ending...")


if __name__ == "__main__":
    mode = input("Choose mode (train/watch): ").strip().lower()

    if mode == "train":
        train()
    elif mode == "watch":
        watch()
    else:
        print("Unknown mode.")
