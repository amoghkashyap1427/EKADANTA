import pygame
import sys
import asyncio
from src.settings import LOGICAL_WIDTH, LOGICAL_HEIGHT, WINDOW_TITLE, FPS, ASSETS_DIR, SAVES_DIR
from src.systems.scene_manager import SceneManager
from src.systems.audio_manager import AudioManager
from src.systems.save_manager import SaveManager
from src.scenes.main_menu import MainMenuScene

class Game:
    def __init__(self, window):
        pygame.mixer.init()
        
        self.logical_width = LOGICAL_WIDTH
        self.logical_height = LOGICAL_HEIGHT
        
        self.window = window
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Initial resize to match current window size
        self._update_resolution(self.window.get_size())
        
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
                # Video resize dynamically updates the logical width to maintain the fixed height
                self._update_resolution((event.w, event.h))
            self.scene_manager.handle_event(event)


    def update(self, dt):
        self.scene_manager.update(dt)

    def draw(self):
        self.scene_manager.draw(self.render_surface)
        
        window_size = self.window.get_size()
        
        # Calculate aspect-preserving scale to fill the window completely (envelope strategy).
        # We ensure no stretching occurs.
        target_aspect = window_size[0] / window_size[1] if window_size[1] > 0 else 1
        
        # We already adjusted logical_width to match aspect, so they should be proportional.
        # But just in case, we do a pure proportional scale.
        scale = window_size[1] / self.logical_height
        
        new_width = int(self.logical_width * scale)
        new_height = int(self.logical_height * scale)
        
        scaled_surface = pygame.transform.smoothscale(self.render_surface, (new_width, new_height))
        
        # Center if there's any tiny rounding error, but it should perfectly fit
        offset_x = (window_size[0] - new_width) // 2
        offset_y = (window_size[1] - new_height) // 2
        
        self.window.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()

    def _update_resolution(self, size):
        if size[1] <= 0: return
        aspect = size[0] / size[1]
        
        # Keep height fixed at LOGICAL_HEIGHT (720), expand/shrink width
        self.logical_height = LOGICAL_HEIGHT
        self.logical_width = max(800, int(self.logical_height * aspect)) # Prevent it from getting too narrow
        
        # Recreate render surface
        self.render_surface = pygame.Surface((self.logical_width, self.logical_height))
        
    def get_logical_mouse(self, mouse_pos):
        window_size = self.window.get_size()
        if window_size[0] == 0 or window_size[1] == 0: return (0, 0)
        
        scale_x = self.logical_width / window_size[0]
        scale_y = self.logical_height / window_size[1]
        
        return (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

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
