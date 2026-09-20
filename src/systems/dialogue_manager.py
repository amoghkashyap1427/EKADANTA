import pygame
from src.settings import COLORS, LOGICAL_WIDTH, LOGICAL_HEIGHT
from src.utils.helpers import load_font

class DialogueManager:
    def __init__(self):
        self.font_speaker = load_font(None, 36)
        self.font_text = load_font(None, 32)
        
        self.active = False
        self.dialogues = [] # list of (speaker, text)
        self.current_index = 0
        
        self.char_index = 0.0
        self.text_speed = 30.0 # chars per second
        self.is_typing = False
        
        self.wait_timer = 0.0
        self.auto_advance = True
        
        self.on_complete = None
        
        # UI Box Dimensions
        self.box_width = LOGICAL_WIDTH - 200
        self.box_height = 180
        self.box_x = 100
        self.box_y = LOGICAL_HEIGHT - self.box_height - 30
        
        # Pre-render parchment bg
        self.bg_surf = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        # Semi-transparent dark brown/charcoal
        self.bg_surf.fill((20, 15, 10, 230))
        # Gold border
        pygame.draw.rect(self.bg_surf, COLORS["muted_gold"], self.bg_surf.get_rect(), 2)
        # Inner thin border
        inner_rect = self.bg_surf.get_rect().inflate(-10, -10)
        pygame.draw.rect(self.bg_surf, (*COLORS["saffron"], 100), inner_rect, 1)

    def start_dialogue(self, dialogues: list[tuple[str, str]], on_complete=None):
        if not dialogues:
            return
        self.dialogues = dialogues
        self.current_index = 0
        self.char_index = 0.0
        self.active = True
        self.is_typing = True
        self.on_complete = on_complete
        self.wait_timer = 0.0

    def _next_line(self):
        self.current_index += 1
        self.char_index = 0.0
        if self.current_index >= len(self.dialogues):
            self.active = False
            if self.on_complete:
                self.on_complete()
        else:
            self.is_typing = True

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
            speaker, text = self.dialogues[self.current_index]
            if self.is_typing:
                # Skip typing
                self.char_index = float(len(text))
                self.is_typing = False
            else:
                # Next line
                self._next_line()
            return True # Event consumed
        return False

    def update(self, dt: float):
        if not self.active:
            return
            
        if self.is_typing:
            speaker, text = self.dialogues[self.current_index]
            self.char_index += self.text_speed * dt
            if self.char_index >= len(text):
                self.char_index = float(len(text))
                self.is_typing = False
                self.wait_timer = 0.0
        elif self.auto_advance:
            self.wait_timer += dt
            speaker, text = self.dialogues[self.current_index]
            # Use ~2.5s for normal, 3.0s for long/important
            delay = 3.0 if len(text) > 40 else 2.5
            if self.wait_timer > delay:
                self._next_line()

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
            
        # Draw box
        surface.blit(self.bg_surf, (self.box_x, self.box_y))
        
        speaker, text = self.dialogues[self.current_index]
        current_text = text[:int(self.char_index)]
        
        # Render speaker
        speaker_surf = self.font_speaker.render(speaker, True, COLORS["saffron"])
        surface.blit(speaker_surf, (self.box_x + 30, self.box_y + 20))
        
        # Render text (simple word wrap or single line for now)
        text_surf = self.font_text.render(current_text, True, COLORS["ivory"])
        surface.blit(text_surf, (self.box_x + 30, self.box_y + 70))
        
        # Draw indicator if waiting for input
        if not self.is_typing:
            indicator = self.font_text.render("▼", True, COLORS["gold"])
            # simple bounce
            import math
            import time
            bounce = math.sin(time.time() * 5) * 5
            surface.blit(indicator, (self.box_x + self.box_width - 40, self.box_y + self.box_height - 40 + bounce))
