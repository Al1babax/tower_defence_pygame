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
        self.state: List[List[int]] = []

        # Init level
        self.level = Level()

        # Current frame of the game
        self.frame = 0

        # Game attributes
        self.game_running = True
        self.lives = 10
        self.money = 1000

        # Active elements
        self.towers: List[Tower] = []
        self.enemies: List[Enemy] = []

    def spawn_enemy(self):
        # Make enemy array based on waves, every enemy has attribute spawn_frame that tells when they should spawn
        # Every wave will have x amount of enemies and
        pass

    def tower_actions(self):
        # Function that applies all the tower damage to enemies in their area
        # Loop through towers and loop through every enemy in their are of influence, and then apply towers damage
        for tower in self.towers:
            pass

    def update(self):
        if self.frame % 10 == 0:
            self.tower_actions()
            self.spawn_enemy()

        self.frame += 1
