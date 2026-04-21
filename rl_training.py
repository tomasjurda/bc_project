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
check_dir = "data/rl_models/checkpoints"
model_name = "ppo_agent_new"
model_path = f"{models_dir}/{model_name}.zip"


# Ensure the required directories exist before starting
if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(check_dir):
    os.makedirs(check_dir)


def train(brain_type: str = "tree", timesteps: int = 100_000) -> None:
    """
    Initializes a headless training environment and trains a PPO model.
    Loads an existing model if one is found, otherwise creates a new one.
    """
    print(f"RL model training (Opponent: {brain_type}, Timesteps: {timesteps})")

    # 1. Environment Setup (Headless)
    SoundManager.init(enable_audio=False)
    SoundManager.load_all_sounds()

    env = CustomEnv(render_mode=None, brain_type=brain_type)

    # Callback to periodically save the model during long training sessions
    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=check_dir, name_prefix=f"{model_name}_checkpoint"
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
    print("Starting training. This may take a while. Press CTRL+C to stop safely.")
    try:
        model.learn(
            total_timesteps=timesteps,
            reset_num_timesteps=reset_timesteps,
            callback=checkpoint_callback,
        )
    except KeyboardInterrupt:
        print("\nTraining interrupted. Saving...")

    # Save the final model state
    model.save(model_path)
    print("Model saved.")


def watch(brain_type: str = "tree"):
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
    env = CustomEnv(render_mode="human", brain_type=brain_type)
    model = PPO.load(model_path, device="cpu")

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

        print(
            f"action: {current_action:>12},\t state: {current_state:>12},\t reward: {current_reward:.2f}"
        )

        # Reset the environment if the episode finishes# Reset the environment if the episode finishes
        if terminated or truncated:
            obs, _ = env.reset()

    # Cleanup after closing the window
    pygame.quit()
    print("Ending...")


if __name__ == "__main__":
    while True:
        mode = input("Choose mode (train/watch/quit): ").strip().lower()

        if mode == "quit":
            print("Exiting program")
            break

        elif mode == "train":
            # Prompt for brain type
            brain_input = (
                input("Enter opponent brain type (default 'tree'): ").strip().lower()
            )
            brain = brain_input if brain_input else "tree"

            # Prompt for timesteps
            timesteps_input = input(
                "Enter training timesteps (default 100000): "
            ).strip()
            try:
                timesteps_value = int(timesteps_input) if timesteps_input else 100_000
            except ValueError:
                print("Invalid input. Defaulting to 100,000 timesteps.")
                timesteps_value = 100_000

            train(brain_type=brain, timesteps=timesteps_value)

        elif mode == "watch":
            brain_input = (
                input("Enter opponent brain type (default 'tree'): ").strip().lower()
            )
            brain = brain_input if brain_input else "tree"

            watch(brain_type=brain)

        else:
            print("Unknown mode. Please choose train, watch, or quit.")
