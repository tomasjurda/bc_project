import os
import pygame
from stable_baselines3 import PPO


from rpg_env import RpgEnv
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
    SoundManager.volume = 0.0

    env = RpgEnv(render_mode=None)

    # 2. Načtení nebo Vytvoření modelu
    if os.path.exists(model_path):
        print(f"Nalezen existující model: {model_path}")
        print("Načítám a pokračuji v tréninku...")

        model = PPO.load(model_path, env=env, tensorboard_log=log_dir)
        reset_timesteps = False
    else:
        print("Model nenalezen, vytvářím nový...")
        model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir, ent_coef=0.01)
        reset_timesteps = True

    # 3. Trénink
    TIMESTEPS = 100000
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=reset_timesteps)

    # 4. Uložení
    model.save(f"{models_dir}/{model_name}")
    print(f"Model uložen.")


def watch():
    print("--- SLEDOVÁNÍ (ESC pro ukončení) ---")

    if not os.path.exists(model_path):
        print("Model neexistuje! Nejdřív spusť trénink.")
        return

    env = RpgEnv(render_mode="human")
    model = PPO.load(model_path)

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
        # if abs(reward) > 0:
        #    print(reward)

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
