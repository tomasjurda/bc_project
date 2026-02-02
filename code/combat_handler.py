from settings import *
from player import Player
from general_states import Heavy_Attack

class CombatHandler:
    def update(self, player : Player, enemy_sprites : pygame.sprite.Group):
        # HURT ENEMY
        if player.attack_hitbox:
            attack_type = 1
            if issubclass(player.fsm.current_state.__class__, Heavy_Attack):
                attack_type = 2
            for enemy in enemy_sprites:
                if player.attack_hitbox.colliderect(enemy.hitbox_rect) and enemy not in player.hit_entities:
                    player.hit_entities.append(enemy)
                    knockback_dir = pygame.Vector2(enemy.hitbox_rect.center) - pygame.Vector2(player.hitbox_rect.center)
                    enemy.take_hit(attack_type , player.damage, knockback_dir.normalize(), player)

        #HURT PLAYER
        for enemy in enemy_sprites:
            if enemy.attack_hitbox:
                attack_type = 1
                if issubclass(enemy.fsm.current_state.__class__, Heavy_Attack):
                    attack_type = 2
                if enemy.attack_hitbox.colliderect(player.hitbox_rect) and player not in enemy.hit_entities:
                    enemy.hit_entities.append(player)
                    knockback_dir = pygame.Vector2(player.hitbox_rect.center) - pygame.Vector2(enemy.hitbox_rect.center)
                    player.take_hit(attack_type , enemy.damage, knockback_dir.normalize(), enemy)