from settings import *
from player import Player

class CombatHandler:
    def update(self, player : Player, enemy_sprites : pygame.sprite.Group):
        # HURT ENEMY
        if player.attack_hitbox != None:
            for enemy in enemy_sprites:
                if player.attack_hitbox.colliderect(enemy.hitbox_rect):
                    knockback_dir = pygame.Vector2(enemy.hitbox_rect.center) - pygame.Vector2(player.hitbox_rect.center)
                    enemy.take_hit(1 , player.damage, knockback_dir.normalize())

        #HURT PLAYER
        for enemy in enemy_sprites:
            if enemy.attack_hitbox != None:
                if enemy.attack_hitbox.colliderect(player.hitbox_rect):
                    knockback_dir = pygame.Vector2(player.hitbox_rect.center) - pygame.Vector2(enemy.hitbox_rect.center)
                    player.take_hit(1 , enemy.damage, knockback_dir.normalize())