import pygame

from source.utils.sprite_manager import SpriteManager
from source.utils.data_manager import DataManager
from source.utils.sound_manager import SoundManager
from source.utils.quest_manager import QuestManager

from source.core.level import Level

from source.entities.entity import Entity
from source.entities.player import Player

from source.dialogs.dialog import DialogUI
from source.core.settings import WINDOW_HEIGHT, WINDOW_WIDTH


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game")

        self.debug_mode = False
        self.game_speed = 1

        # LOAD DATA
        SpriteManager.load_sprites()
        DataManager.load_map_and_npc_data()
        DataManager.preload_ai_models()

        SoundManager.init(enable_audio=True)
        SoundManager.load_all_sounds()
        SoundManager.set_master_volume(0.4)

        self.quest_manager = QuestManager()
        self.player = Player(
            (0, 0),
            {},
            SpriteManager.get_spritesheet("player"),
        )

        self.level_configs = {
            "tutorial": "maps/tutorial_map.tmx",
            "crossroad": "maps/crossroad_map.tmx",
            "arena": "maps/arena_map.tmx",
            "arena_spectate": "maps/map_arena_spectate.tmx",
            "city": "maps/city_map.tmx",
        }

        self.level_cache = {}
        self.MAX_CACHE_SIZE = 3

        self.dialog_ui = DialogUI()
        self.current_level = None
        self.switch_level("tutorial")

    def switch_level(self, name, spawn_pos=None, mode=None):
        if self.current_level:
            # killing entities and removing player in last level
            self.current_level.kill_entities()
            if self.current_level.all_sprites.has(self.player):
                self.current_level.all_sprites.remove(self.player)

        if name in self.level_cache:
            # new level already in cache => load from cache
            self.current_level = self.level_cache[name]
            self.level_cache[name] = self.level_cache.pop(name)

        else:
            # new level object needs to be created and added to cache
            tmx_file = self.level_configs[name]
            new_level = Level(tmx_file, name, self.quest_manager, self.dialog_ui)

            if len(self.level_cache) >= self.MAX_CACHE_SIZE:
                oldest_level_name = next(iter(self.level_cache))
                oldest_level = self.level_cache.pop(oldest_level_name)
                del oldest_level

            self.level_cache[name] = new_level
            self.current_level = new_level

        self.current_level.player = self.player

        # updating player for new level
        if spawn_pos is None:
            spawn_pos = self.current_level.player_spawn_positions[0]

        self.player.rect.center = spawn_pos
        self.player.hitbox_rect.center = spawn_pos
        self.current_level.all_sprites.add(self.player)
        self.player.current_collisions = self.current_level.collision_sprites
        if self.current_level.player_spawn_positions:
            self.player.respawn_point["level"] = name
            self.player.respawn_point["pos"] = (
                self.current_level.player_spawn_positions[0]
            )

        # map construction for path finding
        Entity.g_map.construct(self.current_level.map)
        if mode:
            self.current_level.map_mode = mode
        self.current_level.spawn_entities()

    def display_ui(self, clock):
        font = pygame.font.Font(None, 25)
        fps = font.render(f"FPS: {int(clock.get_fps())}", True, "white")
        self.display_surface.blit(fps, (20, 20))

        debug = font.render(f"debug: {self.debug_mode}", True, "white")
        self.display_surface.blit(debug, (20, 40))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # POSÍLÁNÍ EVENTŮ DO DIALOGU
                if self.dialog_ui.active:
                    self.dialog_ui.handle_event(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.debug_mode = not self.debug_mode

            if not self.player.is_alive:
                self.switch_level(
                    self.player.respawn_point["level"], self.player.respawn_point["pos"]
                )
                self.player.respawn()

            # Playing
            result = self.current_level.check_interactions()
            if result["type"] == "level_change":
                level_mode = result["mode"]
                self.switch_level(
                    level_mode["target_level"],
                    level_mode["spawn_pos"],
                    level_mode["mode"],
                )
            # deltaTime
            raw_dt = clock.tick(60) / 1000
            dt = min(raw_dt, 0.1)

            # update logic
            self.current_level.update(dt * self.game_speed)
            # draw
            self.display_surface.fill("black")
            self.current_level.draw(
                self.display_surface, self.player.rect.center, self.debug_mode
            )

            self.display_ui(clock)
            pygame.display.flip()

        # Exit
        pygame.quit()
