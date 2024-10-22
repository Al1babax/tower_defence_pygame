"""
Engine class that binds all the modules of the engine
"""
from Engine.game import Game
from Engine.render import Render
from pygame import time


class Engine:
    def __init__(self):
        self.game = Game()
        # self.render = Render()
        self.clock = time.Clock()

    def print_game(self):
        from Engine.level import TerrainBlock
        from Engine.enemy import Enemy
        for row in self.game.level.terrain:
            for block in row:
                if isinstance(block, TerrainBlock):
                    print(block.block_type, end=" ")
                elif isinstance(block, Enemy):
                    print("E", end=" ")
            print()

        print("\n")

    def run(self):
        while self.game.game_running:
            if self.game.frame % 60 == 0:
                print("Frame: ", self.game.frame)
                self.print_game()

            # Update loop to run the game
            self.game.update()
            # return_package: dict = self.render.update(self.game.level)

            # if return_package["game_over"] is True:
            #     self.game.game_running = False

            # Deal with the package and check up all the evens

            # Create tick rate
            self.clock.tick(60)

        # Cleanup
        # self.render.close_window()
