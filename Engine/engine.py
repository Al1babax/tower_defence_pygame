"""
Engine class that binds all the modules of the engine
"""
from game import Game
from render import Render

class Engine:

    def __init__(self):
        game = Game()
        render = Render()

    def run(self):
        while True:
            # Update loop to run the game
            self.game.update()
            self.render.update(self.game.state)