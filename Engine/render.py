import pygame
from level import Level


"""
Class to render the game to the screen
"""

class Render:
    def __init__(self, game_running: bool):
        self.game_running = game_running

    def update(self, level_object: Level):
        # Update the screen
        pass

    def close_window(self):
        self.game_running = False
        pygame.quit()
