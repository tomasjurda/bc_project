from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import *


class Level:
    def __init__(self, tmx_file, player):
        self.map = load_pygame(tmx_file)
        self.map_width = self.map.width
        self.map_height = self.map.height

        self.all_sprites = AllSprites()
        self.interact_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.enemy_spawn_positions = []
        self.player_spawn_positions = []

        # load map layers into groups
        self.load_map()

        # add player to level
        self.player = player
        self.all_sprites.add(player)
    
    def load_map(self):
        for x,y,image in self.map.get_layer_by_name('Ground').tiles():
            GroundSprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)
        for obj in self.map.get_layer_by_name('OnGroundObjects'):
            OnGroundSprite((obj.x, obj.y), obj.image, self.all_sprites)
        for x,y,image in self.map.get_layer_by_name('Walls').tiles():
            WallSprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)
        for obj in self.map.get_layer_by_name('Objects'):
            PropSprite((obj.x, obj.y), obj.image, self.all_sprites)
        for obj in self.map.get_layer_by_name('InteractObjects'):
            InteractObjectSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.interact_sprites), obj.name)
        for obj in self.map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in self.map.get_layer_by_name('SpawnPoints'):
            if obj.name == 'Player':
                self.player_spawn_positions.append((obj.x, obj.y))
        
    def update(self, dt):
        self.all_sprites.update(dt, self.collision_sprites)

    def draw(self, surface, player_pos):
        self.all_sprites.draw(surface, player_pos, self.map_width, self.map_height)