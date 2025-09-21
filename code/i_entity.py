from settings import *

class I_Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
        self.ysort = True

        self.max_hitpoints = 10
        self.hitpoints = self.max_hitpoints
        self.damage = 5

        # Basic frame setup
        self.frame_width = 32
        self.frame_height = 32
        self.animation_speed = 5

        # Animation state
        self.status = 'idle'
        self.direction_state = 'down'
        self.frame_index = 0
        self.time_accumulator = 0
        self.image = pygame.Surface((self.frame_width, self.frame_height))
        self.image.fill('blue')
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-18,-20)
        
        # Movement
        self.direction = pygame.Vector2()
        self.speed = 70

        # Attack
        self.attacking = False
        self.attack_cooldown = 1000
        self.attack_time = 0
        # Stun
        self.stunned = False
        self.stun_cooldown = 200
        self.stun_time = 0

    def load_frames(self, row , cols, rotate):
        """Extract frames from a given row in the sprite sheet."""
        frames = []
        for i in range(cols):
            frame = pygame.transform.flip(self.sprite_sheet.subsurface((i * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)), rotate , 0)
            frames.append(frame)
        return frames
    
    def control(self):
        pass

    def take_damage(self, damage, knockback):
        self.hitpoints -= damage
        self.direction = knockback
        if self.hitpoints <= 0:
            self.status = 'death'
            self.direction = pygame.Vector2()
            self.frame_index = 0
        else:
            self.stunned = True
            self.stun_time = pygame.time.get_ticks()
            self.frame_index = 0  # Restart animation
            self.status = 'idle'

    def move(self, dt):
        if self.direction.magnitude_squared() > 0:
            # Movement
            self.status = 'walk'
            self.hitbox_rect.x += self.direction.x * self.speed * dt
            self.collision('horizontal')
            self.hitbox_rect.y += self.direction.y * self.speed * dt
            self.collision('vertical')
            self.rect.center = self.hitbox_rect.center
            # Set direction state for animation
            if self.direction.y > 0.2:
                self.direction_state = 'down'
            elif self.direction.y < -0.2:
                self.direction_state = 'up'
            if self.direction.x > 0.2:
                self.direction_state = 'right'
            elif self.direction.x < -0.2:
                self.direction_state = 'left'
        elif not self.attacking:
            self.status = 'idle'
        
    def attack(self):
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.frame_index = 0  # Restart animation
        self.status = 'attack'
    
    def check_cooldowns(self, dt):
        current_time = pygame.time.get_ticks()
        if self.stunned:
            self.move(dt * 1.5)
            if current_time - self.stun_time >= self.stun_cooldown:
                self.stunned = False
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0 : self.hitbox_rect.right = sprite.rect.left 
                    if self.direction.x < 0 : self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0 : self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.hitbox_rect.top = sprite.rect.bottom
    
    def animate(self, dt):
        pass

    def draw_health_bar(self, surface, offset):
        bar_width = self.rect.width
        bar_height = 4
        health_ratio = self.hitpoints / self.max_hitpoints

        x = self.rect.x - offset.x
        y = self.rect.y - offset.y - bar_height - 2

        pygame.draw.rect(surface, 'red', (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, 'green', (x, y, bar_width * health_ratio, bar_height))

    def update(self, dt):
        if self.status != 'death':
            self.check_cooldowns(dt)
            if not self.stunned:
                self.control()
                self.move(dt)
        self.animate(dt)