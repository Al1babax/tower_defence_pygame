"""
Engine class that binds all the modules of the engine
"""
from Engine.game import Game
from Engine.render import Render
from pygame import time


class Engine:
    def __init__(self):
        self.game = Game()
        self.render = Render()
        self.clock = time.Clock()

    def run(self):
        while self.game.game_running:
            print(self.game.game_running)
            # Update loop to run the game
            self.game.update()
            return_package: dict = self.render.update(self.game.level)

            if return_package["game_over"] is True:
                self.game.game_running = False

            # Deal with the package and check up all the evens

            # Create tick rate
            self.clock.tick(60)

        # Cleanup
        self.render.close_window()
