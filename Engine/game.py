from typing import Optional, List, Tuple

# Engine modules
from tower import Tower
from enemy import Enemy
from level import Level

"""
Class that handles all the logic of the game

Towers are going to apply damage every 10 ticks
Enemies are moving to next grid every 10 ticks

Start game with 10 lives, if more than 10 enemies reach the end game over

Towers cost certain amount of money
Enemies killed give some money
"""


class Game:
    def __init__(self):
        # Init the game state
        self.state: List[List] = []

        # Init level
        self.level = Level()

        # Current frame of the game
        self.frame = 0

        # Game attributes
        self.game_running = True
        self.lives = 10
        self.money = 1000

    def spawn_enemy(self):
        # Make enemy array based on waves, every enemy has attribute spawn_frame that tells when they should spawn
        # Every wave will have x amount of enemies and

        # MAYBE REMOVE THIS FUNCTION AND MOVE TO LEVEL CLASS
        pass

    def tower_actions(self):
        # Function that applies all the tower damage to enemies in their area
        # Loop through towers and loop through every enemy in their are of influence, and then apply towers damage
        for tower in self.level.towers:
            pass

    def enemy_actions(self):
        for enemy in self.level.enemies:
            # Move enemy
            self.enemy.move_forward(self.level.terrain)

    def update(self):
        """
        1. [30 tick] Move all enemies forward
        1.1 Check if enemy reach the end --> lose life if so

        2. [30 tick] Check tower actions
        2.1 Deal damage to enemies, if enemy dies remove it, add money

        3. [30 tick] Check if new enemy should spawn
        3.1 Run the level class which has logic how to spawn enemies
        """

        if self.frame % 30 == 0:
            self.enemy_actions()
            self.tower_actions()

        self.spawn_enemy()

        self.frame += 1
