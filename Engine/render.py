import pygame
from Engine.level import Level
import time

"""
Class to render the game to the screen
"""

return_package = {
    "game_over": False,
    "new_tower": {
        "position": None,
        "type": None
    },
    "remove_tower": None
}


class Render:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tower Defense")

        self.return_package = return_package

    def update(self, level_object: Level) -> dict:
        self.return_package = return_package

        # Update the screen
        self.screen.fill((0, 0, 0))

        # time.sleep(3)

        # Game over
        # self.return_package["game_over"] = True

        return self.return_package

    def close_window(self):
        pygame.quit()
