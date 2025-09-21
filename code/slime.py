from settings import *
from i_enemy import I_Enemy

class Slime(I_Enemy):
    def __init__(self, pos, groups, collision_sprites, sprite_sheet, player):
        super().__init__(pos, groups, collision_sprites, player)
        self.sprite_sheet = sprite_sheet

        # Stats
        self.max_hitpoints = 50
        self.hitpoints = self.max_hitpoints
        self.damage = 20
        self.vision = 250
        self.score_value = 10
        self.heal_value = 10
        self.speed = 80

        # Animation
        self.animation_speed = 6
        self.animations = {
            'idle': { 'down' : self.load_frames(0, 4 , False), 'right' :  self.load_frames(0, 4, False), 'left' : self.load_frames(0, 4, True),'up' : self.load_frames(0, 4, False)},
            'walk': { 'down' : self.load_frames(1, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(1, 6, False)},
            'death' : { 'down' : self.load_frames(2, 5 , True), 'right' :  self.load_frames(2, 5, False), 'left' : self.load_frames(2, 5, True),'up' : self.load_frames(2, 5, False)}
        }
        self.animations['attack'] = self.animations['walk']
        self.image = self.animations[self.status][self.direction_state][self.frame_index]
        
