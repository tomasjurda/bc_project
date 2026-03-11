from os.path import join

import gymnasium as gym
import numpy as np
import pygame

from source.core.settings import WINDOW_WIDTH, WINDOW_HEIGHT

from source.fsm.enemy_states import Basic_Enemy_Run

from source.entities.hostile_npc import HostileNPC

from source.utils.combat_manager import CombatManager
from source.utils.sprite_manager import SpriteManager
from source.utils.data_manager import DataManager

from source.sprites.sprite_group import AllSprites

from source.rl.rl_enemy import RL_Enemy


class RpgEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        # AKCE: 0:Idle, 1:Run, 2:Dodge, 3:Block, 4:L_Atk, 5:H_Atk, 6:Feint, 7:Break
        self.action_space = gym.spaces.Discrete(8)

        # POZOROVÁNÍ: [dist, npc_hp, npc_stamina, npc_action, p_hp, p_stamina, p_action]
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(23,), dtype=np.float32
        )

        pygame.init()
        if render_mode == "human":
            self.display_surface = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        else:
            self.display_surface = pygame.display.set_mode((1, 1), pygame.NOFRAME)

        SpriteManager.add_spritesheet(
            "player_model", join("graphics", "models", "Player.png")
        )
        SpriteManager.add_spritesheet(
            "enemy_model", join("graphics", "models", "Player_BLUE.png")
        )
        DataManager.load_all_data()

        self.clock = pygame.time.Clock()
        self.combat_handler = CombatManager()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.agent = None
        self.opponent = None
        self.last_agent_hp = None
        self.last_opp_hp = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.agent = RL_Enemy(
            (200, 200),
            [self.all_sprites],
            SpriteManager.get_spritesheet("player_model"),
            self.collision_sprites,
            player=None,
        )

        self.agent.states["RUN"]["state"] = Basic_Enemy_Run()

        self.opponent = HostileNPC(
            (600, 400),
            [self.all_sprites],
            SpriteManager.get_spritesheet("enemy_model"),
            self.collision_sprites,
            player=self.agent,
            brain_type="TREE",
        )

        self.opponent.states["RUN"]["state"] = Basic_Enemy_Run()

        self.agent.player = self.opponent

        # Reset statistik
        self.last_agent_hp = self.agent.hitpoints
        self.last_opp_hp = self.opponent.hitpoints

        return np.array(self.agent.get_context_rl(), dtype=np.float32), {}

    def step(self, action):
        self.agent.set_action(action)

        total_reward = 0
        terminated = False
        truncated = False

        for _ in range(4):
            dt = 1 / 60.0

            self.agent.update(dt)
            self.opponent.update(dt)

            # COMBAT HANDLER
            self.combat_handler.check_hits(self.agent, [self.opponent])

            # VÝPOČET ODMĚNY
            step_reward = self._calculate_reward()
            total_reward += step_reward

            # Kontrola konce hry
            if self.agent.hitpoints <= 0 or self.opponent.hitpoints <= 0:
                terminated = True
                # Extra odměna/trest za výsledek
                if self.opponent.hitpoints <= 0:
                    total_reward += 100  # Výhra
                if self.agent.hitpoints <= 0:
                    total_reward -= 50  # Prohra
                break

        # 3. Vykreslení (jen pokud se díváme)
        if self.render_mode == "human":
            self.display_surface.fill("gray")
            self.all_sprites.draw(
                self.display_surface, (0, 0), WINDOW_WIDTH, WINDOW_HEIGHT, 1
            )

            pygame.event.pump()

            pygame.display.update()
            self.clock.tick(20)

        # 4. Výstup
        obs = np.array(self.agent.get_context_rl(), dtype=np.float32)
        info = {}

        return obs, total_reward, terminated, truncated, info

    def _calculate_reward(self):
        # 1. TACTICAL TIME PENALTY
        reward = -0.01

        dist = pygame.Vector2(self.agent.hitbox_rect.center).distance_to(
            pygame.Vector2(self.opponent.hitbox_rect.center)
        )

        agent_state_name = self.agent.current_state_name
        opp_state_name = self.opponent.current_state_name

        MELEE_RANGE = 70

        # 2. THE TRAVERSAL PHASE
        if dist > MELEE_RANGE:
            if "RUN" in agent_state_name:
                reward += 5.0
            elif agent_state_name in [
                "BLOCK",
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
                "DODGE",
                "FEINT",
            ]:
                reward -= 10.0
            else:
                reward -= 2.0

        # 3. THE COMBAT PHASE (Distance <= 70)
        else:
            if agent_state_name == "BLOCK" and opp_state_name not in [
                "LIGHT_ATTACK",
                "HEAVY_ATTACK",
            ]:
                reward -= 0.05

        # 4. HP DELTAS (The Ultimate Goal)
        dmg_dealt = self.last_opp_hp - self.opponent.hitpoints
        if dmg_dealt > 0:
            reward += (dmg_dealt * 2.0) + 10.0  # Massive reward for landing a hit

        dmg_taken = self.last_agent_hp - self.agent.hitpoints
        if dmg_taken > 0:
            reward -= (dmg_taken * 2.0) + 5.0  # Massive penalty for getting hit

        # Reward successfully dodging or blocking an INCOMING attack
        if self.opponent.attack_hitbox and dmg_taken == 0 and dist <= MELEE_RANGE:
            if "BLOCK" in agent_state_name or "DODGE" in agent_state_name:
                reward += 3.0
                if self.agent.is_parying:
                    reward += 1.0

        # Stun status
        if "STUN" in agent_state_name:
            reward -= 0.5
        if "STUN" in opp_state_name:
            reward += 1.0

        # 5. STAMINA MANAGEMENT
        if (self.agent.stamina / self.agent.max_stamina) < 0.1:
            reward -= 0.05

        # Update cached HP for the next step
        self.last_opp_hp = self.opponent.hitpoints
        self.last_agent_hp = self.agent.hitpoints

        return reward
