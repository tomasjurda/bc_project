from i_entity import *
from joblib import load


class I_Enemy(I_Entity):
    def __init__(self, pos, groups, sprite_sheet, collisions, player):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN CREATION
        self.current_collisions = collisions

        self.player = player
        self.current_target = pygame.Vector2()
        self.path_to_player = []

        model_path = join('data', 'npc_brain_tree.joblib')
        self.brain = load(model_path)

        self.fsm = FSM(self)
        self.states = {
            "idle" : Enemy_Idle(),
            "run" : Enemy_Run(),
            "dodge": Dodge(1 , 4),
            "l_attack": Light_Attack( 2 , 3),
            "h_attack" : Enemy_Heavy_Attack( 3 , 4),
            "hurt" : Hurt(),
            "death" : Enemy_Death(),
            "block" : Enemy_Block(1 , 6)
        }
        
        #CDS + ACTIONS
        self.cooldowns= {     
                            "reaction" : 0 # decision timer
                        }

        self.hitpoints = self.max_hitpoints = 200
        self.damage = 20
        self.speed = 100

        
        # AUDIO
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))]
        }

        # ANIMATION
        self.animations = {
            'Enemy_Idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Enemy_Run': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Dodge': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Light_Attack': { 'down' : self.load_frames(6, 5 , False), 'right' :  self.load_frames(7, 5, False), 'left' : self.load_frames(7, 5, True),'up' : self.load_frames(8, 5, False)},
            'Enemy_Heavy_Attack': { 'down' : self.load_frames(13, 6 , False), 'right' :  self.load_frames(14, 6, False), 'left' : self.load_frames(14, 6, True),'up' : self.load_frames(15, 6, False)},
            'Hurt': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Enemy_Death' : { 'down' : self.load_frames(9, 6 , True), 'right' :  self.load_frames(9, 6, False), 'left' : self.load_frames(9, 6, True),'up' : self.load_frames(9, 6, False)},
            'Enemy_Block' : {'down' : self.load_frames(10, 6 , True), 'right' :  self.load_frames(11, 6, False), 'left' : self.load_frames(11, 6, True),'up' : self.load_frames(12, 6, False)}
        }
        self.fsm.change_state(self.states["idle"])


    def face_player(self):
        if not self.player: return
        vec_to_player = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        
        if vec_to_player.length_squared() > 0:
            self.direction = vec_to_player.normalize()
            self.update_direction()
        else:
            self.direction = pygame.Vector2()


    def get_context(self):
        #dist	npc_hp_status	npc_stamina_status	npc_current_action	player_hp_status	player_stamina_status	player_action	new_action
        ACTION_MAP = {"IDLE": 0, "RUN": 1, "DODGE": 2, "BLOCK": 3, "LIGHT_ATTACK": 4, "HEAVY_ATTACK": 5, "FEINT": 6, "HURT": 7}
        # Mapování stavů HP
        #HP_MAP = {"CRITICAL": 0, "HURT": 1, "OK": 2}
        # Mapování stavů Staminy
        #STAMINA_MAP = {"TIRED": 0, "OK": 1}

        # 1. distance
        data = []
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(self.player.rect.center))
        data.append(int(dist))
        

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
        npc_state_name = self.fsm.current_state.__class__.__name__
        npc_clean_name = npc_state_name.replace("Player_", "").replace("Enemy_", "").upper()
        data.append(ACTION_MAP.get(npc_clean_name, 0))

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
        player_state_name = self.player.fsm.current_state.__class__.__name__
        player_clean_name = player_state_name.replace("Player_", "").replace("Enemy_", "").upper()
        data.append(ACTION_MAP.get(player_clean_name, 0))
        
        #print(data)

        return data


    def get_path(self):
        self.path_to_player = self.g_map.get_path(self.rect.center , self.player.rect.center)
        #self.g_map.show_path(self.path_to_player)
        #self.g_map.show_map()
    

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " player_pos: ", (round(self.player.rect.centerx), round(self.player.rect.centery)) ," target: ", self.current_target , " path: ", self.path_to_player)
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " state: ", self.fsm.current_state.__class__.__name__ ," target: ", self.current_target , " path: ", self.path_to_player)
        self.animate()
        

    def decide_action(self):
        self.cooldowns["reaction"] = 0.2
        ctx = self.get_context()
        prediction = self.brain.predict([ctx])[0]

        #print(prediction)
        return prediction

            

