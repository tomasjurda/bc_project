from player import Player
from hostile_npc import HostileNPC
from non_hostile_npc import NonHostileNPC
from sprites import *
from sprite_group import *
from combat_handler import CombatHandler


class Level:
    def __init__(self, tmx_file : str):
        self.map = pytmx.load_pygame(tmx_file)
        self.map_width = self.map.width
        self.map_height = self.map.height

        self.combat_handler = CombatHandler()

        self.all_sprites = AllSprites()
        self.interact_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.npc_spawn_positions = []
        self.player_spawn_positions = []
        
        # add player to level
        self.player = None
        # load map layers into groups
        self.load_map()
    

    def check_interactions(self):
        if self.player.interacting:
            self.player.interacting = False
            for npc in self.enemy_sprites:
                if self.player.rect.colliderect(npc.rect) and not npc.hostile:
                    print("dialog")
                    #self.player.change_state(self.player.states["DIALOG"])
                    return None


            for inter in self.interact_sprites:
                if self.player.rect.colliderect(inter.rect):
                    if inter.type == "door" or inter.type == "invisible_door":
                        split = inter.name.split("-")
                        location = split[0]
                        pos_split = split[1].split()
                        spawn = list(map(int, [pos_split[0], pos_split[1]]))
                        if len(split) < 3:
                            options = None
                        else:
                            options = split[2]

                        return {"target": location,
                                "spawn": spawn,
                                "options" : options  }
                    else:
                        print(inter.type)
                        return None
                        
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
            if obj.name == 'NPC':
                self.npc_spawn_positions.append(((obj.x, obj.y), obj.type))


    def spawn_entities(self, options):
        for spawn, type in self.npc_spawn_positions:
            if type == "smart_hostile":
                if options == "TREE":
                    HostileNPC((spawn[0], spawn[1]), (self.all_sprites, self.enemy_sprites), pygame.image.load(join('graphics', 'models', 'Player_BLUE.png')).convert_alpha(), self.collision_sprites, self.player, brain_type="TREE")
                elif options == "RL_MLP":
                    HostileNPC((spawn[0], spawn[1]), (self.all_sprites, self.enemy_sprites), pygame.image.load(join('graphics', 'models', 'Player_BLUE.png')).convert_alpha(), self.collision_sprites, self.player, brain_type="RL_MLP" )
            elif type == "basic_hostile" and options == "BASIC":
                HostileNPC((spawn[0], spawn[1]), (self.all_sprites, self.enemy_sprites), pygame.image.load(join('graphics', 'models', 'Player_BLUE.png')).convert_alpha(), self.collision_sprites, self.player )
            elif type == "non_hostile":
                NonHostileNPC((spawn[0], spawn[1]), (self.all_sprites, self.enemy_sprites), pygame.image.load(join('graphics', 'models', 'Player_BLUE.png')).convert_alpha(), self.collision_sprites, self.player )


    def kill_entities(self):
        for enemy in self.enemy_sprites:
            enemy.kill()


    def update(self, dt):
        self.all_sprites.update(dt)
        self.combat_handler.check_hits(self.player, self.enemy_sprites)


    def draw(self, surface, player_pos, debug_mode):
        self.all_sprites.draw(surface, player_pos, self.map_width, self.map_height, debug_mode)