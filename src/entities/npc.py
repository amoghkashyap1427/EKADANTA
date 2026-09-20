import pygame
import math
from src.entities.interactive_object import InteractiveObject
from src.settings import COLORS

class NPC(InteractiveObject):
    def __init__(self, x: float, y: float, name: str, dialogues: list[tuple[str, str]]):
        super().__init__(x, y, name, interaction_range=100.0)
        self.dialogues = dialogues
        
        # Pre-render a simple procedural representation of Parvati
        self.surface = pygame.Surface((60, 100), pygame.SRCALPHA)
        self._draw_procedural_npc()
        
    def _draw_procedural_npc(self):
        # Simple elegant silhouette
        # Base shadow
        pygame.draw.ellipse(self.surface, (20, 10, 10, 100), (10, 80, 40, 20))
        # Body (Saree colors)
        pygame.draw.polygon(self.surface, COLORS["crimson"], [(30, 20), (50, 90), (10, 90)])
        pygame.draw.polygon(self.surface, COLORS["muted_gold"], [(30, 20), (45, 90), (15, 90)], 2)
        # Head
        pygame.draw.circle(self.surface, COLORS["saffron"], (30, 20), 15)
        # Halo
        pygame.draw.circle(self.surface, (*COLORS["warm_glow"], 100), (30, 20), 25, 2)
        
    def interact(self, game):
        # Trigger dialogue manager
        from src.scenes.kailash_world import KailashWorldScene
        if isinstance(game.scene_manager.current_scene, KailashWorldScene):
            game.scene_manager.current_scene.dialogue_manager.start_dialogue(self.dialogues)

    def draw(self, surface: pygame.Surface, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        
        # Draw breathing animation
        scale = 1.0 + math.sin(self.time * 2.0) * 0.02
        scaled_surf = pygame.transform.smoothscale(
            self.surface, 
            (int(self.surface.get_width() * scale), int(self.surface.get_height() * scale))
        )
        
        rect = scaled_surf.get_rect(midbottom=(screen_x, screen_y))
        surface.blit(scaled_surf, rect)
