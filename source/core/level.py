import pytmx
import pygame


from source.sprites.sprites import (
    GroundSprite,
    OnGroundSprite,
    WallSprite,
    PropSprite,
    InteractObjectSprite,
    CollisionSprite,
)
from source.core.settings import TILE_SIZE

from source.sprites.sprite_group import AllSprites

from source.utils.sprite_manager import SpriteManager
from source.utils.combat_manager import CombatManager
from source.utils.data_manager import DataManager


from source.entities.hostile_npc import HostileNPC
from source.entities.non_hostile_npc import NonHostileNPC


class Level:
    def __init__(self, tmx_file: str, map_name, quests, dialog_ui):
        self.map = pytmx.load_pygame(tmx_file)
        self.map_name = map_name
        self.map_mode = "basic"
        self.map_width = self.map.width
        self.map_height = self.map.height

        self.dialog_ui = dialog_ui
        self.combat_handler = CombatManager()

        self.all_sprites = AllSprites()
        self.interact_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.npc_spawn_positions = []
        self.player_spawn_positions = []

        self.quests = quests

        # add player to level
        self.player = None
        self.npc_1 = None
        self.npc_2 = None
        # load map layers into groups
        self.load_map()

    def check_interactions(self):
        if self.player.interacting:
            self.player.interacting = False
            for npc in self.enemy_sprites:
                if self.player.rect.colliderect(npc.rect) and not npc.hostile:
                    self.player.change_state(self.player.states["DIALOG"])
                    self.dialog_ui.start_dialogue(self.player, npc)
                    return {"type": "npc_interaction", "mode": None}

            for inter in self.interact_sprites:
                if self.player.rect.colliderect(inter.rect):
                    if "door" in inter.type:
                        door_name = inter.name
                        return {
                            "type": "level_change",
                            "mode": DataManager.get_door_route(
                                self.map_name, self.map_mode, door_name
                            ),
                        }
                    return {"type": "item_interaction", "mode": inter.type}

        return {"type": None, "mode": None}

    def load_map(self):
        for x, y, image in self.map.get_layer_by_name("Ground").tiles():
            GroundSprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in self.map.get_layer_by_name("OnGroundObjects"):
            OnGroundSprite((obj.x, obj.y), obj.image, self.all_sprites)
        for x, y, image in self.map.get_layer_by_name("Walls").tiles():
            WallSprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in self.map.get_layer_by_name("Objects"):
            PropSprite((obj.x, obj.y), obj.image, self.all_sprites)
        for obj in self.map.get_layer_by_name("InteractObjects"):
            InteractObjectSprite(
                (obj.x, obj.y),
                obj.image,
                (self.all_sprites, self.interact_sprites),
                obj.name,
                obj.type,
            )
        for obj in self.map.get_layer_by_name("Collisions"):
            CollisionSprite(
                (obj.x, obj.y),
                pygame.Surface((obj.width, obj.height)),
                self.collision_sprites,
            )
        for obj in self.map.get_layer_by_name("SpawnPoints"):
            if obj.type == "player_spawn":
                self.player_spawn_positions.append((obj.x, obj.y))
            if obj.type == "npc_spawn":
                self.npc_spawn_positions.append(((obj.x, obj.y), obj.name))

    def spawn_entities(self):
        mode = self.map_mode
        if mode == "spectate":
            spawn_pos_1, entity_spawn_1 = self.npc_spawn_positions[0]
            npc_data_1 = DataManager.get_map_npcs(self.map_name, mode).get(
                entity_spawn_1
            )
            self.npc_1 = HostileNPC(
                (spawn_pos_1[0], spawn_pos_1[1]),
                (self.all_sprites, self.enemy_sprites),
                SpriteManager.get_spritesheet(entity_spawn_1),
                self.collision_sprites,
                player=None,
                brain_type=npc_data_1["mode"],
            )

            spawn_pos_2, entity_spawn_2 = self.npc_spawn_positions[1]
            npc_data_2 = DataManager.get_map_npcs(self.map_name, mode).get(
                entity_spawn_2
            )
            self.npc_2 = HostileNPC(
                (spawn_pos_2[0], spawn_pos_2[1]),
                (self.all_sprites, self.enemy_sprites),
                SpriteManager.get_spritesheet(entity_spawn_2),
                self.collision_sprites,
                self.npc_1,
                brain_type=npc_data_2["mode"],
            )

            self.npc_1.player = self.npc_2
        else:
            for spawn_pos, entity_spawn in self.npc_spawn_positions:
                npc_data = DataManager.get_map_npcs(self.map_name, mode).get(
                    entity_spawn
                )
                if not npc_data:
                    continue
                
                if npc_data["type"] == "basic_hostile" and mode == "basic":
                    HostileNPC(
                        (spawn_pos[0], spawn_pos[1]),
                        (self.all_sprites, self.enemy_sprites),
                        SpriteManager.get_spritesheet("basic_npc"),
                        self.collision_sprites,
                        self.player,
                    )
                elif npc_data["type"] == "smart_hostile":
                    if mode == "tree":
                        HostileNPC(
                            (spawn_pos[0], spawn_pos[1]),
                            (self.all_sprites, self.enemy_sprites),
                            SpriteManager.get_spritesheet("tree"),
                            self.collision_sprites,
                            self.player,
                            brain_type="tree",
                        )
                    elif mode == "rl_mlp":
                        HostileNPC(
                            (spawn_pos[0], spawn_pos[1]),
                            (self.all_sprites, self.enemy_sprites),
                            SpriteManager.get_spritesheet("rl_mlp"),
                            self.collision_sprites,
                            self.player,
                            brain_type="rl_mlp",
                        )
                elif npc_data["type"] == "non_hostile":
                    non_hostile_npc_data = DataManager.get_npc_data(entity_spawn)
                    NonHostileNPC(
                        (spawn_pos[0], spawn_pos[1]),
                        (self.all_sprites, self.enemy_sprites),
                        SpriteManager.get_spritesheet(entity_spawn),
                        self.collision_sprites,
                        self.player,
                        non_hostile_npc_data,
                        self.quests,
                        brain_type=npc_data["mode"],
                    )

    def kill_entities(self):
        for enemy in self.enemy_sprites:
            enemy.kill()

    def update(self, dt):
        self.all_sprites.update(dt)
        if self.dialog_ui.active:
            if self.player.current_state_name in ["STUN", "DEATH"]:
                self.dialog_ui.close_dialogue()
            self.dialog_ui.update()

        if self.map_name == "arena_spectate":
            self.combat_handler.check_hits(self.npc_1, [self.npc_2])
        else:
            self.combat_handler.check_hits(self.player, self.enemy_sprites)

    def draw(self, surface, player_pos, debug_mode):
        self.all_sprites.draw(
            surface, player_pos, self.map_width, self.map_height, debug_mode
        )
        if self.dialog_ui.active:
            self.dialog_ui.draw(surface)
