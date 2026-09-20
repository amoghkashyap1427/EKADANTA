import sys
import asyncio
from pathlib import Path

# Ensure src is in the path
sys.path.append(str(Path(__file__).parent))

from src.game import Game

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
