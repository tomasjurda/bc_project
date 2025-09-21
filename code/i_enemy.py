from settings import *
from i_entity import I_Entity
"""
NPCs that are immediatly hostile
"""
class I_Enemy(I_Entity):
    def __init__(self, pos, groups, collision_sprites, player):
        super().__init__(pos, groups, collision_sprites)
        self.player = player
        self.last_player_location = pygame.Vector2()
        self.score_value = 5
        self.heal_value = 5
        self.stuck_counter = 0 #fuj
        self.prev_position = pygame.Vector2(self.rect.center) #fuj

    def control(self):
        player_center = self.player.hitbox_rect.center
        self_center = self.hitbox_rect.center
        to_player = pygame.Vector2(player_center) - pygame.Vector2(self_center)
        distance = to_player.length()

        # Attack
        if self.hitbox_rect.colliderect(self.player.hitbox_rect) and not self.attacking and self.player.status != 'death':
            self.attack()
            knockback_dir = to_player.normalize() if distance != 0 else pygame.Vector2()
            self.player.take_damage(self.damage, knockback_dir)
            return

        # Vision check
        if distance <= self.vision:
            blocked = any(ob.rect.clipline(self.rect.center, self.player.rect.center) for ob in self.collision_sprites)
            if not blocked:
                self.last_player_location = pygame.Vector2(player_center)
                if to_player.length() > 0:
                    self.direction = to_player.normalize()
                self.status = 'walk'
                return

        # Move toward last known position
        if self.last_player_location != pygame.Vector2():
            to_last_pos = self.last_player_location - pygame.Vector2(self_center)
            if to_last_pos.length() > 10:
                self.direction = to_last_pos.normalize()
                self.status = 'walk'

                # Check for being stuck , cely fuj
                if pygame.Vector2(self.rect.center).distance_to(self.prev_position) < 2:
                    self.stuck_counter += 1
                else:
                    self.stuck_counter = 0
                if self.stuck_counter > 5:
                    # Apply small random offset
                    jitter = pygame.Vector2(uniform(-1, 1), uniform(-1, 1))
                    self.direction += jitter
                    self.direction = self.direction.normalize()
                    self.stuck_counter = 0
                self.prev_position = pygame.Vector2(self.rect.center)
                return

        # Idle
        self.direction = pygame.Vector2()
        self.status = 'idle'


    def animate(self, dt):
        frames = self.animations[self.status][self.direction_state]
        self.time_accumulator += dt
        if self.time_accumulator >= 1 / self.animation_speed:
            self.time_accumulator = 0
            self.frame_index += 1

            if self.status == 'death' and self.frame_index >= len(frames):
                self.player.score += self.score_value
                self.player.heal(self.heal_value)
                self.kill()

            # If attack ends, return to idle
            if self.status == 'attack' and self.frame_index >= len(frames):
                #self.attacking = False
                self.status = 'idle'
                self.frame_index = 0

            self.frame_index %= len(frames)
            self.image = frames[self.frame_index]
