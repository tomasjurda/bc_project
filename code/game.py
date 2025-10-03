from settings import *
#from player import Player
#from slime import Slime
#from skeleton import Skeleton
from level import *
#from sprites import *
#from pytmx.util_pygame import load_pygame
#from groups import *

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game")
        
        #self.setup_game()
        self.state = 'playing'
        self.player = Player((0,0), {} ,pygame.image.load(join('graphics', 'models', 'player.png')).convert_alpha())

        # load maps without player
        self.levels = {
            "tutorial": Level("maps/tutorial_map.tmx", self.player),
            "crossroad": Level("maps/crossroad_map.tmx", self.player)
        }
        self.current_level = self.levels["tutorial"]
        self.switch_level("tutorial", self.current_level.player_spawn_positions[0])
        
        #self.current_level.all_sprites.add(self.player)

    def switch_level(self, name, spawn_pos):
        if self.current_level.all_sprites.has(self.player):
            self.current_level.all_sprites.remove(self.player)
        self.current_level = self.levels[name]
        self.player.rect.center = spawn_pos
        self.player.hitbox_rect.center = spawn_pos
        self.current_level.all_sprites.add(self.player)  # re-add to new sprite group
        self.player.current_collisions = self.current_level.collision_sprites
        #print(len(self.player.current_collisons))
        #print(len(self.current_level.collision_sprites))
        
    """
    def reset_game(self):
        # Kill all enemies
        for enemy in self.enemy_sprites.sprites():
            enemy.kill()
        # Respawn player
        self.player.respawn(self.player_spawn_positions[0])
    """  
    def display_fps(self, clock):
        font = pygame.font.Font(None, 25)
        fps = font.render(f"FPS: {int(clock.get_fps())}", True, 'white')
        self.display_surface.blit(fps, (20, 20))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Menu
            """
            if self.state == 'death': 
                self.state = 'playing'
                self.reset_game()
            """
            # Playing
            result = self.current_level.check_interactions()
            if result:
                self.switch_level(result["target"], result["spawn"])
            #deltaTime
            dt = clock.tick(60) / 1000
            #update logic
            #self.all_sprites.update(dt)
            self.current_level.update(dt)
            #draw
            self.display_surface.fill('black')
            #self.all_sprites.draw(self.display_surface, self.player.rect.center, self.map_width, self.map_height)
            self.current_level.draw(self.display_surface, self.player.rect.center)
            self.display_fps(clock)
            pygame.display.flip()

        # Exit
        pygame.quit()