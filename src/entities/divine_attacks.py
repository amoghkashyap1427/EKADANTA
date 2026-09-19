import pygame
import math
from src.entities.base_entity import BaseEntity
from src.settings import COLORS

class DivineShockwave(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 0)
        self.radius = 10.0
        self.max_radius = 400.0
        self.expansion_speed = 300.0
        self.life = 0.0
        self.active = True
        
    def update(self, dt: float):
        if not self.active: return
        self.radius += self.expansion_speed * dt
        self.life += dt
        if self.radius > self.max_radius:
            self.active = False
            
    def draw(self, surface: pygame.Surface, camera):
        if not self.active: return
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        # Calculate alpha based on life
        alpha = max(0, 255 - int((self.radius / self.max_radius) * 255))
        
        surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*COLORS["ivory"], alpha), (int(self.radius), int(self.radius)), int(self.radius), 4)
        pygame.draw.circle(surf, (*COLORS["muted_gold"], alpha//2), (int(self.radius), int(self.radius)), int(self.radius) - 4, 10)
        
        surface.blit(surf, surf.get_rect(center=(screen_x, screen_y)))
        
class TridentStrikeArea(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 0)
        self.radius = 80.0
        self.timer = 1.5 # 1.5s telegraph
        self.active = True
        self.struck = False
        self.strike_duration = 0.3
        
    def update(self, dt: float):
        if not self.active: return
        if not self.struck:
            self.timer -= dt
            if self.timer <= 0:
                self.struck = True
        else:
            self.strike_duration -= dt
            if self.strike_duration <= 0:
                self.active = False

    def draw(self, surface: pygame.Surface, camera):
        if not self.active: return
        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        
        if not self.struck:
            # Telegraph
            alpha = int(100 + abs(math.sin(self.timer * 10)) * 100)
            surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLORS["crimson"], alpha), (int(self.radius), int(self.radius)), int(self.radius), 2)
            pygame.draw.circle(surf, (*COLORS["crimson"], 50), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(surf, surf.get_rect(center=(screen_x, screen_y)))
        else:
            # Strike effect
            alpha = max(0, int((self.strike_duration / 0.3) * 255))
            surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLORS["gold"], alpha), (int(self.radius), int(self.radius)), int(self.radius))
            
            # Vertical beam
            pygame.draw.rect(surface, (*COLORS["ivory"], alpha), (screen_x - int(self.radius), screen_y - 1000, int(self.radius*2), 1000 + int(self.radius)))
            surface.blit(surf, surf.get_rect(center=(screen_x, screen_y)))
