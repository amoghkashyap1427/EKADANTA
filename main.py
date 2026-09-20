import sys
import asyncio

# Ensure src is in the path
sys.path.append(".")

from src.game import Game

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
