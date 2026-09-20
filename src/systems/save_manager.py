import json
from pathlib import Path
from src.settings import SAVES_DIR

class SaveManager:
    def __init__(self):
        self.saves_dir = SAVES_DIR
        try:
            self.saves_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create saves dir in SaveManager: {e}")
        self.save_file = self.saves_dir / "savegame.json"
        
        self.default_data = {
            "current_chapter": 0,
            "completed_chapters": [],
            "settings": {
                "music_volume": 0.5,
                "sfx_volume": 0.7
            }
        }
        self.data = self.load()

    def load(self) -> dict:
        if self.save_file.exists():
            try:
                with open(self.save_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Save file corrupted. Loading defaults.")
        return self.default_data.copy()

    def save(self):
        try:
            with open(self.save_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")
