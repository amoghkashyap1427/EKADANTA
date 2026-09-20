import pygame
import math
from src.entities.base_entity import BaseEntity
from src.settings import COLORS

class Stranger(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40)
        self.target = None
        self.speed = 100.0
        self.time = 0.0
        self.is_shiva_revealed = False
        
        # Stranger Silhouette
        self.stranger_surf = pygame.Surface((150, 200), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(self.stranger_surf, (20, 20, 40), (40, 50, 70, 150))
        # Head
        pygame.draw.circle(self.stranger_surf, (20, 20, 40), (75, 40), 25)
        # Trident
        pygame.draw.line(self.stranger_surf, (40, 40, 70), (120, 10), (120, 180), 5)
        pygame.draw.line(self.stranger_surf, (40, 40, 70), (100, 40), (140, 40), 4)
        pygame.draw.line(self.stranger_surf, (40, 40, 70), (100, 40), (100, 10), 4)
        pygame.draw.line(self.stranger_surf, (40, 40, 70), (140, 40), (140, 10), 4)
        
        # Long flowing hair
        pygame.draw.arc(self.stranger_surf, (15, 15, 30), (50, 30, 70, 100), -math.pi/2, math.pi/2, 5)
        pygame.draw.arc(self.stranger_surf, (15, 15, 30), (40, 30, 90, 120), -math.pi/2, math.pi/2, 5)

        # Shiva Divine Form
        self.shiva_surf = pygame.Surface((150, 200), pygame.SRCALPHA)
        # Body (Ash/blue-gray)
        pygame.draw.ellipse(self.shiva_surf, (100, 120, 150), (40, 50, 70, 150))
        # Tiger Skin cloth (Subtle orange/black)
        pygame.draw.arc(self.shiva_surf, (200, 100, 50), (40, 120, 70, 60), 0, math.pi, 15)
        # Head
        pygame.draw.circle(self.shiva_surf, (100, 120, 150), (75, 40), 25)
        # Third eye
        pygame.draw.ellipse(self.shiva_surf, (255, 200, 50), (73, 30, 4, 8))
        # Crescent Moon
        pygame.draw.arc(self.shiva_surf, (255, 255, 200), (55, 20, 20, 20), math.pi/2, math.pi, 3)
        # Trident (Glowing)
        pygame.draw.line(self.shiva_surf, (255, 200, 100), (120, 10), (120, 180), 5)
        pygame.draw.line(self.shiva_surf, (255, 200, 100), (100, 40), (140, 40), 4)
        pygame.draw.line(self.shiva_surf, (255, 200, 100), (100, 40), (100, 10), 4)
        pygame.draw.line(self.shiva_surf, (255, 200, 100), (140, 40), (140, 10), 4)
        
        # Long flowing hair
        pygame.draw.arc(self.shiva_surf, (40, 40, 60), (50, 30, 70, 100), -math.pi/2, math.pi/2, 5)
        pygame.draw.arc(self.shiva_surf, (40, 40, 60), (40, 30, 90, 120), -math.pi/2, math.pi/2, 5)

    def update(self, dt: float):
        self.time += dt
        if self.target:
            tx, ty = self.target
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist > 10:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt

    def draw(self, surface: pygame.Surface, camera):
        # Draw aura
        if self.is_shiva_revealed:
            aura_radius = 100 + math.sin(self.time * 3) * 15
            pygame.draw.circle(surface, (100, 150, 255, 40), (int(self.x - camera.x), int(self.y - camera.y - 40)), int(aura_radius))
            surface.blit(self.shiva_surf, (self.x - camera.x - 50, self.y - camera.y - 120))
        else:
            aura_radius = 80 + math.sin(self.time * 2) * 10
            pygame.draw.circle(surface, (100, 100, 150, 30), (int(self.x - camera.x), int(self.y - camera.y - 40)), int(aura_radius))
            surface.blit(self.stranger_surf, (self.x - camera.x - 50, self.y - camera.y - 120))
