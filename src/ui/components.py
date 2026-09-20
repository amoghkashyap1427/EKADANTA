import pygame
import math
from src.settings import COLORS

class Button:
    def __init__(self, text: str, font: pygame.font.Font, x: int, y: int, action=None, disabled: bool = False):
        self.text = text
        self.font = font
        self.x = x
        self.y = y
        self.action = action
        self.disabled = disabled
        
        self.is_hovered = False
        self.hover_progress = 0.0  # 0 to 1 for smooth transitions
        
        # Dimensions
        self._render_text()
        self.rect = self.text_surface.get_rect(center=(self.x, self.y))
        
        self.particles = []

    def _render_text(self):
        color = COLORS["charcoal"] if self.disabled else (
            self._lerp_color(COLORS["ivory"], COLORS["muted_gold"], self.hover_progress)
        )
        # If disabled, use a very dim color
        if self.disabled:
            color = (80, 80, 80)
            
        # Optional scale effect
        scale = 1.0 + (self.hover_progress * 0.05)
        # We can simulate scale by rendering a slightly larger font, but it's expensive.
        # Alternatively, we can scale the surface.
        base_surface = self.font.render(self.text, True, color)
        
        if scale != 1.0:
            new_size = (int(base_surface.get_width() * scale), int(base_surface.get_height() * scale))
            self.text_surface = pygame.transform.smoothscale(base_surface, new_size)
        else:
            self.text_surface = base_surface

    def _lerp_color(self, c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    def update(self, dt: float, mouse_pos: tuple[int, int], is_focused: bool = False):
        if self.disabled:
            return
            
        # Check hover
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos) or is_focused
        
        # Smooth transition
        if self.is_hovered:
            self.hover_progress = min(1.0, self.hover_progress + dt * 5.0)
            # Add particles occasionally
            import random
            if random.random() < 0.1:
                self.particles.append({
                    "x": self.rect.x + random.random() * self.rect.width,
                    "y": self.rect.bottom,
                    "vy": -random.random() * 20 - 10,
                    "life": 1.0
                })
        else:
            self.hover_progress = max(0.0, self.hover_progress - dt * 5.0)
            
        self._render_text()
        self.rect = self.text_surface.get_rect(center=(self.x, self.y))
        
        # Update particles
        for p in self.particles[:]:
            p["x"] += math.sin(p["life"] * 10) * 0.5
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface: pygame.Surface):
        # Draw underline if hovered
        if self.hover_progress > 0.01:
            underline_width = int(self.rect.width * self.hover_progress)
            underline_rect = pygame.Rect(
                self.rect.centerx - underline_width // 2,
                self.rect.bottom + 2,
                underline_width,
                2
            )
            pygame.draw.rect(surface, COLORS["muted_gold"], underline_rect)
            
            # Draw glow
            glow = pygame.Surface((self.rect.width + 40, self.rect.height + 40), pygame.SRCALPHA)
            glow_alpha = int(50 * self.hover_progress)
            pygame.draw.ellipse(glow, (*COLORS["warm_glow"], glow_alpha), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
            
        surface.blit(self.text_surface, self.rect)
        
        # Draw particles
        for p in self.particles:
            alpha = max(0, min(255, int(255 * p["life"])))
            color = (*COLORS["gold"], alpha)
            # Create a small surface for the particle
            psurf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(psurf, color, (2, 2), 2)
            surface.blit(psurf, (int(p["x"]), int(p["y"])))
