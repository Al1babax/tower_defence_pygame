from typing import Optional, List, Tuple

# Engine modules
from Engine.tower import Tower
from Engine.enemy import Enemy
from Engine.level import Level

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

    def tower_actions(self):
        # Function that applies all the tower damage to enemies in their area
        # Loop through towers and loop through every enemy in their are of influence, and then apply towers damage
        for tower in self.level.towers:
            tower.shoot(self.level.enemies, self.frame)

    def enemy_actions(self):
        # Go through all the enemies and try to move them forward
        # For enemy to know which next block to go calculate the shortest path using A* algorithm

        # For now this will be little clunky because if the order of moving enemies is not right,
        # enemies will block each other for now because they cannot yet overlap
        for enemy in self.level.enemies:
            # Move enemy
            enemy.move_forward(self.level.terrain, self.level.end_blocks)

    def update(self):
        """
        1. Move all enemies forward
        1.1 Check if enemy reach the end --> lose life if so

        2. Check tower actions
        2.1 Deal damage to enemies, if enemy dies remove it, add money

        3. Check if new enemy should spawn
        3.1 Run the level class which has logic how to spawn enemies
        """
        self.enemy_actions()
        self.tower_actions()
        self.level.spawn_enemy_wave(self.frame)

        self.frame += 1
