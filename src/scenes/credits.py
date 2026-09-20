import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS
from src.ui.components import Button

class CreditsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = load_font(None, 60)
        self.font_text = load_font(None, 36)
        self.font_small = load_font(None, 24)
        
        self.elements = [
            (self.font_title.render("EKADANTA", True, COLORS["ivory"]), -100),
            (self.font_small.render("THE STORY OF GANESHA", True, COLORS["saffron"]), -50),
            (self.font_text.render("Created for the Ganesh Chaturthi Game Design Contest", True, COLORS["muted_gold"]), 50),
            (self.font_text.render("An interactive story of devotion, courage, wisdom and obstacles.", True, COLORS["white"]), 120),
        ]
        
        self.back_btn = Button("BACK", self.font_text, self.game.logical_width // 2, self.game.logical_height - 100, self._action_back)
        self.anim_time = 0.0

    def _action_back(self):
        from src.scenes.main_menu import MainMenuScene
        self.game.scene_manager.change_scene(MainMenuScene(self.game))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN):
            self._action_back()
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            logical_mouse = self.game.get_logical_mouse(event.pos)
            if self.back_btn.rect.collidepoint(logical_mouse):
                self._action_back()

    def update(self, dt: float):
        self.anim_time += dt
        
        lw = self.game.logical_width
        lh = self.game.logical_height
        
        self.back_btn.rect.centerx = lw // 2
        self.back_btn.rect.centery = lh - 100
        
        mouse_pos = pygame.mouse.get_pos()
        logical_mouse = self.game.get_logical_mouse(mouse_pos)
        
        self.back_btn.update(dt, logical_mouse, is_focused=True)

    def draw(self, surface: pygame.Surface):
        surface.fill(COLORS["charcoal"])
        
        alpha = min(255, int(self.anim_time * 255))
        
        for text_surf, y_offset in self.elements:
            text_surf.set_alpha(alpha)
            rect = text_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2 + y_offset))
            surface.blit(text_surf, rect)
            
        self.back_btn.text_surface.set_alpha(alpha)
        self.back_btn.draw(surface)
