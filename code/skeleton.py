from settings import *
from i_enemy import I_Enemy

class Skeleton(I_Enemy):
    def __init__(self, pos, groups, collision_sprites, sprite_sheet, player):
        super().__init__(pos, groups, collision_sprites, player)
        self.sprite_sheet = sprite_sheet

        # STATS
        self.max_hitpoints = 80
        self.hitpoints = self.max_hitpoints
        self.damage = 15
        self.vision = 300
        self.score_value = 20
        self.heal_value = 20
        self.speed = 100

        # Animation
        self.animation_speed = 6
        self.animations = {
            'idle': { 'down' : self.load_frames(0, 6 , False), 'right' :  self.load_frames(1, 6, False), 'left' : self.load_frames(1, 6, True),'up' : self.load_frames(2, 6, False)},
            'walk': { 'down' : self.load_frames(3, 6 , False), 'right' :  self.load_frames(4, 6, False), 'left' : self.load_frames(4, 6, True),'up' : self.load_frames(5, 6, False)},
            'attack': { 'down' : self.load_frames(7, 4 , False), 'right' :  self.load_frames(8, 4, False), 'left' : self.load_frames(8, 4, True),'up' : self.load_frames(9, 4, False)},
            'death' : { 'down' : self.load_frames(6, 4 , True), 'right' :  self.load_frames(6, 4, False), 'left' : self.load_frames(6, 4, True),'up' : self.load_frames(6, 4, False)}
        }
        self.image = self.animations[self.status][self.direction_state][self.frame_index]