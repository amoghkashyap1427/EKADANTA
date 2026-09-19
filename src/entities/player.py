import pygame
import math
import random
from src.entities.base_entity import BaseEntity
from src.settings import COLORS

class Player(BaseEntity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Ganesha")
        self.speed = 200.0
        self.vx = 0.0
        self.vy = 0.0
        
        self.time = 0.0
        self.is_moving = False
        self.facing_right = True
        
        # Divine Strike logic
        self.strike_cooldown = 0.0
        self.strike_anticipation = 0.0
        self.strike_duration = 0.0
        self.strike_particles = []
        
        # Health & damage logic
        self.health = 3
        self.invulnerable_timer = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.flash_timer = 0.0
        
        self.strike_hitbox = None # (x, y, radius)
        
        # Dash mechanic
        self.dash_cooldown = 0.0
        self.dash_timer = 0.0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0
        self.dash_trail = [] # list of dicts
        
        # Chapter 3 properties
        self.is_reborn = False
        self.pulse_cooldown = 0.0
        self.pulse_timer = 0.0
        self.pulse_particles = []
        
        self._build_surfaces()

    def _build_surfaces(self):
        # Build a procedural Ganesha player sprite
        self.surf_right = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.surf_left = pygame.Surface((60, 80), pygame.SRCALPHA)
        
        # Right facing
        # Shadow
        pygame.draw.ellipse(self.surf_right, (0, 0, 0, 100), (10, 65, 40, 15))
        # Body
        pygame.draw.ellipse(self.surf_right, COLORS["saffron"], (15, 30, 30, 40))
        # Head
        pygame.draw.circle(self.surf_right, COLORS["saffron"], (30, 25), 18)
        # Trunk (facing right)
        pygame.draw.polygon(self.surf_right, COLORS["saffron"], [(35, 25), (45, 25), (40, 45), (32, 50), (32, 40)])
        # Ear
        pygame.draw.ellipse(self.surf_right, COLORS["saffron"], (12, 15, 12, 20))
        # Crown
        pygame.draw.polygon(self.surf_right, COLORS["gold"], [(20, 10), (40, 10), (30, 0)])
        
        # Left facing (flip horizontal)
        self.surf_left = pygame.transform.flip(self.surf_right, True, False)
        
        # --- REBORN SURFACES ---
        self.reborn_right = pygame.Surface((70, 90), pygame.SRCALPHA)
        self.reborn_left = pygame.Surface((70, 90), pygame.SRCALPHA)
        
        # Shadow
        pygame.draw.ellipse(self.reborn_right, (0, 0, 0, 100), (15, 75, 40, 15))
        # Body (childlike)
        pygame.draw.ellipse(self.reborn_right, COLORS["saffron"], (20, 40, 30, 35))
        # Clothing accent (Dhoti style)
        pygame.draw.ellipse(self.reborn_right, COLORS["gold"], (20, 60, 30, 15))
        # Head (Elephant)
        pygame.draw.circle(self.reborn_right, COLORS["saffron"], (35, 30), 20)
        # Big ear
        pygame.draw.ellipse(self.reborn_right, COLORS["saffron"], (12, 18, 16, 25))
        pygame.draw.ellipse(self.reborn_right, COLORS["warm_glow"], (14, 20, 12, 21)) # Inner ear
        # Trunk (curved)
        pygame.draw.polygon(self.reborn_right, COLORS["saffron"], [(45, 30), (55, 30), (50, 50), (45, 55), (40, 50), (40, 40)])
        # Gentle eye
        pygame.draw.circle(self.reborn_right, COLORS["ivory"], (42, 25), 3)
        pygame.draw.circle(self.reborn_right, (0, 0, 0), (43, 25), 1)
        # Crown
        pygame.draw.polygon(self.reborn_right, COLORS["gold"], [(25, 12), (45, 12), (35, 0)])
        
        self.reborn_left = pygame.transform.flip(self.reborn_right, True, False)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.is_reborn and self.pulse_cooldown <= 0:
                    self._execute_divine_pulse()
                elif not self.is_reborn and self.strike_cooldown <= 0.0 and self.strike_duration <= 0.0 and self.strike_anticipation <= 0.0:
                    self._prepare_divine_strike()
            elif (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT) and self.dash_cooldown <= 0.0 and self.dash_timer <= 0.0:
                self._execute_dash()

    def _execute_dash(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        
        if dx == 0 and dy == 0:
            dx = 1 if self.facing_right else -1
            
        length = math.hypot(dx, dy)
        self.dash_dir_x = dx / length
        self.dash_dir_y = dy / length
        
        self.dash_timer = 0.25 # 0.25s dash
        self.dash_cooldown = 1.0 # 1s cooldown
        self.invulnerable_timer = max(self.invulnerable_timer, 0.3) # I-frames during dash
        self.dash_trail = []

    def _prepare_divine_strike(self):
        self.strike_anticipation = 0.15 # 0.15s windup
        self.strike_cooldown = 0.8
        self.vx = 0.0
        self.vy = 0.0

    def _execute_divine_pulse(self):
        self.pulse_cooldown = 1.5
        self.pulse_timer = 0.5
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.pulse_particles.append({
                "x": self.x,
                "y": self.y - 20,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.5, 1.0),
                "max_life": 1.0
            })
            
    def _execute_divine_strike(self):
        self.strike_duration = 0.2
        
        # Spawn particles
        dir_x = 1 if self.facing_right else -1
        for _ in range(20):
            self.strike_particles.append({
                "x": self.x + dir_x * 20,
                "y": self.y - 40,
                "vx": dir_x * random.uniform(100, 300) + random.uniform(-50, 50),
                "vy": random.uniform(-100, 100),
                "life": random.uniform(0.2, 0.5),
                "max_life": 0.5
            })
            
        # Define hitbox for the scene to check collisions
        self.strike_hitbox = (self.x + dir_x * 40, self.y - 20, 50.0)

    def hurt(self, dx: float, dy: float):
        if self.invulnerable_timer > 0.0:
            return False
            
        self.health -= 1
        self.invulnerable_timer = 1.0
        self.flash_timer = 0.2
        
        self.knockback_vx = dx * 400.0
        self.knockback_vy = dy * 400.0
        
        # Cancel any ongoing attack
        self.strike_anticipation = 0.0
        self.strike_duration = 0.0
        self.strike_hitbox = None
        
        return True

    def update(self, dt: float):
        self.time += dt
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        
        # Pulse logic
        if self.pulse_cooldown > 0:
            self.pulse_cooldown -= dt
        if self.pulse_timer > 0:
            self.pulse_timer -= dt
            
        for p in self.pulse_particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.pulse_particles.remove(p)

        # Combat cooldowns
        if self.strike_cooldown > 0:
            self.strike_cooldown -= dt
            
        if self.strike_anticipation > 0:
            self.strike_anticipation -= dt
            if self.strike_anticipation <= 0:
                self._execute_divine_strike()
                
        if self.strike_duration > 0:
            self.strike_duration -= dt
            if self.strike_duration <= 0:
                self.strike_hitbox = None
                
        # Update strike particles
        for p in self.strike_particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.strike_particles.remove(p)
                
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
            
        for t in self.dash_trail[:]:
            t["life"] -= dt
            if t["life"] <= 0:
                self.dash_trail.remove(t)
                
        if self.dash_timer > 0:
            self.dash_timer -= dt
            self.x += self.dash_dir_x * 600 * dt
            self.y += self.dash_dir_y * 600 * dt
            
            # Add to trail occasionally
            if random.random() > 0.3:
                self.dash_trail.append({"x": self.x, "y": self.y, "life": 0.2, "max_life": 0.2, "facing_right": self.facing_right})
            
            self.is_moving = True
            return # Skip normal movement during dash
                
        # Movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        
        # Normalize
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            
        self.vx = dx * self.speed
        self.vy = dy * self.speed
        
        self.is_moving = (self.vx != 0 or self.vy != 0)
        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False
        
        # Knockback overrides movement
        if abs(self.knockback_vx) > 10 or abs(self.knockback_vy) > 10:
            self.x += self.knockback_vx * dt
            self.y += self.knockback_vy * dt
            self.knockback_vx *= 0.9
            self.knockback_vy *= 0.9
            self.is_moving = False
        else:
            # Apply movement (Strike anticipation/duration halts movement)
            if self.strike_duration <= 0 and self.strike_anticipation <= 0:
                self.x += self.vx * dt
                self.y += self.vy * dt

    def draw(self, surface: pygame.Surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Draw Dash Trail
        for t in self.dash_trail:
            alpha = max(0, min(255, int(150 * (t["life"] / t["max_life"]))))
            t_surf = self.surf_right.copy() if t["facing_right"] else self.surf_left.copy()
            # Golden tint
            t_surf.fill((255, 200, 50, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            t_rect = t_surf.get_rect(midbottom=(t["x"] - camera.x, t["y"] - camera.y))
            surface.blit(t_surf, t_rect)
        
        # Draw Strike Particles
        for p in self.strike_particles:
            alpha = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
            pygame.draw.circle(surface, (*COLORS["gold"], alpha), (int(p["x"] - camera.x), int(p["y"] - camera.y)), 3)
            
        # Draw Strike Arc
        if self.strike_duration > 0:
            arc_radius = 60
            arc_surf = pygame.Surface((arc_radius*2, arc_radius*2), pygame.SRCALPHA)
            dir_mod = 1 if self.facing_right else -1
            # Draw a crescent arc
            rect = arc_surf.get_rect()
            start_angle = -math.pi/4 if self.facing_right else math.pi - math.pi/4
            end_angle = math.pi/4 if self.facing_right else math.pi + math.pi/4
            
            alpha = max(0, min(255, int(255 * (self.strike_duration / 0.2))))
            pygame.draw.arc(arc_surf, (*COLORS["warm_glow"], alpha), rect, start_angle, end_angle, 10)
            
            arc_x = screen_x + (30 * dir_mod)
            arc_y = screen_y - 40
            surface.blit(arc_surf, arc_surf.get_rect(center=(arc_x, arc_y)))

        # Draw Pulse
        if self.pulse_timer > 0:
            radius = int((0.5 - self.pulse_timer) * 300)
            alpha = int((self.pulse_timer / 0.5) * 150)
            if radius > 0:
                pygame.draw.circle(surface, (*COLORS["gold"], alpha), (int(screen_x), int(screen_y - 20)), radius, 2)
        
        for p in self.pulse_particles:
            alpha = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
            pygame.draw.circle(surface, (*COLORS["gold"], alpha), (int(p["x"] - camera.x), int(p["y"] - camera.y)), 4)
            
        # Choose sprite
        if self.is_reborn:
            surf = self.reborn_right if self.facing_right else self.reborn_left
        else:
            surf = self.surf_right if self.facing_right else self.surf_left
        
        # Walk bobbing
        y_offset = 0
        if self.is_moving:
            y_offset = abs(math.sin(self.time * 15.0)) * 5
        elif self.strike_anticipation > 0:
            y_offset = -5 # Crunch down
        else:
            # Idle breathing
            y_offset = math.sin(self.time * 2.0) * 2
            
        rect = surf.get_rect(midbottom=(screen_x, screen_y - y_offset))
        
        # Flash / i-frame blinking
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((60, 80), pygame.SRCALPHA)
            flash_surf.fill((255, 200, 200, 150)) # Crimson/white tint
            surf = surf.copy()
            surf.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(surf, rect)
        elif self.invulnerable_timer > 0:
            # Blink if invulnerable
            if int(self.time * 10) % 2 == 0:
                surface.blit(surf, rect)
        else:
            surface.blit(surf, rect)
