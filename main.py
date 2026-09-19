import sys
from pathlib import Path

# Ensure src is in the path
sys.path.append(str(Path(__file__).parent))

from src.game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
