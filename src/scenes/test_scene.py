import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS

class BootScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = load_font(None, 74)
        self.font_subtitle = load_font(None, 36)
        self.font_info = load_font(None, 24)
        
        self.title_text = self.font_title.render("EKADANTA", True, COLORS["saffron"])
        self.subtitle_text = self.font_subtitle.render("THE STORY OF GANESHA", True, COLORS["gold"])
        self.info_text = self.font_info.render("FOUNDATION BUILD", True, COLORS["white"])
        
        self.title_rect = self.title_text.get_rect(center=(self.game.logical_width//2, self.game.logical_height//2 - 50))
        self.subtitle_rect = self.subtitle_text.get_rect(center=(self.game.logical_width//2, self.game.logical_height//2 + 20))
        self.info_rect = self.info_text.get_rect(center=(self.game.logical_width//2, self.game.logical_height//2 + 100))

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        lw = self.game.logical_width
        lh = self.game.logical_height
        self.title_rect.center = (lw//2, lh//2 - 50)
        self.subtitle_rect.center = (lw//2, lh//2 + 20)
        self.info_rect.center = (lw//2, lh//2 + 100)

    def draw(self, surface: pygame.Surface):
        surface.fill(COLORS["charcoal"])
        surface.blit(self.title_text, self.title_rect)
        surface.blit(self.subtitle_text, self.subtitle_rect)
        surface.blit(self.info_text, self.info_rect)
