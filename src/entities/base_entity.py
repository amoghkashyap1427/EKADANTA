import pygame

class BaseEntity:
    def __init__(self, x: float, y: float, name: str = "Entity"):
        self.x = x
        self.y = y
        self.name = name
        self.active = True

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface, camera):
        pass
