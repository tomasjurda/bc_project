from settings import *

class Menu:
    def __init__(self, screen, options):
        self.screen = screen
        self.font = pygame.font.Font(None, 60)
        self.options = options
        self.selected = 0

    def draw(self):
        self.screen.fill((20, 20, 20))
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (100, 100, 100)
            text_surf = self.font.render(option, True, color)
            rect = text_surf.get_rect(center=(self.screen.get_width() // 2, 200 + i * 80))
            self.screen.blit(text_surf, rect)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.options)
            pygame.time.wait(150)
        elif keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            pygame.time.wait(150)
            return self.options[self.selected]
        return None