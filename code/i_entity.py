from settings import *
from fsm import FSM
from grid_map import GridMap
from animation import Animation
from enemy_states import *
from player_states import *


class I_Entity(pygame.sprite.Sprite):
    g_map = GridMap()
    
    def __init__(self, pos, groups, sprite_sheet):
        super().__init__(groups)
        self.ysort = True
        self.dt = 0

        self.is_blocking = False
        self.is_dodging = False

        self.hitpoints = self.max_hitpoints = 50
        self.stamina = self.max_stamina = 10.0
        self.damage = 5

        self.hit_entities = []
        self.fsm = None

        # Basic frame setup and animation
        self.current_animation = None
        self.frame_width = 64
        self.frame_height = 64
        self.direction_state = 'down'
        
        # Hitbox and sprites
        self.sprite_sheet = sprite_sheet
        self.image = pygame.Surface((self.frame_width, self.frame_height))
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-30,-30)
        self.attack_hitbox = None
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


    def respawn(self):
        self.hitpoints = self.max_hitpoints
        

    def update_direction(self):
        # Set direction state for animation
        if abs(self.direction.x) > abs(self.direction.y):
                self.direction_state = 'right' if self.direction.x > 0 else 'left'
        else:
            self.direction_state = 'down' if self.direction.y > 0 else 'up'


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
    

    def draw_ui(self, surface : pygame.surface.Surface, offset, debug_mode):
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

        if debug_mode:
            state_y = self.rect.y - offset.y + self.frame_height - 10
            font = pygame.font.Font(None, 20)
            state_text = self.fsm.current_state.__class__.__name__
            clean_state_text = state_text.replace("Player_", "").replace("Enemy_", "").upper()
            state = font.render(f"{clean_state_text}", True, 'white')
            surface.blit(state, (x + 32 - state.width / 2, state_y))

            hitbox_surface = pygame.Surface((self.hitbox_rect.width, self.hitbox_rect.height), pygame.SRCALPHA)
            hitbox_col = None
            if self.is_dodging:
                hitbox_col = (0, 0, 0, 128)
            elif self.is_blocking:
                hitbox_col = (255, 0, 0, 128)
            else:
                hitbox_col = (0, 255, 0, 128)
            hitbox_surface.fill(hitbox_col)
            surface.blit(hitbox_surface, (self.hitbox_rect.x - offset.x, self.hitbox_rect.y - offset.y))
    

    def create_attack_hitbox(self):
        self.attack_hitbox = self.hitbox_rect.copy()
        if self.direction_state == 'right':
            self.attack_hitbox.midleft = self.hitbox_rect.midright
            
        elif self.direction_state == 'left':
            self.attack_hitbox.midright = self.hitbox_rect.midleft

        elif self.direction_state == 'up':
            self.attack_hitbox.midbottom = self.hitbox_rect.midtop

        else:
            self.attack_hitbox.midtop = self.hitbox_rect.midbottom

        self.hit_entities = []


    def take_hit(self, damage, knockback):
        self.hitpoints -= damage

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
            self.stamina += dt * 2


    def update(self, dt):
        pass
