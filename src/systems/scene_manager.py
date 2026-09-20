import pygame

class SceneManager:
    def __init__(self, game):
        self.game = game
        self.current_scene = None
        
        # Transition state
        self.transitioning = False
        self.transition_alpha = 0
        self.transition_speed = 510 # Complete full 255 alpha in 0.5s
        self.transition_surface = pygame.Surface((game.logical_width, game.logical_height))
        self.transition_surface.fill((0, 0, 0))
        self.next_scene = None
        self.fade_state = "none" # "out", "in", "none"

    def change_scene(self, scene):
        """Start a transition to a new scene."""
        if self.current_scene is None:
            self._switch(scene)
        else:
            self.next_scene = scene
            self.transitioning = True
            self.fade_state = "out"
            self.transition_alpha = 0

    def _switch(self, scene):
        if self.current_scene:
            self.current_scene.exit()
        self.current_scene = scene
        if self.current_scene:
            self.current_scene.enter()

    def handle_event(self, event: pygame.event.Event):
        if self.transitioning:
            return
            
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt: float):
        if self.transitioning:
            if self.fade_state == "out":
                self.transition_alpha += self.transition_speed * dt
                if self.transition_alpha >= 255:
                    self.transition_alpha = 255
                    self._switch(self.next_scene)
                    self.next_scene = None
                    self.fade_state = "in"
            elif self.fade_state == "in":
                self.transition_alpha -= self.transition_speed * dt
                if self.transition_alpha <= 0:
                    self.transition_alpha = 0
                    self.transitioning = False
                    self.fade_state = "none"
        
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, surface: pygame.Surface):
        if self.current_scene:
            self.current_scene.draw(surface)
            
        if self.transitioning:
            self.transition_surface.set_alpha(int(self.transition_alpha))
            surface.blit(self.transition_surface, (0, 0))
