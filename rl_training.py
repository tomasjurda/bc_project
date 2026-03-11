import os
import pygame
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback


from source.rl.rpg_env import RpgEnv
from source.utils.sound_manager import SoundManager

# Cesta pro ukládání modelů
models_dir = "data/rl_models"
log_dir = "data/logs"
model_name = "ppo_rpg_agent"
model_path = f"{models_dir}/{model_name}.zip"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def train():
    print("--- TRÉNINK ---")
    # 1. Prostředí (Headless)
    SoundManager.init(enable_audio=False)
    SoundManager.load_all_sounds()

    env = RpgEnv(render_mode=None)

    checkpoint_callback = CheckpointCallback(
        save_freq=100000, save_path=models_dir, name_prefix="ppo_rpg_checkpoint"
    )

    # 2. Načtení nebo Vytvoření modelu
    if os.path.exists(model_path):
        print(f"Nalezen existující model: {model_path}")
        print("Načítám a pokračuji v tréninku...")

        model = PPO.load(model_path, env=env, tensorboard_log=log_dir)
        reset_timesteps = False
    else:
        print("Model nenalezen, vytvářím nový...")
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

    # Trénink
    print("Starting training. This may take a few hours. Press CTRL+C to stop safely.")
    try:
        model.learn(
            total_timesteps=20_000,
            reset_num_timesteps=reset_timesteps,
            callback=checkpoint_callback,
        )
    except KeyboardInterrupt:
        print("\nTrénink přerušen uživatelem. Ukládám současný stav...")

    # Uložení
    model.save(model_path)
    print("Model uložen.")


def watch():
    print("--- SLEDOVÁNÍ (ESC pro ukončení) ---")

    if not os.path.exists(model_path):
        print("Model neexistuje! Nejdřív spusť trénink.")
        return

    env = RpgEnv(render_mode="human")
    model = PPO.load(model_path)

    SoundManager.init(enable_audio=True)
    SoundManager.load_all_sounds()
    SoundManager.set_master_volume(0.4)

    obs, _ = env.reset()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not running:
            break

        # Predikce akce
        action, _states = model.predict(obs)

        # Krok hry
        obs, reward, terminated, truncated, info = env.step(action)
        print(
            f"reaction: {env.agent.cooldowns["reaction"]:.2f}, action: {env.agent.current_action}, reward: {reward:.2f}"
        )

        if terminated or truncated:
            obs, _ = env.reset()

    # Úklid po ukončení
    pygame.quit()
    print("Ukončeno.")


if __name__ == "__main__":
    mode = input("Vyber mód (train/watch): ").strip().lower()

    if mode == "train":
        train()
    elif mode == "watch":
        watch()
    else:
        print("Neznámý mód.")
