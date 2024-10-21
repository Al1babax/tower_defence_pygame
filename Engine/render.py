import pygame
from Engine.level import Level

"""
Class to render the game to the screen
"""


class Render:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tower Defense")

    def update(self, level_object: Level) -> bool:
        # Update the screen
        self.screen.fill((0, 0, 0))

        return False

    def close_window(self):
        pygame.quit()
