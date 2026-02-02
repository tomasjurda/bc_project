from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.Vector2()

    def draw(self, surface : pygame.Surface, player_pos, map_width, map_height):
        self.offset.x = max(0, min(player_pos[0] - WINDOW_WIDTH / 2, map_width * TILE_SIZE - WINDOW_WIDTH))
        self.offset.y = max(0, min(player_pos[1] - WINDOW_HEIGHT / 2, map_height * TILE_SIZE - WINDOW_HEIGHT))

        
        ground_and_col_sprites = [sprite for sprite in self if not hasattr(sprite, 'ysort')]
        ysort_sprites = [sprite for sprite in self if hasattr(sprite, 'ysort')]

        for sprite in ground_and_col_sprites:
            surface.blit(sprite.image, (int(sprite.rect.topleft[0] - self.offset.x), int(sprite.rect.topleft[1] - self.offset.y)))
        for sprite in sorted(ysort_sprites, key=lambda sprite: sprite.rect.bottomright[1]):
            if hasattr(sprite, 'invisible'):
                continue
            surface.blit(sprite.image, (int(sprite.rect.topleft[0] - self.offset.x), int(sprite.rect.topleft[1] - self.offset.y)))
            if hasattr(sprite, 'draw_bars'):
                sprite.draw_bars(surface, self.offset)
            if hasattr(sprite, "attack_hitbox"):
                if sprite.attack_hitbox:
                    #pygame.draw.rect(surface, 'black', sprite.attack_hitbox.move(-self.offset.x, -self.offset.y))
                    pass
        
        
        
