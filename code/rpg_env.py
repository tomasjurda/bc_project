import gymnasium as gym
import numpy as np
import pygame
from os.path import join
import os

from rl_enemy import RL_Enemy
from npc import NPC
from combat_handler import CombatHandler
from settings import *
from sprite_group import AllSprites
from enemy_states import Basic_Enemy_Run

class RpgEnv(gym.Env):
    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        
        # AKCE: 0:Idle, 1:Run, 2:Dodge, 3:Block, 4:L_Atk, 5:H_Atk, 6:Feint, 7:Break
        self.action_space = gym.spaces.Discrete(8)
        
        # POZOROVÁNÍ: [dist, npc_hp, npc_stamina, npc_action, p_hp, p_stamina, p_action]
        self.observation_space = gym.spaces.Box(
            low=0.0, 
            high=1.0, 
            shape=(19,),
            dtype=np.float32
        )
        
        pygame.init()
        if render_mode == "human":
            self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            self.display_surface = pygame.display.set_mode((1, 1), pygame.NOFRAME)

        self.clock = pygame.time.Clock()
        self.combat_handler = CombatHandler()


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group() 
        
        self.agent = RL_Enemy(
            (200, 200), [self.all_sprites], 
            pygame.image.load(join('graphics', 'models', 'Player.png')), 
            self.collision_sprites, 
            player=None
        )
        
        self.agent.states["RUN"]["state"] = Basic_Enemy_Run()

        self.opponent = NPC(
            (600, 400), [self.all_sprites],
            pygame.image.load(join('graphics', 'models', 'Player_BLUE.png')),
            self.collision_sprites,
            player=self.agent,
            brain_type="Tree"
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
            dt = 1/60.0
            
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
                if self.opponent.hitpoints <= 0: total_reward += 100 # Výhra
                if self.agent.hitpoints <= 0: total_reward -= 50 # Prohra
                break

        # 3. Vykreslení (jen pokud se díváme)
        if self.render_mode == "human":
            self.display_surface.fill('gray')
            self.all_sprites.draw(self.display_surface, (0,0), WINDOW_WIDTH, WINDOW_HEIGHT, 1)
            
            pygame.event.pump()
            
            pygame.display.update()
            self.clock.tick(10)

        # 4. Výstup
        obs = np.array(self.agent.get_context_rl(), dtype=np.float32)
        info = {}
        
        return obs, total_reward, terminated, truncated, info


    def _calculate_reward(self):
        reward = 0
        #reward -= 0.1
        
        dist = pygame.Vector2(self.agent.hitbox_rect.center).distance_to(pygame.Vector2(self.opponent.hitbox_rect.center))
        agent_state_name = self.agent.current_state_name
        opp_state_name = self.opponent.current_state_name

        agent_stamina_pct = (self.agent.stamina / self.agent.max_stamina) * 100
        
        # 1. LOGIKA VZDÁLENOSTI
        if dist > 80:
            if "RUN" in agent_state_name:
                reward += 0.5
            else:
                reward -= 1.0 
                if "ATTACK" in agent_state_name:
                    reward -= 2.0
        elif dist < 20:
            reward -= 0.2
        else:
            if "RUN" not in agent_state_name:
                reward += 0.05
            if "IDLE" in agent_state_name and agent_stamina_pct > 50:
                reward -= 0.2
            


        # 2. LOGIKA STAMINY
        if agent_stamina_pct < 20:
            reward -= 0.1 
        

        # 3. LOGIKA ÚTOKU 
        dmg_dealt = self.last_opp_hp - self.opponent.hitpoints
        if dmg_dealt > 0:
            reward += dmg_dealt * 2.0 + 5.0 # Úspěšný zásah
        else:
            if self.agent.attack_hitbox:
                if self.agent.hit_entities:
                    reward -= 0.2 # Útok do bloku
                else:
                    reward -= 1.0 # Máchání do vzduchu
        

        # 4. LOGIKA OBRANY 
        dmg_taken = self.last_agent_hp - self.agent.hitpoints
        
        # Trest za obdržené poškození
        if dmg_taken > 0:
            reward -= dmg_taken * 1.0 
        
        # Odměna za úspěšný blok/úhyb
        if self.opponent.attack_hitbox and dmg_taken == 0 and dist < 90:
            if "BLOCK" in agent_state_name or "DODGE" in agent_state_name:
                reward += 2.0
                if self.agent.is_parying:
                    reward += 5.0

        if "STUN" in agent_state_name: 
            reward -= 0.2
        
        if "STUN" in opp_state_name:
            reward += 0.5

        # Update uložených HP
        self.last_opp_hp = self.opponent.hitpoints
        self.last_agent_hp = self.agent.hitpoints
        
        return reward