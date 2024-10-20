"""
Engine class that binds all the modules of the engine
"""
from game import Game
from render import Render
from pygame import time


class Engine:
    def __init__(self):
        self.game = Game()
        self.render = Render()
        self.clock = time.Clock()

    def run(self):
        while True:
            # Update loop to run the game
            self.game.update()
            self.render.update(self.game.level.terrain)

            # Create tick rate
            self.clock.tick(60)
