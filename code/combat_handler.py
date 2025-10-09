from settings import *
from player import Player

class CombatHandler:
    def update(self, player : Player, enemy_sprites : pygame.sprite.Group):
        # HURT ENEMY
        if player.attack_hitbox != None:
            for enemy in enemy_sprites:
                if player.attack_hitbox.colliderect(enemy.hitbox_rect):
                    enemy.take_hit(1 , player.damage)
        #HURT PLAYER
        for enemy in enemy_sprites:
            if enemy.attack_hitbox != None:
                if player.attack_hitbox.colliderect(enemy.hitbox_rect):
                    player.take_hit(1 , enemy.damage)