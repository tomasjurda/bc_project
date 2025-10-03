from settings import *
from FSM import *

class I_Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_sheet):
        super().__init__(groups)
        self.ysort = True
        self.dt = 0

        self.max_hitpoints = 10
        self.hitpoints = self.max_hitpoints
        self.max_stamina = 10.0
        self.stamina = self.max_stamina
        self.damage = 5

        # Basic frame setup
        self.frame_width = 64
        self.frame_height = 64
        self.animation_speed = 5

        # Animation state
        #self.status = 'idle'
        self.direction_state = 'down'
        self.frame_index = 0
        self.time_accumulator = 0
        
        self.sprite_sheet = sprite_sheet
        self.image = pygame.Surface((self.frame_width, self.frame_height))
        self.image.fill('blue')
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-30,-30)
        
        # Movement
        self.direction = pygame.Vector2()
        self.speed = 70

        # Attack
        #self.attacking = False
        #self.attack_cooldown = 1000
        #self.attack_time = 0
        # Stun
        #self.stunned = False
        #self.stun_cooldown = 200
        #self.stun_time = 0

    def load_frames(self, row , cols, rotate):
        """Extract frames from a given row in the sprite sheet."""
        frames = []
        for i in range(cols):
            frame = pygame.transform.flip(self.sprite_sheet.subsurface((i * self.frame_width / 2, row * self.frame_height / 2, self.frame_width / 2, self.frame_height / 2)), rotate , 0)
            frame = pygame.transform.scale2x(frame)
            frames.append(frame)
        return frames

    def move(self, collision_sprites, extra = 1):
        self.hitbox_rect.x += self.direction.x * self.speed * self.dt * extra
        self.collision(collision_sprites, 'horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * self.dt * extra
        self.collision(collision_sprites,'vertical')
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
        
    def collision(self, collision_sprites ,direction):
        for sprite in collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0 : self.hitbox_rect.right = sprite.rect.left 
                    if self.direction.x < 0 : self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0 : self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.hitbox_rect.top = sprite.rect.bottom
    
    def draw_bars(self, surface, offset):
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.hitpoints / self.max_hitpoints
        stamina_ratio = self.stamina / self.max_stamina

        x = self.rect.x - offset.x
        health_y = self.rect.y - offset.y - bar_height * 2
        stamina_y = self.rect.y - offset.y - bar_height

        pygame.draw.rect(surface, 'black', (x, health_y, bar_width, bar_height * 2))
        pygame.draw.rect(surface, 'green', (x, health_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(surface, 'yellow', (x, stamina_y, bar_width * stamina_ratio, bar_height))
    
    def animate(self):
        pass

    def control(self):
        pass

    def update(self, dt):
        pass
