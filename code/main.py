from settings import *
from player import Player
from slime import Slime
from skeleton import Skeleton
from menu import Menu
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import *

"""
python -m venv myenv        
myenv/Scripts/activate
pip install pygame-ce
pip install pytmx
python code\main.py  
"""

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.map_width = 0
        self.map_height = 0
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.enemy_spawn_positions = []
        self.player_spawn_positions = []
        self.setup_game()
        self.state = 'menu'
        self.menu = Menu(self.display_surface, ['Start Game', 'Quit'])
        self.death_screen = Menu(self.display_surface, ['Respawn', 'Menu'])

    def setup_game(self):
        map = load_pygame(join('maps','map.tmx'))
        self.map_width = map.width
        self.map_height = map.height

        for x,y,image in map.get_layer_by_name('Ground').tiles():
            GroundSprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)
        for x,y,image in map.get_layer_by_name('OnGround').tiles():
            OnGroundSprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)
        for x,y,image in map.get_layer_by_name('Walls').tiles():
            WallSprite((x * TILE_SIZE , y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Props'):
            PropSprite((obj.x, obj.y), obj.image, self.all_sprites)
        for obj in map.get_layer_by_name('Collision'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in map.get_layer_by_name('SpawnPoints'):
            if obj.name == 'Player':
                self.player_spawn_positions.append((obj.x, obj.y))
            else:
                self.enemy_spawn_positions.append((obj.x, obj.y, obj.name))
        
        self.player = Player(choice(self.player_spawn_positions), self.all_sprites, self.collision_sprites, self.enemy_sprites, pygame.image.load(join('graphics', 'models', 'Player.png')).convert_alpha())
        for point in self.enemy_spawn_positions:
            if point[2] == 'Slime':
                Slime((point[0], point[1]), (self.all_sprites, self.enemy_sprites), self.collision_sprites, pygame.image.load(join('graphics', 'models', 'Slime.png')).convert_alpha(), self.player)
            elif point[2] == 'Skeleton':
                Skeleton((point[0], point[1]), (self.all_sprites, self.enemy_sprites), self.collision_sprites, pygame.image.load(join('graphics', 'models', 'Skeleton.png')).convert_alpha(), self.player)
    
    def reset_game(self):
        # Kill all enemies
        for enemy in self.enemy_sprites.sprites():
            enemy.kill()
        # Respawn player
        self.player.respawn(choice(self.player_spawn_positions))
        # Spawn new enemies
        for x, y, name in self.enemy_spawn_positions:
            if name == 'Slime':
                Slime((x, y), (self.all_sprites, self.enemy_sprites), self.collision_sprites, pygame.image.load(join('graphics', 'models', 'Slime.png')).convert_alpha(), self.player)
            elif name == 'Skeleton':
                Skeleton((x, y), (self.all_sprites, self.enemy_sprites), self.collision_sprites, pygame.image.load(join('graphics', 'models', 'Skeleton.png')).convert_alpha(), self.player)

    def show_ui(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, 'white')
        self.display_surface.blit(score_text, (20, 20))

    def run(self):
        while self.running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Menu
            if self.state == 'menu':
                choice = self.menu.input()
                if choice == 'Start Game':
                    self.state = 'playing'
                    self.reset_game()
                elif choice == 'Quit':
                    self.running = False
                self.menu.draw()
                pygame.display.update()
            elif self.state == 'death':
                choice = self.death_screen.input()
                if choice == 'Respawn':
                    self.state = 'playing'
                    self.reset_game()
                elif choice == 'Menu':
                    self.state = 'menu'
                self.death_screen.draw()
                pygame.display.update()

            # Playing
            elif self.state == 'playing':
                if not self.player.alive:
                    self.state = 'death'
                elif not self.enemy_sprites:
                    print('you won')
                    self.state = 'menu'
                else:
                    #deltaTime
                    dt = self.clock.tick(60) / 1000
                    
                    #update logic
                    self.all_sprites.update(dt)
                    #draw
                    self.display_surface.fill('black')
                    self.all_sprites.draw(self.display_surface, self.player.rect.center, self.map_width, self.map_height)
                    self.show_ui()
                    pygame.display.flip()
        # Exit
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
