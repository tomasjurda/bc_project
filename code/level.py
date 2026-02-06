from player import Player
from i_enemy import I_Enemy
from sprites import *
from sprite_group import *
from combat_handler import CombatHandler, SoundManager


class Level:
    def __init__(self, tmx_file : str, player : Player, sound_manager : SoundManager):
        self.map = pytmx.load_pygame(tmx_file)
        self.map_width = self.map.width
        self.map_height = self.map.height
        #self.sound_manager = sound_manager
        self.combat_handler = CombatHandler(sound_manager)

        self.all_sprites = AllSprites()
        self.interact_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.enemy_spawn_positions = []
        self.player_spawn_positions = []
        
        # add player to level
        self.player = player
        # load map layers into groups
        self.load_map()
    

    def check_interactions(self):
        if self.player.interacting:
            for inter in self.interact_sprites:
                if self.player.rect.colliderect(inter.rect):
                    if inter.type == "door" or inter.type == "invisible_door":
                        split = inter.name.split()
                        location = split[0]
                        spawn = list(map(int, [split[1], split[2]]))
                        return {"target": location,
                                "spawn": spawn  }
                    else:
                        print(inter.type)
                
            self.player.interacting = False
        return None
    

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
            InteractObjectSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.interact_sprites), obj.name , obj.type)
        for obj in self.map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in self.map.get_layer_by_name('SpawnPoints'):
            if obj.name == 'Player':
                self.player_spawn_positions.append((obj.x, obj.y))
            if obj.name == 'Enemy':
                I_Enemy((obj.x, obj.y), (self.all_sprites, self.enemy_sprites), pygame.image.load(join('graphics', 'models', 'Player.png')).convert_alpha(), self.collision_sprites, self.player)
        

    def update(self, dt):
        self.all_sprites.update(dt)
        self.combat_handler.check_hits(self.player, self.enemy_sprites)


    def draw(self, surface, player_pos, debug_mode):
        self.all_sprites.draw(surface, player_pos, self.map_width, self.map_height, debug_mode)