"""
Module containing the CombatManager class responsible for handling
hit detection, blocking, parrying, and damage resolution between entities.
"""

import random
import pygame
from source.entities.entity import Entity


class CombatManager:
    """
    Manages combat interactions such as hit detection, blocking angles,
    and applying knockback/damage between the player and enemies.
    """

    @classmethod
    def check_hits(
        cls, player: Entity, enemy_sprites: pygame.sprite.Group | list[Entity]
    ) -> None:
        """
        Checks for active attack hitboxes intersecting with hurtboxes for both
        the player/npc with hostile group for that specific entity

        Args:
            player (Entity): Entity (usually the Player)
            enemy_sprites (pygame.sprite.Group | list[Entity]): A group or list of enemy entities for the "player" entity
        """

        # Player attack
        if player.attack_hitbox:
            attack_type = 1
            if "HEAVY_ATTACK" in player.current_state_name:
                attack_type = 2
            for enemy in enemy_sprites:
                if not player.attack_hitbox:
                    break
                if (
                    "DEATH" in enemy.current_state_name
                    or enemy.cooldowns["imunity"] > 0
                ):
                    continue
                if (
                    player.attack_hitbox.colliderect(enemy.hitbox_rect)
                    and enemy not in player.hit_entities
                ):
                    player.hit_entities.append(enemy)
                    cls.resolve_hit(player, enemy, attack_type)

        # Enemy attacks
        for enemy in enemy_sprites:
            if enemy.attack_hitbox and "DEATH" not in player.current_state_name:
                attack_type = 1
                if "HEAVY_ATTACK" in enemy.current_state_name:
                    attack_type = 2
                if (
                    enemy.attack_hitbox.colliderect(player.hitbox_rect)
                    and player not in enemy.hit_entities
                    and player.cooldowns["imunity"] <= 0
                ):
                    enemy.hit_entities.append(player)
                    cls.resolve_hit(enemy, player, attack_type)

    @staticmethod
    def resolve_hit(attacker: Entity, defender: Entity, attack_type: int) -> None:
        """
        Resolves the outcome of a successful hitbox intersection.
        Handles dodging, blocking angles, parrying, and damage application.

        Args:
            attacker (Entity): The entity delivering the attack.
            defender (Entity): The entity receiving the attack.
            attack_type (int): The type of attack (1 for Light, 2 for Heavy).
        """
        # 1. Check Dodge (Invulnerability frames)
        if defender.is_dodging:
            random.choice(attacker.sound_effects["miss"]).play()
            return

        # 2. Check Block / Parry
        if defender.is_blocking and attack_type == 1 or defender.is_parying:
            vec_to_attacker = pygame.Vector2(
                attacker.hitbox_rect.center
            ) - pygame.Vector2(defender.hitbox_rect.center)
            vec_direction = None
            if defender.direction_state == "right":
                vec_direction = pygame.Vector2(1, 0)
            elif defender.direction_state == "left":
                vec_direction = pygame.Vector2(-1, 0)
            elif defender.direction_state == "down":
                vec_direction = pygame.Vector2(0, 1)
            else:
                vec_direction = pygame.Vector2(0, -1)

            cos_angle = pygame.math.Vector2.dot(
                vec_direction, vec_to_attacker.normalize()
            )
            if cos_angle > 0:
                if defender.is_parying:
                    defender.sound_effects["parry"][0].play()
                    attacker.take_hit(0, 3, pygame.Vector2())
                    return
                else:
                    random.choice(attacker.sound_effects["hit"]).play()
                    return
            else:
                pass

        # 3. Direct Hit (Calculate Knockback and Apply Damage)
        knockback_dir = pygame.Vector2(defender.hitbox_rect.center) - pygame.Vector2(
            attacker.hitbox_rect.center
        )

        # Normalize the knockback vector so the distance doesn't affect the knockback speed
        if knockback_dir.length_squared() > 0:
            knockback_dir.normalize_ip()
        random.choice(attacker.sound_effects["damage"]).play()
        defender.take_hit(attacker.damage, attack_type, knockback_dir)
