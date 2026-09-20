import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.ui.components import Button

class HowToPlayScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = load_font(None, 60)
        self.font_text = load_font(None, 36)
        
        self.instructions = [
            ("EXPLORE", "Discover the world and the stories hidden within it."),
            ("INTERACT", "Talk, observe and make choices."),
            ("ACT", "Face obstacles through light action and skill."),
            ("REMEMBER", "Your actions shape how the story unfolds.")
        ]
        
        self.rendered_instructions = []
        for title, text in self.instructions:
            t_surf = self.font_title.render(title, True, COLORS["saffron"])
            d_surf = self.font_text.render(text, True, COLORS["ivory"])
            self.rendered_instructions.append((t_surf, d_surf))
            
        self.back_btn = Button("BACK", self.font_text, LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 80, self._action_back)
        self.anim_time = 0.0

    def _action_back(self):
        from src.scenes.main_menu import MainMenuScene
        self.game.scene_manager.change_scene(MainMenuScene(self.game))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN):
            self._action_back()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            logical_mouse = self.game.get_logical_mouse()
            if self.back_btn.rect.collidepoint(logical_mouse):
                self._action_back()

    def update(self, dt: float):
        self.anim_time += dt
        logical_mouse = self.game.get_logical_mouse()
        self.back_btn.update(dt, logical_mouse, is_focused=True)

    def draw(self, surface: pygame.Surface):
        surface.fill(COLORS["charcoal"])
        
        alpha = min(255, int(self.anim_time * 255))
        
        start_y = 100
        spacing = 110
        for i, (t_surf, d_surf) in enumerate(self.rendered_instructions):
            t_surf.set_alpha(alpha)
            d_surf.set_alpha(alpha)
            
            t_rect = t_surf.get_rect(center=(LOGICAL_WIDTH // 2, start_y + i * spacing))
            d_rect = d_surf.get_rect(center=(LOGICAL_WIDTH // 2, start_y + i * spacing + 40))
            
            surface.blit(t_surf, t_rect)
            surface.blit(d_surf, d_rect)
            
        self.back_btn.text_surface.set_alpha(alpha)
        self.back_btn.draw(surface)
