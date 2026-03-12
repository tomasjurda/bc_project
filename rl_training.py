"""
Module for training and evaluating a Reinforcement Learning (RL) agent
using Proximal Policy Optimization (PPO) in a custom RPG environment.
"""

import os
import pygame
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback


from source.rl.rpg_env import RpgEnv
from source.utils.sound_manager import SoundManager

# Directory paths for saving models and tensorboard logs
models_dir = "data/rl_models"
log_dir = "data/logs"
model_name = "ppo_rpg_agent"
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

    env = RpgEnv(render_mode=None)

    # Callback to periodically save the model during long training sessions
    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=models_dir, name_prefix="ppo_rpg_checkpoint"
    )

    # 2. Load or Create Model
    if os.path.exists(model_path):
        print(f"Found existing model: {model_path}")
        print("Continuing the training...")

        # Load existing model and attach the environment and logger
        model = PPO.load(model_path, env=env, tensorboard_log=log_dir)
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
        )
        reset_timesteps = True

    # 3. Execution
    print("Starting training. This may take a few hours. Press CTRL+C to stop safely.")
    try:
        model.learn(
            total_timesteps=20_000,
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
    env = RpgEnv(render_mode="human")
    model = PPO.load(model_path)

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

        if not running:
            break

        # Predict the next action based on the current observation
        action, _states = model.predict(obs)

        # Step the environment forward based on the agent's action
        obs, reward, terminated, truncated, info = env.step(action)
        print(
            f"reaction: {env.agent.cooldowns['reaction']:.2f}, action: {env.agent.current_action}, reward: {reward:.2f}"
        )

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
