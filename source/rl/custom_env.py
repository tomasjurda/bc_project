"""
Module defining the custom Gymnasium environment for training the RL agent.
"""

from typing import Any
import gymnasium as gym
import numpy as np
import pygame

from source.core.settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SHARED_ACTION_MAP,
    MELEE_RANGE,
)

from source.states.enemy_states import Basic_Enemy_Run

from source.entities.hostile_npc import HostileNPC

from source.utils.combat_manager import CombatManager
from source.utils.sprite_manager import SpriteManager
from source.utils.data_manager import DataManager

from source.sprites.sprite_group import AllSprites

from source.rl.rl_enemy import RLEnemy


class CustomEnv(gym.Env):
    """
    Custom Gymnasium environment for an Souls-like combat scenario.

    The environment handles a 1v1 combat situation where an RL agent learns
    to fight against a rule-based or tree-based NPC.

    Attributes:
        render_mode (str | None): Specifies if the environment should be rendered ("human" or None).
        action_space (gym.spaces.Discrete): The discrete actions available to the agent.
        observation_space (gym.spaces.Box): The continuous observation space of the agent.
        display_surface (pygame.Surface): The Pygame surface used for rendering.
        clock (pygame.time.Clock): Pygame clock to control frame rate during rendering.
        all_sprites (AllSprites): Group containing all rendered entities.
        collision_sprites (pygame.sprite.Group): Group handling environment collisions.
        agent (RLEnemy | None): The Reinforcement Learning agent being trained.
        opponent (HostileNPC | None): The opponent NPC the agent fights against.
        last_agent_hp (int | float | None): The agent's HP from the previous step (for reward calculation).
        last_opp_hp (int | float | None): The opponent's HP from the previous step (for reward calculation).
    """

    def __init__(
        self, render_mode: str | None = None, brain_type: str = "tree"
    ) -> None:
        """
        Initializes the RPG environment, defining observation and action spaces.

        Args:
            render_mode (str | None): "human" to display the Pygame window, or None for headless training.
            brain_type (str): The logic/brain type for the opponent NPC.
        """
        super().__init__()
        self.render_mode = render_mode
        self.debug_mode = False
        self.brain_type = brain_type

        self.max_steps = 1800  # 30 seconds at 60 FPS
        self.current_step = 0

        # ACTIONS: 0:Idle, 1:Run, 2:Dodge, 3:Block, 4:L_Atk, 5:H_Atk, 6:Feint, 7:Break
        self.action_space = gym.spaces.Discrete(8)

        # OBSERVATION: [dist, npc_hp, npc_stamina, npc_action (onehot), p_hp, p_stamina, p_action (onehot)] (23 features total)
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(23,), dtype=np.float32
        )

        pygame.init()

        # Setup display based on render mode
        if render_mode == "human":
            self.display_surface = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        else:
            self.display_surface = pygame.display.set_mode((1, 1), pygame.NOFRAME)

        # Preload necessary sprite models and data
        SpriteManager.load_sprites()
        DataManager.load_map_and_npc_data()

        self.clock = pygame.time.Clock()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        # Entity placeholders
        self.agent = None
        self.opponent = None

        # Stat trackers for reward calculation
        self.last_agent_hp = None
        self.last_opp_hp = None
        self.out_of_combat_punishment = 0
        self.pasive_punishment = 0

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict]:
        """
        Resets the environment to its initial state, spawning the agent and opponent.

        Args:
            seed (int | None): Optional random seed for environment reproducibility.
            options (dict | None): Optional additional settings for resetting.

        Returns:
            tuple: A tuple containing the initial observation array and an info dictionary.
        """
        super().reset(seed=seed)

        self.current_step = 0

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        # Instantiate the Reinforcement Learning agent
        self.agent = RLEnemy(
            (200, 200),
            [self.all_sprites],
            SpriteManager.get_spritesheet("rl_mlp"),
            self.collision_sprites,
            player=None,
        )

        # Force the agent's base RUN state to use the basic enemy run logic
        self.agent.states["RUN"]["state"] = Basic_Enemy_Run()

        # Instantiate the Opponent NPC using the Decision Tree ("TREE") brain
        self.opponent = HostileNPC(
            (600, 400),
            [self.all_sprites],
            SpriteManager.get_spritesheet(self.brain_type),
            self.collision_sprites,
            player=self.agent,
            brain_type=self.brain_type,
        )

        self.opponent.states["RUN"]["state"] = Basic_Enemy_Run()

        # Assign the opponent as the target for the agent
        self.agent.player = self.opponent

        # Reset HP tracking statistics
        self.last_agent_hp = self.agent.hitpoints
        self.last_opp_hp = self.opponent.hitpoints
        self.out_of_combat_punishment = 0
        self.pasive_punishment = 0

        # Return initial observation (normalized context data) and empty info dict
        return np.array(self.agent.get_context_rl(), dtype=np.float32), {}

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        """
        Advances the environment by one logical RL step (which comprises 15 rendered frames).

        Args:
            action (int): The integer code of the action chosen by the RL agent.

        Returns:
            tuple: Contains (observation, reward, terminated, truncated, info).
        """
        self.agent.set_action(action)

        total_reward = 0
        terminated = False
        truncated = False

        FRAME_SKIP = 15

        # Run 15 game frames per 1 RL step to allow animations and physics to unfold
        for _ in range(FRAME_SKIP):
            dt = 1 / 60.0

            self.agent.update(dt)
            self.opponent.update(dt)
            CombatManager.check_hits(self.agent, [self.opponent])

            self.current_step += 1

            # Reward calculation
            step_reward = self._calculate_reward()
            total_reward += step_reward

            # Render the environment (only if being watched by a human)
            if self.render_mode == "human":
                self.display_surface.fill("gray")
                self.all_sprites.draw(
                    self.display_surface,
                    (0, 0),
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                    self.debug_mode,
                )

                pygame.event.pump()
                pygame.display.update()
                self.clock.tick(60)

            if not terminated and self.current_step >= self.max_steps:
                truncated = True
                total_reward += (self.agent.hitpoints - self.opponent.hitpoints) * 50

            # Check for episode termination (death of either entity)
            if self.agent.hitpoints <= 0 or self.opponent.hitpoints <= 0:
                terminated = True
                # Extra win/loss flat reward modifiers
                if self.opponent.hitpoints <= 0:
                    total_reward += 100  # Win
                if self.agent.hitpoints <= 0:
                    total_reward -= 50  # Loss
                break

        # Generate Output
        obs = np.array(self.agent.get_context_rl(), dtype=np.float32)
        info = {}

        return obs, total_reward, terminated, truncated, info

    def _calculate_reward(self) -> float:
        """
        Calculates the reward for the agent based on spacing, combat events, and resource management.
        """
        # Small penalty every frame to encourage ending the fight quickly
        reward = -0.1

        dist = pygame.Vector2(self.agent.hitbox_rect.center).distance_to(
            pygame.Vector2(self.opponent.hitbox_rect.center)
        )

        agent_state_name = self.agent.current_state_name
        opp_state_name = self.opponent.current_state_name

        action_str = SHARED_ACTION_MAP.get(int(self.agent.current_action), "IDLE")

        # Spacing and aggresion
        if dist > MELEE_RANGE:
            self.pasive_punishment = 0

            if "RUN" in agent_state_name:
                self.out_of_combat_punishment = 0
                reward += 2.5
            elif agent_state_name in ["BLOCK", "LIGHT_ATTACK", "HEAVY_ATTACK"]:
                self.out_of_combat_punishment += 0.25
            else:
                self.out_of_combat_punishment += 0.05
        else:
            self.out_of_combat_punishment = 0
            reward += 0.25

            if agent_state_name in ["IDLE", "RUN"] and self.agent.stamina >= 0.7:
                self.pasive_punishment += 0.25
            elif agent_state_name in ["LIGHT_ATTACK", "HEAVY_ATTACK"]:
                self.pasive_punishment = 0
            elif agent_state_name in ["BLOCK", "DODGE"]:
                if (
                    opp_state_name not in ["LIGHT_ATTACK", "HEAVY_ATTACK"]
                    and self.agent.stamina >= 0.7
                ):
                    self.pasive_punishment += 0.1
                else:
                    self.pasive_punishment = 0

        reward -= self.out_of_combat_punishment + self.pasive_punishment

        # Punish trying to BREAK when not stunned
        if agent_state_name != "STUN" and action_str == "BREAK":
            reward -= 2.5

        # Punish trying to FEINT when not winding up a heavy attack
        if action_str == "FEINT":
            if agent_state_name == "HEAVY_ATTACK" and (
                opp_state_name == "DODGE" or dist > MELEE_RANGE
            ):
                reward += 5.0
            else:
                reward -= 1.0

        # HP deltas
        dmg_dealt = self.last_opp_hp - self.opponent.hitpoints
        if dmg_dealt > 0:
            reward += (dmg_dealt * 2.0) + 10.0

        dmg_taken = self.last_agent_hp - self.agent.hitpoints
        if dmg_taken > 0:
            reward -= (dmg_taken * 2.0) + 5.0

        # Combat events
        if self.opponent.attack_hitbox and dmg_taken == 0 and dist <= MELEE_RANGE:
            if "BLOCK" in agent_state_name or "DODGE" in agent_state_name:
                reward += 3.0
                if self.agent.is_parying:
                    reward += 1.0

        if (
            action_str == "HEAVY_ATTACK" or agent_state_name == "HEAVY_ATTACK"
        ) and opp_state_name == "BLOCK":
            reward += 10.0

        if "STUN" in agent_state_name:
            reward -= 1.0
        if "STUN" in opp_state_name:
            reward += 2.5

        if (self.agent.stamina / self.agent.max_stamina) < 0.2:
            reward -= 0.5

        # Update cached HP for the next step
        self.last_opp_hp = self.opponent.hitpoints
        self.last_agent_hp = self.agent.hitpoints

        return reward
