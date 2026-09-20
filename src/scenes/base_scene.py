import pygame

class BaseScene:
    def __init__(self, game):
        self.game = game

    def enter(self):
        """Called when this scene becomes the active scene."""
        pass

    def exit(self):
        """Called when this scene is being replaced."""
        pass

    def handle_event(self, event: pygame.event.Event):
        """Process Pygame events."""
        pass

    def update(self, dt: float):
        """Update game logic (dt is time in seconds since last frame)."""
        pass

    def draw(self, surface: pygame.Surface):
        """Render the scene to the given surface."""
        pass
