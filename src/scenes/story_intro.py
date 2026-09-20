import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS

class StoryIntroScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font_chapter = load_font(None, 40)
        self.font_title = load_font(None, 80)
        self.font_location = load_font(None, 36)
        
        self.time = 0.0
        self.stage = 0
        self.transitioning_out = False
        
        self.chapter_surf = self.font_chapter.render("CHAPTER I", True, COLORS["gold"])
        self.title_surf = self.font_title.render("THE CHILD OF PARVATI", True, COLORS["ivory"])
        self.location_surf = self.font_location.render("Mount Kailash", True, COLORS["saffron"])
        
        self.chapter_rect = self.chapter_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2 - 60))
        self.title_rect = self.title_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2))
        self.location_rect = self.location_surf.get_rect(center=(self.game.logical_width // 2, self.game.logical_height // 2 + 60))

    def update(self, dt: float):
        self.time += dt
        if self.time > 5.0 and not self.transitioning_out:
            self.transitioning_out = True
            from src.scenes.kailash_world import KailashWorldScene
            self.game.scene_manager.change_scene(KailashWorldScene(self.game))
            
        lw = self.game.logical_width
        lh = self.game.logical_height
        self.chapter_rect.center = (lw // 2, lh // 2 - 60)
        self.title_rect.center = (lw // 2, lh // 2)
        self.location_rect.center = (lw // 2, lh // 2 + 60)

    def draw(self, surface: pygame.Surface):
        surface.fill(COLORS["black"])
        
        # Simple fade sequence
        # 0-1: Fade in Chapter
        # 1-2: Fade in Title
        # 2-3: Fade in Location
        # 3-4: Hold
        # 4-5: Fade out
        
        if self.time > 0.0:
            alpha_chap = max(0, min(255, int((self.time - 0.0) * 255)))
            if self.time > 4.0:
                alpha_chap = max(0, min(255, int((5.0 - self.time) * 255)))
            self.chapter_surf.set_alpha(alpha_chap)
            surface.blit(self.chapter_surf, self.chapter_rect)
            
        if self.time > 1.0:
            alpha_title = max(0, min(255, int((self.time - 1.0) * 255)))
            if self.time > 4.0:
                alpha_title = max(0, min(255, int((5.0 - self.time) * 255)))
            self.title_surf.set_alpha(alpha_title)
            surface.blit(self.title_surf, self.title_rect)
            
        if self.time > 2.0:
            alpha_loc = max(0, min(255, int((self.time - 2.0) * 255)))
            if self.time > 4.0:
                alpha_loc = max(0, min(255, int((5.0 - self.time) * 255)))
            self.location_surf.set_alpha(alpha_loc)
            surface.blit(self.location_surf, self.location_rect)
