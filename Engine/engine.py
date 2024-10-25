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

    def print_game(self):
        from Engine.level import TerrainBlock
        from Engine.enemy import Enemy
        from Engine.tower import Tower
        for row in self.game.level.terrain:
            for block in row:
                if isinstance(block, TerrainBlock):
                    print(block.block_type, end=" ")
                elif isinstance(block, Enemy):
                    print("E", end=" ")
                elif isinstance(block, Tower):
                    print("T", end=" ")
            print()

        print("\n")

    def run(self):
        while self.game.game_running:
            if self.game.frame % 60 == 0:
                print("Frame: ", self.game.frame)
                # self.print_game()

            # Update loop to run the game
            self.game.update()

            # Render info package
            render_package = {
                "money": self.game.money,
                "lives": self.game.lives,
                "current_frame": self.game.frame,
                "level": self.game.level,
            }
            return_package: dict = self.render.update(render_package)

            if return_package["game_over"] is True:
                self.game.game_running = False

            # Deal with the package and check up all the evens

            # Create tick rate
            self.clock.tick(60)

        # Cleanup
        self.render.close_window()
