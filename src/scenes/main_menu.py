import pygame
from src.scenes.base_scene import BaseScene
from src.utils.helpers import load_font
from src.settings import COLORS, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.ui.components import Button
from src.ui.effects import Diya, ProceduralBackground, GaneshaSilhouette

class MainMenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        
        self.font_title = load_font(None, 100)
        self.font_subtitle = load_font(None, 40)
        self.font_button = load_font(None, 36)
        
        self.bg = ProceduralBackground()
        self.silhouette = GaneshaSilhouette()
        
        # Diyas at the bottom corners
        self.diyas = [
            Diya(150, LOGICAL_HEIGHT - 100),
            Diya(LOGICAL_WIDTH - 150, LOGICAL_HEIGHT - 100)
        ]
        
        # Check save progress
        has_save = len(self.game.save_manager.data.get("completed_chapters", [])) > 0 or \
                   self.game.save_manager.data.get("current_chapter", 0) > 0
                   
        self.buttons = []
        start_y = LOGICAL_HEIGHT // 2 + 50
        spacing = 50
        
        menu_items = [
            ("BEGIN THE JOURNEY", self._action_begin),
            ("CONTINUE", self._action_continue),
            ("HOW TO PLAY", self._action_how_to_play),
            ("SETTINGS", self._action_settings),
            ("CREDITS", self._action_credits),
            ("QUIT", self._action_quit)
        ]
        
        for i, (text, action) in enumerate(menu_items):
            disabled = (text == "CONTINUE" and not has_save)
            btn = Button(text, self.font_button, LOGICAL_WIDTH // 2, start_y + i * spacing, action, disabled)
            self.buttons.append(btn)
            
        self.focused_index = 0
        if self.buttons[0].disabled:
            self._move_focus(1)
            
        # Animation State
        # 0: BG -> 1: Silhouette -> 2: Title -> 3: Subtitle -> 4: Buttons
        self.anim_time = 0.0
        
        # Pre-render text
        self.title_text = self.font_title.render("EKADANTA", True, COLORS["ivory"])
        self.title_rect = self.title_text.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2 - 150))
        
        self.subtitle_text = self.font_subtitle.render("Where every obstacle becomes a story.", True, COLORS["muted_gold"])
        self.subtitle_rect = self.subtitle_text.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2 - 60))

    def _move_focus(self, direction):
        original = self.focused_index
        self.focused_index = (self.focused_index + direction) % len(self.buttons)
        # Skip disabled
        while self.buttons[self.focused_index].disabled:
            self.focused_index = (self.focused_index + direction) % len(self.buttons)
            if self.focused_index == original:
                break
        
        # Play hover sound if we wanted
        # self.game.audio_manager.play_sfx("hover.wav")

    def handle_event(self, event: pygame.event.Event):
        if self.anim_time < 3.0: # Ignore inputs during intro
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._move_focus(-1)
            elif event.key == pygame.K_DOWN:
                self._move_focus(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                btn = self.buttons[self.focused_index]
                if not btn.disabled and btn.action:
                    # self.game.audio_manager.play_sfx("select.wav")
                    btn.action()
            elif event.key == pygame.K_ESCAPE:
                self._action_quit()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # We need to scale mouse pos to logical pos
                # Actually, for simplicity and robustness in Pybag later, 
                # calculating logical mouse pos depends on window scaling.
                # Let's approximate logical pos:
                logical_mouse = self.game.get_logical_mouse()
                
                for i, btn in enumerate(self.buttons):
                    if btn.rect.collidepoint(logical_mouse) and not btn.disabled:
                        self.focused_index = i
                        if btn.action:
                            # self.game.audio_manager.play_sfx("select.wav")
                            btn.action()

    def _action_begin(self):
        from src.scenes.story_intro import StoryIntroScene
        self.game.scene_manager.change_scene(StoryIntroScene(self.game))

    def _action_continue(self):
        from src.scenes.kailash_world import KailashWorldScene
        self.game.scene_manager.change_scene(KailashWorldScene(self.game))

    def _action_how_to_play(self):
        from src.scenes.how_to_play import HowToPlayScene
        self.game.scene_manager.change_scene(HowToPlayScene(self.game))

    def _action_settings(self):
        from src.scenes.settings import SettingsScene
        self.game.scene_manager.change_scene(SettingsScene(self.game))

    def _action_credits(self):
        from src.scenes.credits import CreditsScene
        self.game.scene_manager.change_scene(CreditsScene(self.game))

    def _action_quit(self):
        self.game.running = False

    def update(self, dt: float):
        self.anim_time += dt
        self.bg.update(dt)
        self.silhouette.update(dt)
        
        for diya in self.diyas:
            diya.update(dt)
            
        # Get logical mouse pos
        logical_mouse = self.game.get_logical_mouse()
        
        # Update buttons
        btn_anim_start = 2.0
        if self.anim_time > btn_anim_start:
            # Prevent mouse hover from overriding keyboard focus if mouse isn't moving
            # (Simplified approach: just pass focused state)
            for i, btn in enumerate(self.buttons):
                btn.update(dt, logical_mouse, i == self.focused_index)

    def draw(self, surface: pygame.Surface):
        # 1. Background
        bg_alpha = min(1.0, self.anim_time / 1.0)
        self.bg.draw(surface, bg_alpha)
        
        # 2. Silhouette
        sil_alpha = min(1.0, max(0.0, (self.anim_time - 0.5) / 1.0))
        self.silhouette.draw(surface, sil_alpha)
        
        # 3. Diyas
        if self.anim_time > 1.0:
            for diya in self.diyas:
                diya.draw(surface)
        
        # 4. Title
        if self.anim_time > 1.0:
            title_alpha = min(255, max(0, int((self.anim_time - 1.0) * 255)))
            self.title_text.set_alpha(title_alpha)
            surface.blit(self.title_text, self.title_rect)
            
        # 5. Subtitle
        if self.anim_time > 1.5:
            sub_alpha = min(255, max(0, int((self.anim_time - 1.5) * 255)))
            self.subtitle_text.set_alpha(sub_alpha)
            surface.blit(self.subtitle_text, self.subtitle_rect)
            
        # 6. Buttons
        if self.anim_time > 2.0:
            for i, btn in enumerate(self.buttons):
                # Staggered fade in
                delay = 2.0 + (i * 0.1)
                if self.anim_time > delay:
                    btn_alpha = min(255, max(0, int((self.anim_time - delay) * 255 * 2)))
                    btn.text_surface.set_alpha(btn_alpha)
                    btn.draw(surface)
