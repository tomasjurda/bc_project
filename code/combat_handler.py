from settings import *
from player import Player
from general_states import Heavy_Attack
from sound_manager import SoundManager

class CombatHandler:
    def __init__(self, sound_manager : SoundManager):
        self.sound_manager = sound_manager


    def check_hits(self, player : Player, enemy_sprites : pygame.sprite.Group):
        # PLAYER ATTACK
        if player.attack_hitbox:
            attack_type = 1
            if issubclass(player.fsm.current_state.__class__, Heavy_Attack):
                attack_type = 2
            for enemy in enemy_sprites:
                if player.attack_hitbox.colliderect(enemy.hitbox_rect) and enemy not in player.hit_entities:
                    player.hit_entities.append(enemy)
                    self.resolve_hit(player, enemy, attack_type)
            if not player.hit_entities:
                self.sound_manager.play_sound(player.sound_effects['miss'][0])
        

        # ENEMY ATTACKS
        for enemy in enemy_sprites:
            if enemy.attack_hitbox:
                attack_type = 1
                if issubclass(enemy.fsm.current_state.__class__, Heavy_Attack):
                    attack_type = 2
                if enemy.attack_hitbox.colliderect(player.hitbox_rect) and player not in enemy.hit_entities:
                    enemy.hit_entities.append(player)
                    self.resolve_hit(enemy, player, attack_type)
                if not enemy.hit_entities:
                    self.sound_manager.play_sound(enemy.sound_effects['miss'][0])
    
    
    def resolve_hit(self, attacker, defender, attack_type):
        if defender.is_dodging:
            self.sound_manager.play_sound(rand.choice(attacker.sound_effects['miss']))
            return
        
        elif defender.is_blocking and attack_type == 1:
            vec_to_attacker = pygame.Vector2(attacker.hitbox_rect.center) - pygame.Vector2(defender.hitbox_rect.center)
            vec_direction = None
            if defender.direction_state == 'right': vec_direction = pygame.Vector2(1, 0)
            elif defender.direction_state == 'left': vec_direction = pygame.Vector2(-1, 0)
            elif defender.direction_state == 'down': vec_direction = pygame.Vector2(0, 1)
            else: vec_direction = pygame.Vector2(0, -1)

            cos_angle = pygame.math.Vector2.dot(vec_direction, vec_to_attacker.normalize())
            if cos_angle > 0:
                defender.stamina -= 1.0
                self.sound_manager.play_sound(rand.choice(attacker.sound_effects['hit']))
                return
            else:
                pass
        
        knockback_dir = pygame.Vector2(defender.hitbox_rect.center) - pygame.Vector2(attacker.hitbox_rect.center)
        self.sound_manager.play_sound(rand.choice(attacker.sound_effects['damage']))
        defender.take_hit(attacker.damage * attack_type, knockback_dir.normalize())
        
        