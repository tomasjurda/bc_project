from FSM import FSM
from i_entity import I_Entity
from enemy_states import *
"""
NPCs that are immediatly hostile
"""
class I_Enemy(I_Entity):
    def __init__(self, pos, groups, sprite_sheet, collisions, player):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN CREATION
        self.current_collisions = collisions

        self.player = player
        self.last_player_location = pygame.Vector2()
        self.current_target = pygame.Vector2()
        self.path_to_player = []

        self.fsm = FSM(self)
        self.states = {
            "idle" : Enemy_Idle(),
            "run" : Enemy_Run(),
            "dodge": Dodge(),
            "l_attack": Light_Attack(),
            "h_attack" : Heavy_Attack(),
            "hurt" : Hurt(),
            "death" : Enemy_Death(),
            "block" : Enemy_Block()
        }
        self.fsm.change_state(self.states["idle"])
        
        #CDS + ACTIONS
        self.cooldowns={    "attack" : 0,
                            "dodge" : 0,
                            "respawn": 0,
                            "stun" : 0,
                            "reaction" : 0   }
        
        self.attack_hitbox = None

        self.max_hitpoints = 100
        self.hitpoints = self.max_hitpoints
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
            'Hurt': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Enemy_Death' : { 'down' : self.load_frames(9, 6 , True), 'right' :  self.load_frames(9, 6, False), 'left' : self.load_frames(9, 6, True),'up' : self.load_frames(9, 6, False)},
            'Enemy_Block' : {'down' : self.load_frames(10, 6 , True), 'right' :  self.load_frames(11, 6, False), 'left' : self.load_frames(11, 6, True),'up' : self.load_frames(12, 6, False)}
        }
        self.image = self.animations[self.fsm.current_state.__class__.__name__][self.direction_state][self.frame_index]

    
    def take_hit(self, attack_type , damage, knockback):
        current_state = self.fsm.current_state.__class__.__name__
        if current_state == 'Dodge':
            return
        elif current_state == 'Enemy_Block' and attack_type == 1: #1 == light
            return
        
        self.hitpoints -= damage
        if self.hitpoints <= 0:
            self.fsm.change_state(self.states["death"])
        else:
            self.direction = knockback
            self.fsm.change_state(self.states["hurt"])

    def get_path(self):
        self.path_to_player = self.g_map.get_path(self.rect.center , self.last_player_location)
        self.g_map.show_path(self.path_to_player)
        #self.g_map.show_map()
    
    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " player_pos: ", (round(self.player.rect.centerx), round(self.player.rect.centery)) ," target: ", self.current_target , " path: ", self.path_to_player)
        #print(" enemy_pos: ", (round(self.rect.centerx), round(self.rect.centery)) , " state: ", self.fsm.current_state.__class__.__name__ ," target: ", self.current_target , " path: ", self.path_to_player)
        self.animate()
        
        

            

