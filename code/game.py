from level import *
from i_entity import I_Entity

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game")


        self.debug_mode = False
        self.game_speed = 1

        self.player = Player((0,0), {} ,pygame.image.load(join('graphics', 'models', 'Player.png')).convert_alpha())
        

        # load maps
        self.levels = {
            "tutorial": Level("maps/tutorial_map.tmx", self.player),
            "crossroad": Level("maps/crossroad_map.tmx", self.player),
            "arena": Level("maps/arena_map.tmx", self.player)
        }
        self.current_level = self.levels["tutorial"]
        self.switch_level("tutorial", self.current_level.player_spawn_positions[0])


    def switch_level(self, name, spawn_pos, options = None):
        self.current_level.kill_entities()

        if self.current_level.all_sprites.has(self.player):
            self.current_level.all_sprites.remove(self.player)
        self.current_level = self.levels[name]

        # updating player for new level
        self.player.rect.center = spawn_pos
        self.player.hitbox_rect.center = spawn_pos
        self.current_level.all_sprites.add(self.player) 
        self.player.current_collisions = self.current_level.collision_sprites
        if self.current_level.player_spawn_positions:
            self.player.respawn_point["level"] = name
            self.player.respawn_point["pos"] = self.current_level.player_spawn_positions[0]
        
        # map construction for path finding 
        I_Entity.g_map.construct(self.current_level.map)
        self.current_level.spawn_entities(options)
        
        

    def display_ui(self, clock):
        font = pygame.font.Font(None, 25)
        fps = font.render(f"FPS: {int(clock.get_fps())}", True, 'white')
        self.display_surface.blit(fps, (20, 20))

        debug = font.render(f"debug: {self.debug_mode}", True, 'white')
        self.display_surface.blit(debug, (20, 40))


    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.debug_mode = not self.debug_mode
    
            if not self.player.is_alive:
                self.switch_level(self.player.respawn_point["level"], self.player.respawn_point["pos"])
                self.player.respawn()

            # Playing
            result = self.current_level.check_interactions()
            if result:
                self.switch_level(result["target"], result["spawn"], result["options"])
            #deltaTime
            dt = clock.tick(60) / 1000
            #update logic
            self.current_level.update(dt * self.game_speed)
            #draw
            self.display_surface.fill('black')
            self.current_level.draw(self.display_surface, self.player.rect.center, self.debug_mode)
            
            self.display_ui(clock)
            pygame.display.flip()

        # Exit
        pygame.quit()