import pygame


class Camera:
    def __init__(self, width: float, height: float):
        self.camera_rect = pygame.Rect(0, 0, 1280, 720)
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        
        # Shake/offset for future polish
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.shake_duration = 0.0
        self.shake_intensity = 0.0

    def add_shake(self, intensity: float, duration: float):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)

    def update(self, target, dt: float, logical_width: float = 1280, logical_height: float = 720):
        # Desired position (center target)
        target_x = target.x - logical_width / 2
        target_y = target.y - logical_height / 2
        
        # Clamp to world bounds
        target_x = max(0, min(self.width - logical_width, target_x))
        target_y = max(0, min(self.height - logical_height, target_y))
        
        # Smooth interpolation (lerp)
        lerp_speed = 5.0 * dt
        self.x += (target_x - self.x) * lerp_speed
        self.y += (target_y - self.y) * lerp_speed
        
        # Shake logic
        if self.shake_duration > 0:
            self.shake_duration -= dt
            # Random offset
            import random
            self.offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
            self.offset_x = 0.0
            self.offset_y = 0.0
            
        self.camera_rect = pygame.Rect(int(self.x + self.offset_x), int(self.y + self.offset_y), int(logical_width), int(logical_height))
