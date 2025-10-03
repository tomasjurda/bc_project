from i_entity import I_Entity
from FSM import FSM
from player_states import *

class Player(I_Entity):
    def __init__(self, pos, groups ,sprite_sheet):
        super().__init__(pos, groups, sprite_sheet)

        self.current_collisions = pygame.sprite.Group()
        #STATS
        self.max_hitpoints = 100
        self.hitpoints = self.max_hitpoints
        self.damage = 20
        self.speed = 150

        #CONTROL
        self.fsm = FSM(self)
        self.fsm.change_state(Player_Idle())
        
        #CDS + ACTIONS
        self.cooldowns = {"attack" : 0,
                          "dodge" : 0}
        self.attack_hitbox = None
        self.interacting = False

        # AUDIO
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))]
        }

        # ANIMATION
        self.animation_speed = 10
        self.animations = {
            'Player_Idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Player_Run': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Player_Dodge': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Player_Attack': { 'down' : self.load_frames(6, 4 , False), 'right' :  self.load_frames(7, 4, False), 'left' : self.load_frames(7, 4, True),'up' : self.load_frames(8, 4, False)},
            'death' : { 'down' : self.load_frames(9, 4 , True), 'right' :  self.load_frames(9, 4, False), 'left' : self.load_frames(9, 4, True),'up' : self.load_frames(9, 4, False)}
        }
        self.image = self.animations[self.fsm.current_state.__class__.__name__][self.direction_state][self.frame_index]
             
    def set_animation(self):
        self.time_accumulator = 0
        self.frame_index = 0
         
    def animate(self):
        #print(self.fsm.current_state.__class__.__name__)
        frames = self.animations[self.fsm.current_state.__class__.__name__][self.direction_state]
        self.time_accumulator += self.dt
        if self.time_accumulator >= 1 / self.animation_speed:
            self.time_accumulator = 0
            self.frame_index += 1
            self.frame_index %= len(frames)

            self.image = frames[self.frame_index]

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()
    
    def update_cooldowns(self, dt):
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= dt
        if self.stamina < 10.0:
            self.stamina += dt * 2
