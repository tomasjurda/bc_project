from i_entity import *
from FSM import FSM

class Player(I_Entity):
    def __init__(self, pos, groups ,sprite_sheet):
        super().__init__(pos, groups, sprite_sheet)

        # SETTING THIS IN SWITCH_LEVEL
        self.current_collisions = pygame.sprite.Group()

        #STATS
        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.damage = 20
        self.speed = 150

        #CONTROL
        self.fsm = FSM(self)
        self.states = {
            "idle" : Player_Idle(),
            "run" : Player_Run(),
            "dodge": Dodge(),
            "l_attack": Light_Attack(2 , 3),
            "h_attack" : Player_Heavy_Attack(3 , 4),
            "hurt" : Hurt(),
            "death" : Player_Death(),
            "block" : Player_Block()
        }

        #CDS + ACTIONS
        
        self.cooldowns={    #"attack" : 0,
                            #"dodge" : 0,
                            #"respawn": 0,
                            #"stun" : 0   
                            }
        
        
        
        self.attack_hitbox = None
        self.interacting = False

        # AUDIO
        self.sound_effects = {
            'hit' : [pygame.mixer.Sound(join('assets', 'sword_hit_1.wav')), pygame.mixer.Sound(join('assets', 'sword_hit_2.wav')),pygame.mixer.Sound(join('assets', 'sword_hit_3.wav'))],
            'miss' : [pygame.mixer.Sound(join('assets', 'sword_miss_1.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_2.wav')),pygame.mixer.Sound(join('assets', 'sword_miss_3.wav'))],
            'damage' : [pygame.mixer.Sound(join('assets', 'human_damage_1.wav')),pygame.mixer.Sound(join('assets', 'human_damage_2.wav')),pygame.mixer.Sound(join('assets', 'human_damage_3.wav'))]
        }

        # ANIMATION
        self.animations = {
            'Player_Idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Player_Run': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Dodge': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'Light_Attack': { 'down' : self.load_frames(6, 5 , False), 'right' :  self.load_frames(7, 5, False), 'left' : self.load_frames(7, 5, True),'up' : self.load_frames(8, 5, False)},
            'Player_Heavy_Attack': { 'down' : self.load_frames(13, 6 , False), 'right' :  self.load_frames(14, 6, False), 'left' : self.load_frames(14, 6, True),'up' : self.load_frames(15, 6, False)},
            'Hurt': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'Player_Death' : { 'down' : self.load_frames(9, 6 , True), 'right' :  self.load_frames(9, 6, False), 'left' : self.load_frames(9, 6, True),'up' : self.load_frames(9, 6, False)},
            'Player_Block' : {'down' : self.load_frames(10, 6 , True), 'right' :  self.load_frames(11, 6, False), 'left' : self.load_frames(11, 6, True),'up' : self.load_frames(12, 6, False)}
        }
        self.fsm.change_state(self.states["idle"])


    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()

