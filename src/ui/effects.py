import pygame
import math
import random
from src.settings import COLORS

class Diya:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.time = random.random() * 10.0
        self.particles = []
        
        # Pre-render the clay base to save performance
        self.base_surface = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.base_surface, COLORS["dark_brown"], (0, 0, 40, 20))
        pygame.draw.ellipse(self.base_surface, (80, 50, 25), (4, 2, 32, 16))
        
    def update(self, dt: float):
        self.time += dt * 5.0
        
        # Spawn particles
        if random.random() < 0.2:
            max_life = random.uniform(0.5, 1.5)
            self.particles.append({
                "x": self.x + random.uniform(-5, 5),
                "y": self.y - 10,
                "vx": random.uniform(-10, 10),
                "vy": random.uniform(-30, -15),
                "life": max_life,
                "max_life": max_life
            })
            
        # Update particles
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface: pygame.Surface):
        # Draw base
        surface.blit(self.base_surface, (self.x - 20, self.y - 10))
        
        # Draw glow
        glow_size = 60 + math.sin(self.time) * 5
        glow = pygame.Surface((int(glow_size), int(glow_size)), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*COLORS["warm_glow"], 30), glow.get_rect())
        surface.blit(glow, glow.get_rect(center=(self.x, self.y - 10)))
        
        # Draw flame (polygon that flickers)
        flame_height = 15 + math.sin(self.time * 2.0) * 3
        flame_offset = math.cos(self.time * 3.0) * 2
        
        points = [
            (self.x - 4, self.y - 5),
            (self.x + 4, self.y - 5),
            (self.x + flame_offset, self.y - 5 - flame_height)
        ]
        pygame.draw.polygon(surface, COLORS["saffron"], points)
        pygame.draw.polygon(surface, COLORS["gold"], [
            (self.x - 2, self.y - 5),
            (self.x + 2, self.y - 5),
            (self.x + flame_offset * 0.5, self.y - 5 - flame_height * 0.7)
        ])
        
        # Draw particles (smoke/sparks)
        for p in self.particles:
            alpha = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
            color = (*COLORS["gold"], alpha)
            psurf = pygame.Surface((2, 2), pygame.SRCALPHA)
            psurf.fill(color)
            surface.blit(psurf, (int(p["x"]), int(p["y"])))

class GaneshaSilhouette:
    def __init__(self):
        self.surface = pygame.Surface((600, 600), pygame.SRCALPHA)
        self._draw_abstract_silhouette()
        self.time = 0.0
        self.alpha = 0.0
        self.target_alpha = 40.0 # Extremely subtle

    def _draw_abstract_silhouette(self):
        color = (*COLORS["saffron"], 255) # Render full opacity, handle alpha during blit
        
        # Head
        pygame.draw.circle(self.surface, color, (300, 200), 80)
        
        # Ears (Ellipses)
        pygame.draw.ellipse(self.surface, color, (140, 120, 120, 180))
        pygame.draw.ellipse(self.surface, color, (340, 120, 120, 180))
        
        # Crown
        pygame.draw.polygon(self.surface, color, [(250, 130), (350, 130), (300, 40)])
        
        # Trunk (Curved polygon)
        pygame.draw.polygon(self.surface, color, [(270, 250), (330, 250), (310, 450), (250, 480), (260, 430)])
        
        # Base/Body
        pygame.draw.ellipse(self.surface, color, (150, 300, 300, 250))

    def update(self, dt: float):
        self.time += dt
        
    def draw(self, surface: pygame.Surface, fade_in_progress: float, logical_width: float, logical_height: float):
        # Pulse alpha slowly
        pulse = math.sin(self.time * 0.5) * 10
        current_alpha = max(0, min(255, int((self.target_alpha + pulse) * fade_in_progress)))
        
        self.surface.set_alpha(current_alpha)
        rect = self.surface.get_rect(center=(logical_width // 2, logical_height // 2))
        surface.blit(self.surface, rect)

class ProceduralBackground:
    def __init__(self):
        self.particles = []
        for _ in range(30):
            self.particles.append(self._spawn_particle())
        
        # Pre-render radial light very large to cover all possible resolutions
        self.light = pygame.Surface((3000, 2000), pygame.SRCALPHA)
        center = (1500, 1000)
        radius = 800
        for i in range(10, 0, -1):
            r = int(radius * (i / 10.0))
            alpha = int(10 * (1.0 - (i / 10.0)))
            pygame.draw.circle(self.light, (*COLORS["warm_glow"], alpha), center, r)

        self.time = 0.0

    def _spawn_particle(self):
        return {
            "x": random.uniform(0, 3000),
            "y": random.uniform(0, 2000),
            "vx": random.uniform(-10, 10),
            "vy": random.uniform(-5, 5),
            "size": random.uniform(1, 3),
            "phase": random.uniform(0, math.pi * 2)
        }

    def update(self, dt: float, logical_width: float = 1280, logical_height: float = 720):
        self.time += dt
        for p in self.particles:
            p["x"] += (p["vx"] + math.sin(self.time + p["phase"]) * 10) * dt
            p["y"] += (p["vy"] + math.cos(self.time * 0.5 + p["phase"]) * 5) * dt
            
            # Wrap around
            if p["x"] < 0: p["x"] = logical_width
            elif p["x"] > logical_width: p["x"] = 0
            if p["y"] < 0: p["y"] = logical_height
            elif p["y"] > logical_height: p["y"] = 0

    def draw(self, surface: pygame.Surface, fade_in_progress: float, logical_width: float, logical_height: float):
        surface.fill(COLORS["charcoal"])
        
        self.light.set_alpha(int(255 * fade_in_progress))
        light_rect = self.light.get_rect(center=(logical_width // 2, logical_height // 2))
        surface.blit(self.light, light_rect)
        
        # Draw dust particles
        for p in self.particles:
            alpha = max(0, min(255, int((100 + math.sin(self.time * 2 + p["phase"]) * 50) * fade_in_progress)))
            color = (*COLORS["gold"], alpha)
            psurf = pygame.Surface((int(p["size"]*2), int(p["size"]*2)), pygame.SRCALPHA)
            pygame.draw.circle(psurf, color, (int(p["size"]), int(p["size"])), int(p["size"]))
            surface.blit(psurf, (int(p["x"]), int(p["y"])))
