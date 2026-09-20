import pygame
import math
import random
from src.entities.base_entity import BaseEntity
from src.settings import COLORS

class Vighna(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Vighna")
        self.health = 4
        self.state = "IDLE"  # IDLE, CHASE, DEFEATED
        self.speed = 80.0
        
        self.time = random.uniform(0, 10.0)
        self.particles = []
        
        self.flash_timer = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        
        self.detection_range = 400.0
        
        self._build_surface()

    def _build_surface(self):
        self.surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        
        # Smoky body
        pygame.draw.circle(self.surface, (20, 20, 25, 200), (25, 25), 20)
        pygame.draw.circle(self.surface, (10, 10, 15, 255), (25, 25), 15)
        
        # Glowing crimson eyes
        pygame.draw.circle(self.surface, COLORS["crimson"], (18, 20), 4)
        pygame.draw.circle(self.surface, COLORS["crimson"], (32, 20), 4)
        
        # Inner glow for eyes
        pygame.draw.circle(self.surface, (255, 100, 100), (18, 20), 2)
        pygame.draw.circle(self.surface, (255, 100, 100), (32, 20), 2)

    def hit(self, dx: float, dy: float):
        if self.state == "DEFEATED":
            return
            
        self.health -= 1
        self.flash_timer = 0.2
        
        if self.health <= 0:
            self.state = "DEFEATED"
            # Spawn dissolve particles
            for _ in range(15):
                self.particles.append({
                    "x": self.x + random.uniform(-20, 20),
                    "y": self.y + random.uniform(-20, 20),
                    "vx": random.uniform(-50, 50),
                    "vy": random.uniform(-100, -20),
                    "life": random.uniform(0.5, 1.5),
                    "max_life": 1.5,
                    "color": COLORS["gold"]
                })
        else:
            # Apply knockback
            self.knockback_vx = dx * 300.0
            self.knockback_vy = dy * 300.0

    def update(self, dt: float, player=None):
        self.time += dt
        
        if self.flash_timer > 0:
            self.flash_timer -= dt
            
        if self.state == "DEFEATED":
            # Update dissolve particles
            for p in self.particles[:]:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["life"] -= dt
                if p["life"] <= 0:
                    self.particles.remove(p)
            
            if len(self.particles) == 0:
                self.active = False
            return
            
        # Spawn ambient smoke particles
        if random.random() < 0.1:
            self.particles.append({
                "x": self.x + random.uniform(-15, 15),
                "y": self.y + random.uniform(-10, 20),
                "vx": random.uniform(-10, 10),
                "vy": random.uniform(-20, -5),
                "life": 1.0,
                "max_life": 1.0,
                "color": (50, 40, 40)
            })
            
        # Update ambient particles
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)
                
        # Knockback friction
        if abs(self.knockback_vx) > 10 or abs(self.knockback_vy) > 10:
            self.x += self.knockback_vx * dt
            self.y += self.knockback_vy * dt
            self.knockback_vx *= 0.9
            self.knockback_vy *= 0.9
            return # Don't move normally while knocked back
            
        if not player:
            return
            
        # AI Logic
        dist = math.hypot(player.x - self.x, player.y - self.y)
        
        if self.state == "IDLE":
            if dist < self.detection_range:
                self.state = "CHASE"
                
        elif self.state == "CHASE":
            if dist > 10.0:
                dx = (player.x - self.x) / dist
                dy = (player.y - self.y) / dist
                
                # Bobbing movement
                bob = math.sin(self.time * 5.0) * 0.5 + 0.5
                actual_speed = self.speed * bob
                
                self.x += dx * actual_speed * dt
                self.y += dy * actual_speed * dt

    def draw(self, surface: pygame.Surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Draw particles (behind if smoke, front if gold dissolve)
        for p in self.particles:
            alpha = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
            color = (*p["color"], alpha)
            psurf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(psurf, color, (2, 2), 2)
            surface.blit(psurf, (int(p["x"] - camera.x), int(p["y"] - camera.y)))
            
        if self.state == "DEFEATED":
            return
            
        # Float bob
        y_offset = math.sin(self.time * 3.0) * 5
        
        # Draw body
        rect = self.surface.get_rect(center=(screen_x, screen_y + y_offset))
        
        if self.flash_timer > 0:
            # Draw white silhouette flash
            flash_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, 200), (25, 25), 20)
            surface.blit(flash_surf, rect)
        else:
            surface.blit(self.surface, rect)
