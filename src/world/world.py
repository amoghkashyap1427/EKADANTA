import pygame
import math
import random
from src.settings import COLORS

class World:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.entities = []
        self.time = 0.0
        
        self._build_environment()
        self._init_particles()

    def _build_environment(self):
        # Pre-render static world background to save performance
        self.bg_surf = pygame.Surface((self.width, self.height))
        self.bg_surf.fill(COLORS["charcoal"])
        
        # Draw some procedural pathways / ground details
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            w = random.randint(100, 400)
            h = random.randint(50, 150)
            rect = pygame.Rect(x, y, w, h)
            # Subtle stone color
            color = (
                COLORS["charcoal"][0] + random.randint(-5, 10),
                COLORS["charcoal"][1] + random.randint(-5, 5),
                COLORS["charcoal"][2] + random.randint(-5, 5)
            )
            pygame.draw.ellipse(self.bg_surf, color, rect)

        # Draw borders/mountains in bg
        for i in range(10):
            pygame.draw.polygon(self.bg_surf, (20, 20, 25), [
                (i * 300 - 100, 0),
                (i * 300 + 150, -200 + random.randint(0, 100)),
                (i * 300 + 400, 0)
            ])
            
        # Draw some rangoli patterns randomly on the ground
        for _ in range(15):
            cx = random.randint(0, self.width)
            cy = random.randint(0, self.height)
            for r in range(10, 40, 10):
                pygame.draw.circle(self.bg_surf, (*COLORS["saffron"], 30), (cx, cy), r, 2)

    def _init_particles(self):
        self.particles = []
        for _ in range(100):
            self.particles.append({
                "x": random.uniform(0, self.width),
                "y": random.uniform(0, self.height),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(5, 15)
            })

    def add_entity(self, entity):
        self.entities.append(entity)
        
    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self, dt: float):
        self.time += dt
        
        # Update particles (fireflies/dust)
        for p in self.particles:
            p["x"] += math.sin(self.time + p["phase"]) * p["speed"] * dt
            p["y"] += math.cos(self.time * 0.5 + p["phase"]) * (p["speed"] * 0.5) * dt
            # wrap around
            if p["x"] < 0: p["x"] = self.width
            if p["x"] > self.width: p["x"] = 0
            if p["y"] < 0: p["y"] = self.height
            if p["y"] > self.height: p["y"] = 0

        # Sort entities by Y for pseudo-3D depth
        self.entities.sort(key=lambda e: e.y)
        
        for e in self.entities:
            if e.active:
                e.update(dt)

    def draw(self, surface: pygame.Surface, camera, logical_width: float, logical_height: float, darken_factor: float = 0.0):
        # Draw background based on camera
        # Only blit the visible portion
        src_rect = pygame.Rect(int(camera.x), int(camera.y), int(logical_width), int(logical_height))
        # Ensure it doesn't go out of bounds of surface
        src_rect.clamp_ip(self.bg_surf.get_rect())
        
        surface.blit(self.bg_surf, (0, 0), src_rect)
        
        if darken_factor > 0:
            dark_surf = pygame.Surface((int(logical_width), int(logical_height)), pygame.SRCALPHA)
            dark_surf.fill((0, 0, 0, int(150 * darken_factor)))
            surface.blit(dark_surf, (0, 0))
        
        # Draw Entities
        for e in self.entities:
            if e.active:
                # Basic culling
                if (camera.x - 100 <= e.x <= camera.x + logical_width + 100) and \
                   (camera.y - 100 <= e.y <= camera.y + logical_height + 100):
                    e.draw(surface, camera)
                    
        # Draw particles
        for p in self.particles:
            if (camera.x <= p["x"] <= camera.x + logical_width) and \
               (camera.y <= p["y"] <= camera.y + logical_height):
                alpha = max(0, min(255, int(100 + math.sin(self.time * 3 + p["phase"]) * 100)))
                pygame.draw.circle(surface, (*COLORS["gold"], alpha), 
                                  (int(p["x"] - camera.x), int(p["y"] - camera.y)), 2)
                                  
        # Draw UI/prompts of entities last so they appear on top
        for e in self.entities:
            if e.active and hasattr(e, "draw_ui"):
                e.draw_ui(surface, camera)
