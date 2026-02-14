from i_entity import *
from joblib import load
from stable_baselines3 import PPO
import numpy as np

ACTION_MAP = {"IDLE": 0, "RUN": 1, "DODGE": 2, "BLOCK": 3, "LIGHT_ATTACK": 4, "HEAVY_ATTACK": 5, "STUN": 6}

class I_NPC(I_Entity):
    mlp_brain = PPO.load(join("data", "rl_models" ,"ppo_rpg_agent.zip"))
    tree_brain = load(join("data", "npc_brain_tree.joblib"))  

    def __init__(self, pos, groups, sprite_sheet, collisions, player, brain_type = "BASIC"):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN CREATION
        self.current_collisions = collisions

        self.hostile = False
        self.player = player
        self.current_target = pygame.Vector2()
        self.path_to_player = []
        self.brain_type = brain_type

        if brain_type == "TREE":
            self.brain = copy(I_NPC.tree_brain)
        elif brain_type == "RL_MLP":
            self.brain = copy(I_NPC.mlp_brain)
        else:
            self.brain = None

        self.fsm = FSM(self)
        # STATES AND ANIMATIONS
        self.states = {
            "IDLE"          : { "state" : Enemy_Idle()  ,   "stamina_cost" : 0.0    ,   "animation" :   { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)}},
            "RUN"           : { "state" : Enemy_Run()   ,   "stamina_cost" : 0.0    ,   "animation" :   { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)}},
            "DODGE"         : { "state" : Enemy_Dodge(1,4)    ,   "stamina_cost" : 3.0    ,   "animation" :   { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)}},
            "LIGHT_ATTACK"  : { "state" : Enemy_Light_Attack(2,3)     ,  "stamina_cost" : 3.0   , "animation" : { 'down' : self.load_frames(6, 5 , False), 'right' :  self.load_frames(7, 5, False), 'left' : self.load_frames(7, 5, True),'up' : self.load_frames(8, 5, False)}},
            "HEAVY_ATTACK"  : { "state" : Enemy_Heavy_Attack(3,4)     ,  "stamina_cost" : 5.0   , "animation" : { 'down' : self.load_frames(13, 6 , False), 'right' :  self.load_frames(14, 6, False), 'left' : self.load_frames(14, 6, True),'up' : self.load_frames(15, 6, False)}}, 
            "STUN"          : { "state" : Enemy_Stun()                ,  "stamina_cost" : 0.0   , "animation" : { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)}},
            "DEATH"         : { "state" : Enemy_Death()               ,  "stamina_cost" : 0.0   , "animation" : { 'down' : self.load_frames(9, 6 , True), 'right' :  self.load_frames(9, 6, False), 'left' : self.load_frames(9, 6, True),'up' : self.load_frames(9, 6, False)}},
            "BLOCK"         : { "state" : Enemy_Block(1,6)            ,  "stamina_cost" : 0.0   , "animation" : { 'down' : self.load_frames(10, 6 , True), 'right' :  self.load_frames(11, 6, False), 'left' : self.load_frames(11, 6, True),'up' : self.load_frames(12, 6, False)}}
        }
        
        #COOLDOWNS
        self.cooldowns= {     
            "reaction" : 0,
            "stun" : 0,
            "imunity" : 0
        }

        self.hitpoints = self.max_hitpoints = 200
        self.damage = 20
        self.speed = 100

        # AUDIO
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))],
            'block' : [pygame.mixer.Sound(join('assets', 'block_1.wav')),pygame.mixer.Sound(join('assets', 'block_2.wav')),pygame.mixer.Sound(join('assets', 'block_3.wav'))],
            'parry' : [pygame.mixer.Sound(join('assets', 'parry.wav')), pygame.mixer.Sound(join('assets', 'parry_1.wav')),pygame.mixer.Sound(join('assets', 'parry_2.wav')),pygame.mixer.Sound(join('assets', 'parry_3.wav'))],
            'dodge' : [pygame.mixer.Sound(join('assets', 'dodge.wav'))],
            'break' : [pygame.mixer.Sound(join('assets', 'break.wav'))]
        }

        self.change_state(self.states["IDLE"])


    def face_player(self):
        if not self.player: return
        vec_to_player = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        
        if vec_to_player.length_squared() > 0:
            self.direction = vec_to_player.normalize()
            self.update_direction()
        else:
            self.direction = pygame.Vector2()


    def get_context_rl(self):
        #dist	npc_hp_status	npc_stamina_status	npc_current_action	player_hp_status	player_stamina_status	player_action	new_action

        # 1. distance
        data = []
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(self.player.rect.center))
        data.append(min(dist + rand.randint(-10 , 10) / 400.0, 1.0))
        
        # 2. npc hp 0-1
        data.append(self.hitpoints / self.max_hitpoints)

        # 3. npc stamina 0-1
        data.append(self.stamina / self.max_stamina)

        # 4. NPC current action
        idx = self._get_action_index(self)
        my_action_one_hot = np.eye(7)[idx]
        data.extend(my_action_one_hot)

        # 5. player hp
        data.append(self.player.hitpoints / self.player.max_hitpoints)

        # 6. player stamina
        data.append(self.player.stamina / self.player.max_stamina)

        # 7. player current action
        idx_p = self._get_action_index(self.player)
        opp_action_one_hot = np.eye(7)[idx_p]
        data.extend(opp_action_one_hot)

        #print(data)
        return data


    def _get_action_index(self, entity):
        idx = ACTION_MAP.get(entity.current_state_name, 0)
        if idx >= 7: idx = 0 
        
        return idx


    def get_context(self):
        #dist	npc_hp_status	npc_stamina_status	npc_current_action	player_hp_status	player_stamina_status	player_action	new_action
        #ACTION_MAP = {"IDLE": 0, "RUN": 1, "DODGE": 2, "BLOCK": 3, "LIGHT_ATTACK": 4, "HEAVY_ATTACK": 5, "STUN": 6}
        # Mapování stavů HP {"CRITICAL": 0, "HURT": 1, "OK": 2}
        # Mapování stavů Staminy {"TIRED": 0, "OK": 1}

        # 1. distance
        data = []
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(self.player.rect.center))
        data.append(int(dist) + rand.randint(-10 , 10))
        #print(dist)

        # 2. NPC hp
        hp_per = self.hitpoints / self.max_hitpoints * 100
        if hp_per < 20:
            data.append(0)
        elif hp_per < 50:
            data.append(1)
        else:
            data.append(2)

        # 3. NPC stamina
        stam_per = self.stamina / self.max_stamina * 100
        if stam_per < 30:
            data.append(0)
        else:
            data.append(1)

        # 4. NPC current action
        data.append(ACTION_MAP.get(self.current_state_name, 0))

        # 5. player hp
        hp_pl_per = self.player.hitpoints / self.player.max_hitpoints * 100
        if hp_pl_per < 20:
            data.append(0)
        elif hp_pl_per < 50:
            data.append(1)
        else:
            data.append(2)

        # 6. player stamina
        stam_pl_per = self.player.stamina / self.player.max_stamina * 100
        if stam_pl_per < 30:
            data.append(0)
        else:
            data.append(1)

        # 7. player current action
        data.append(ACTION_MAP.get(self.player.current_state_name, 0))

        return data


    def get_path(self):
        self.path_to_player = self.g_map.get_path(self.rect.center , self.player.rect.center)
        #self.g_map.show_path(self.path_to_player)
        #self.g_map.show_map()
    

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()
        

    def decide_action(self):
        if not self.hostile:
            return "IDLE"
        
        self.cooldowns["reaction"] = rand.triangular(0.2, 0.25, 0.22)
        distance_to_player = pygame.Vector2(self.hitbox_rect.center).distance_to(pygame.Vector2(self.player.hitbox_rect.center))

        if self.player.current_state_name != "DEATH" and distance_to_player <= 400:
            if self.brain_type == "RL_MLP":
                ctx = self.get_context_rl()
                prediction = self.brain.predict([ctx])[0][0]
            elif self.brain_type == "TREE":
                ctx = self.get_context()
                prediction = self.brain.predict([ctx])[0]
            else:
                ctx = self.get_context()
                if ctx[0] > 60:
                    prediction = "RUN"
                else:
                    if ctx[2] == 1:
                        prediction = "LIGHT_ATTACK"
                    else:
                        prediction = "IDLE"
            return prediction
        else:
            return "IDLE"
        
            

