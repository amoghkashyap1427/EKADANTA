import asyncio
import pygame
import sys

from src.game import Game

async def main():
    game = Game()
    
    while game.running:
        # 60 FPS is defined in settings, but we can hardcode 60 or import it
        dt = game.clock.tick(60) / 1000.0
        game.handle_events()
        game.update(dt)
        game.draw()
        await asyncio.sleep(0)
        
    game.quit()

if __name__ == "__main__":
    asyncio.run(main())
