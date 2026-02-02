from settings import *
from FSM import *
from GridMap import GridMap
from animation import Animation
from enemy_states import *
from player_states import *


class I_Entity(pygame.sprite.Sprite):
    g_map = GridMap()
    
    def __init__(self, pos, groups, sprite_sheet):
        super().__init__(groups)
        self.ysort = True
        self.dt = 0

        self.max_hitpoints = 50
        self.hitpoints = self.max_hitpoints
        self.max_stamina = 10.0
        self.stamina = self.max_stamina
        self.damage = 5

        self.hit_entities = []

        # Basic frame setup and animation
        self.current_animation = None
        self.frame_width = 64
        self.frame_height = 64
        self.direction_state = 'down'
        
        # Hitbox and sprites
        self.sprite_sheet = sprite_sheet
        self.image = pygame.Surface((self.frame_width, self.frame_height))
        self.image.fill('blue')
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20,-20)
        # Movement
        self.direction = pygame.Vector2()
        self.speed = 70

    def load_frames(self, row , cols, rotate):
        """Extract frames from a given row in the sprite sheet."""
        frames = []
        for i in range(cols):
            frame = pygame.transform.flip(self.sprite_sheet.subsurface((i * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)), rotate , 0)
            frames.append(frame)
        return frames

    def update_direction(self):
        # Set direction state for animation
        if self.direction.y > 0.2:
            self.direction_state = 'down'
        elif self.direction.y < -0.2:
            self.direction_state = 'up'
        if self.direction.x > 0.2:
            self.direction_state = 'right'
        elif self.direction.x < -0.2:
            self.direction_state = 'left'

    def move(self, collision_sprites, extra = 1):
        #self.hitbox_rect.x += self.direction.x * self.speed * self.dt * extra
        self.rect.x += self.direction.x * self.speed * self.dt * extra
        self.collision(collision_sprites, 'horizontal')
        #self.hitbox_rect.y += self.direction.y * self.speed * self.dt * extra
        self.rect.y += self.direction.y * self.speed * self.dt * extra
        self.collision(collision_sprites,'vertical')
        #self.rect.center = self.hitbox_rect.center
        self.hitbox_rect.center = self.rect.center
        
    def collision(self, collision_sprites ,direction):
        for sprite in collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0 : self.rect.right = sprite.rect.left 
                    if self.direction.x < 0 : self.rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0 : self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.rect.top = sprite.rect.bottom
    
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
    
    def attack(self):
        #create attack hitbox
        self.attack_hitbox = self.hitbox_rect.copy().inflate(-5, -5)
        if self.direction_state == 'right':
            self.attack_hitbox.midleft = self.hitbox_rect.midright
        elif self.direction_state == 'left':
            self.attack_hitbox.midright = self.hitbox_rect.midleft
        elif self.direction_state == 'up':
            self.attack_hitbox.midbottom = self.hitbox_rect.midtop
        else:
            self.attack_hitbox.midtop = self.hitbox_rect.midbottom

        self.hit_entities = []
        #play sound
        play_sound = rand.choice(self.sound_effects['miss'])
        play_sound.set_volume(0.4)
        play_sound.play()

    def take_hit(self, attack_type , damage, knockback, attack_source = None):
        current_state = self.fsm.current_state.__class__
        
        if issubclass(current_state, Dodge):
            print("Dodged!")
            return
        
        elif issubclass(current_state, Block) and attack_type == 1:
            if attack_source:
                vec_to_source = pygame.Vector2(attack_source.hitbox_rect.center) - pygame.Vector2(self.hitbox_rect.center)
                vec_direction = None
                if self.direction_state == 'right': vec_direction = pygame.Vector2(1, 0)
                elif self.direction_state == 'left': vec_direction = pygame.Vector2(-1, 0)
                elif self.direction_state == 'down': vec_direction = pygame.Vector2(0, 1)
                else: vec_direction = pygame.Vector2(0, -1)

                cos_angle = pygame.math.Vector2.dot(vec_direction, vec_to_source.normalize())
                if cos_angle > 0:
                    self.stamina -= 1.0
                    print("Blocked!")
                    return
                else:
                    print("Wrong dir!")
        
        self.hitpoints -= damage * attack_type

        if self.hitpoints <= 0:
            self.fsm.change_state(self.states["death"])
        else:
            self.direction = knockback
            self.fsm.change_state(self.states["hurt"])

    def set_animation(self, speed=8, loop = True, loop_start = 0, sync_with_current = False):
        frames = self.animations[self.fsm.current_state.__class__.__name__][self.direction_state]

        saved_frame_index = 0
        saved_time = 0

        if sync_with_current and self.current_animation:
            saved_frame_index = self.current_animation.frame_index
            saved_time = self.current_animation.time_accumulator

        self.current_animation = Animation(frames, speed, loop , loop_start)
        
        if sync_with_current:
            safe_index = saved_frame_index if saved_frame_index < len(frames) else 0
            self.current_animation.frame_index = safe_index
            self.current_animation.time_accumulator = saved_time

        self.image = self.current_animation.frames[int(self.current_animation.frame_index)]

    def animate(self):
        if self.current_animation:
            self.image = self.current_animation.update(self.dt)

    def update_cooldowns(self, dt):
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= dt
        if self.stamina < 10.0:
            self.stamina += dt * 3

    def update(self, dt):
        self.dt = dt
        self.update_cooldowns(dt)
        self.fsm.update()
        self.animate()
