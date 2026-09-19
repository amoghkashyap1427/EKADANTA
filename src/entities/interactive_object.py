import pygame
import math
from src.entities.base_entity import BaseEntity
from src.settings import COLORS, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.utils.helpers import load_font

class InteractiveObject(BaseEntity):
    def __init__(self, x: float, y: float, name: str, interaction_range: float = 80.0):
        super().__init__(x, y, name)
        self.interaction_range = interaction_range
        self.font = load_font(None, 24)
        self.prompt_surf = self.font.render("[E] INTERACT", True, COLORS["ivory"])
        self.is_near_player = False
        self.time = 0.0

    def check_proximity(self, player_x: float, player_y: float) -> bool:
        dist = math.hypot(self.x - player_x, self.y - player_y)
        self.is_near_player = dist <= self.interaction_range
        return self.is_near_player

    def interact(self, game):
        """Override this to provide specific interaction behavior."""
        pass

    def update(self, dt: float):
        self.time += dt

    def draw(self, surface: pygame.Surface, camera):
        # We don't draw the object itself here (the World class might draw it as part of bg)
        # But we do draw the interaction prompt if near
        pass
        
    def draw_ui(self, surface: pygame.Surface, camera):
        if self.is_near_player:
            # Hovering prompt
            screen_x = self.x - camera.x
            screen_y = self.y - camera.y - 60 + math.sin(self.time * 4.0) * 5
            
            # Draw tiny shadow/bg for text
            bg_rect = self.prompt_surf.get_rect(center=(screen_x, screen_y))
            bg_rect.inflate_ip(20, 10)
            
            # Semi-transparent dark background
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            pygame.draw.rect(s, COLORS["muted_gold"], s.get_rect(), 1)
            
            surface.blit(s, bg_rect)
            surface.blit(self.prompt_surf, self.prompt_surf.get_rect(center=(screen_x, screen_y)))
