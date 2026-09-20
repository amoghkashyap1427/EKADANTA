import pygame
import sys
import asyncio
from src.settings import LOGICAL_WIDTH, LOGICAL_HEIGHT, WINDOW_TITLE, FPS, ASSETS_DIR, SAVES_DIR
from src.systems.scene_manager import SceneManager
from src.systems.audio_manager import AudioManager
from src.systems.save_manager import SaveManager
from src.scenes.main_menu import MainMenuScene

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.logical_width = LOGICAL_WIDTH
        self.logical_height = LOGICAL_HEIGHT
        
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        
        self.render_surface = pygame.Surface((self.logical_width, self.logical_height))
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        try:
            ASSETS_DIR.mkdir(parents=True, exist_ok=True)
            (ASSETS_DIR / "images").mkdir(exist_ok=True)
            (ASSETS_DIR / "audio").mkdir(exist_ok=True)
            (ASSETS_DIR / "fonts").mkdir(exist_ok=True)
            (ASSETS_DIR / "data").mkdir(exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create assets dir (expected in pygbag): {e}")
            
        try:
            SAVES_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create saves dir: {e}")
        
        self.save_manager = SaveManager()
        self.audio_manager = AudioManager()
        
        settings = self.save_manager.data.get("settings", {})
        self.audio_manager.set_music_volume(settings.get("music_volume", 0.5))
        self.audio_manager.set_sfx_volume(settings.get("sfx_volume", 0.7))
        
        self.scene_manager = SceneManager(self)
        
        initial_scene = MainMenuScene(self)
        self.scene_manager.change_scene(initial_scene)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Video resize is handled mostly by the scaling in draw, 
                # but we could respond to it if needed.
                pass
            self.scene_manager.handle_event(event)


    def update(self, dt):
        self.scene_manager.update(dt)


    def get_logical_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        window_w, window_h = self.window.get_size()
        
        scale = min(window_w / self.logical_width, window_h / self.logical_height)
        display_w = int(self.logical_width * scale)
        display_h = int(self.logical_height * scale)
        
        x_offset = (window_w - display_w) // 2
        y_offset = (window_h - display_h) // 2
        
        logical_x = (mouse_x - x_offset) / scale
        logical_y = (mouse_y - y_offset) / scale
        return (int(logical_x), int(logical_y))

    def draw(self):
        self.scene_manager.draw(self.render_surface)
        
        window_w, window_h = self.window.get_size()
        scale = min(window_w / self.logical_width, window_h / self.logical_height)
        display_w = int(self.logical_width * scale)
        display_h = int(self.logical_height * scale)
        
        scaled_surface = pygame.transform.smoothscale(self.render_surface, (display_w, display_h))
        
        x_offset = (window_w - display_w) // 2
        y_offset = (window_h - display_h) // 2
        
        self.window.fill((0, 0, 0))
        self.window.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            await asyncio.sleep(0)
            
        self.quit()
        
    def quit(self):
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()
