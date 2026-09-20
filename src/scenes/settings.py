import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS
from src.ui.components import Button

class SettingsScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = load_font(None, 60)
        self.font_text = load_font(None, 36)
        
        self.title_surf = self.font_title.render("SETTINGS", True, COLORS["ivory"])
        self.text_surf = self.font_text.render("Settings will be available soon.", True, COLORS["muted_gold"])
        
        self.title_rect = self.title_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2 - 50))
        self.text_rect = self.text_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2 + 20))
        
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
        
        # Reposition dynamically
        lw = self.game.logical_width
        lh = self.game.logical_height
        
        self.title_rect.center = (lw // 2, lh // 2 - 50)
        self.text_rect.center = (lw // 2, lh // 2 + 20)
        self.back_btn.rect.centerx = lw // 2
        self.back_btn.rect.centery = lh - 100
        
        mouse_pos = pygame.mouse.get_pos()
        logical_mouse = self.game.get_logical_mouse(mouse_pos)
        self.back_btn.update(dt, logical_mouse, is_focused=True)

    def draw(self, surface: pygame.Surface):
        surface.fill(COLORS["charcoal"])
        
        alpha = min(255, int(self.anim_time * 255))
        
        self.title_surf.set_alpha(alpha)
        self.text_surf.set_alpha(alpha)
        self.back_btn.text_surface.set_alpha(alpha)
        
        surface.blit(self.title_surf, self.title_rect)
        surface.blit(self.text_surf, self.text_rect)
        self.back_btn.draw(surface)
