"""
Global configuration and settings.
"""
import os
import sys
from pathlib import Path

# Window settings
LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 720
WINDOW_TITLE = "EKADANTA — The Story of Ganesha"
FPS = 60

# Colors (RGB)
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "saffron": (255, 153, 51),
    "charcoal": (30, 30, 30),
    "gold": (255, 215, 0),
    "dark_brown": (60, 40, 20),
    "ivory": (255, 255, 240),
    "muted_gold": (200, 170, 70),
    "crimson": (150, 20, 20),
    "warm_glow": (255, 200, 100)
}

# Directories
if sys.platform == "emscripten":
    BASE_DIR = Path(".")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
SAVES_DIR = BASE_DIR / "saves"

# Volumes
DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SFX_VOLUME = 0.7

DEBUG_MODE = True
