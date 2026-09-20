import asyncio
import pygame
import sys
from src.settings import LOGICAL_WIDTH, LOGICAL_HEIGHT

from src.game import Game

async def main():
    pygame.init()
    # Set mode to (0, 0) to request full available window size in Pygbag
    window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    
    game = Game(window)
    
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
