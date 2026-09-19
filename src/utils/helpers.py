import pygame
from src.settings import ASSETS_DIR

def load_image(filename: str, alpha: bool = True) -> pygame.Surface | None:
    """Load an image safely, returning None if missing."""
    path = ASSETS_DIR / "images" / filename
    try:
        if alpha:
            img = pygame.image.load(str(path)).convert_alpha()
        else:
            img = pygame.image.load(str(path)).convert()
        return img
    except (pygame.error, FileNotFoundError) as e:
        print(f"Warning: Could not load image {filename}: {e}")
        return None

def load_font(filename: str | None, size: int) -> pygame.font.Font:
    """Load a font safely, falling back to default Pygame font if missing."""
    if filename:
        path = ASSETS_DIR / "fonts" / filename
        try:
            return pygame.font.Font(str(path), size)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load font {filename}: {e}")
    return pygame.font.Font(None, size)
