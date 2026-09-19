import pygame
from src.settings import ASSETS_DIR

class AudioManager:
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.current_music = None
    
    def play_music(self, filename: str, loop: int = -1):
        path = ASSETS_DIR / "audio" / filename
        if not path.exists():
            print(f"Warning: Music file {filename} not found.")
            return
        
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loop)
            self.current_music = filename
        except pygame.error as e:
            print(f"Warning: Could not play music {filename}: {e}")
            
    def play_sfx(self, filename: str):
        path = ASSETS_DIR / "audio" / filename
        if not path.exists():
            print(f"Warning: SFX file {filename} not found.")
            return
        
        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(self.sfx_volume)
            sound.play()
        except pygame.error as e:
            print(f"Warning: Could not play SFX {filename}: {e}")

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
