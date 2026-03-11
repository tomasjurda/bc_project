"""Module"""

import random
import pygame


class CombatManager:
    def check_hits(self, player, enemy_sprites):
        # PLAYER ATTACK
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
                    self.resolve_hit(player, enemy, attack_type)

        # ENEMY ATTACKS
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
                    self.resolve_hit(enemy, player, attack_type)

    def resolve_hit(self, attacker, defender, attack_type):
        if defender.is_dodging:
            random.choice(attacker.sound_effects["miss"]).play()
            return

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

        knockback_dir = pygame.Vector2(defender.hitbox_rect.center) - pygame.Vector2(
            attacker.hitbox_rect.center
        )
        if knockback_dir.length_squared() > 0:
            knockback_dir.normalize_ip()
        random.choice(attacker.sound_effects["damage"]).play()
        defender.take_hit(attacker.damage, attack_type, knockback_dir)
