import json
from os.path import join
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
from source.utils.combat_handler import CombatHandler
from source.dialogs.dialog import DialogUI
from source.entities.hostile_npc import HostileNPC
from source.entities.non_hostile_npc import NonHostileNPC

# from source.entities.player import Player


class Level:
    with open(join("data", "nonhostile_npcs.json"), "r", encoding="utf-8") as f:
        npc_database = json.load(f)

    with open(join("data", "map_data.json"), "r", encoding="utf-8") as f:
        map_database = json.load(f)

    def __init__(self, tmx_file: str, map_name, quests):
        self.map = pytmx.load_pygame(tmx_file)
        self.map_name = map_name
        self.map_width = self.map.width
        self.map_height = self.map.height

        self.dialog_ui = DialogUI()
        self.combat_handler = CombatHandler()

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
                    return {"type": "npc_interaction", "options": None}

            for inter in self.interact_sprites:
                if self.player.rect.colliderect(inter.rect):
                    if "door" in inter.type:
                        door_name = inter.name
                        return {
                            "type": "level_change",
                            "options": Level.map_database[self.map_name]["doors"][
                                door_name
                            ],
                        }
                    return {"type": "item_interaction", "options": inter.type}

        return {"type": None, "options": None}

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

    def spawn_entities(self, options):
        if options == "SPECTATE":
            spawn_pos_1, entity_spawn_1 = self.npc_spawn_positions[0]
            npc_data_1 = Level.map_database[self.map_name]["npcs"][entity_spawn_1]
            self.npc_1 = HostileNPC(
                (spawn_pos_1[0], spawn_pos_1[1]),
                (self.all_sprites, self.enemy_sprites),
                SpriteManager.get_spritesheet("enemy_model"),
                self.collision_sprites,
                player=None,
                brain_type=npc_data_1["options"],
            )

            spawn_pos_2, entity_spawn_2 = self.npc_spawn_positions[1]
            npc_data_2 = Level.map_database[self.map_name]["npcs"][entity_spawn_2]
            self.npc_2 = HostileNPC(
                (spawn_pos_2[0], spawn_pos_2[1]),
                (self.all_sprites, self.enemy_sprites),
                SpriteManager.get_spritesheet("enemy_model"),
                self.collision_sprites,
                self.npc_1,
                brain_type=npc_data_2["options"],
            )

            self.npc_1.player = self.npc_2

        else:
            for spawn_pos, entity_spawn in self.npc_spawn_positions:
                npc_data = Level.map_database[self.map_name]["npcs"][entity_spawn]
                if npc_data["type"] == "basic_hostile" and options == "BASIC":
                    HostileNPC(
                        (spawn_pos[0], spawn_pos[1]),
                        (self.all_sprites, self.enemy_sprites),
                        SpriteManager.get_spritesheet("enemy_model"),
                        self.collision_sprites,
                        self.player,
                    )
                elif npc_data["type"] == "smart_hostile":
                    if options == "TREE":
                        HostileNPC(
                            (spawn_pos[0], spawn_pos[1]),
                            (self.all_sprites, self.enemy_sprites),
                            SpriteManager.get_spritesheet("enemy_model"),
                            self.collision_sprites,
                            self.player,
                            brain_type="TREE",
                        )
                    elif options == "RL_MLP":
                        HostileNPC(
                            (spawn_pos[0], spawn_pos[1]),
                            (self.all_sprites, self.enemy_sprites),
                            SpriteManager.get_spritesheet("enemy_model"),
                            self.collision_sprites,
                            self.player,
                            brain_type="RL_MLP",
                        )
                elif npc_data["type"] == "non_hostile":
                    non_hostile_npc_data = Level.npc_database[entity_spawn]
                    NonHostileNPC(
                        (spawn_pos[0], spawn_pos[1]),
                        (self.all_sprites, self.enemy_sprites),
                        SpriteManager.get_spritesheet("enemy_model"),
                        self.collision_sprites,
                        self.player,
                        non_hostile_npc_data,
                        self.quests,
                        brain_type=npc_data["options"],
                    )

    def kill_entities(self):
        for enemy in self.enemy_sprites:
            enemy.kill()

    def update(self, dt):
        self.all_sprites.update(dt)
        if self.dialog_ui.active:
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
