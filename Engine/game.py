from typing import Optional, List, Tuple
import random

# Engine modules
from Engine.tower import Tower
from Engine.enemy import Enemy
from Engine.level import Level, TerrainBlock

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

        # Force spawn turret for testing
        # self.force_spawn_turret_for_testing()
        self.force_spawn_turret_2()

    def force_spawn_turret_for_testing(self):
        # Force spawn turret for testing
        # Find a terrain block with open turret slot and spawn a turret there
        position = [5, 10]
        new_tower = Tower("standard", position)
        self.level.update(2, current_position=position, tower=new_tower)

    def force_spawn_turret_2(self):
        # Randomly choose turret spawn to put a turret
        # Find a terrain block with open turret slot and spawn a turret there
        if len(self.level.tower_slots) == 0:
            return

        random_turret_position = random.choice(self.level.tower_slots)
        new_tower = Tower("standard", random_turret_position)
        self.level.update(2, current_position=random_turret_position, tower=new_tower)

    def tower_actions(self):
        # Function that applies all the tower damage to enemies in their area
        # Loop through towers and loop through every enemy in their are of influence, and then apply towers damage
        for tower in self.level.towers:
            possible_death_enemy: Enemy = tower.shoot(self.level.enemies, self.frame)

            if possible_death_enemy is None:
                continue

            # If enemy dies, remove it from the enemy_list, add 0 terrain block to the position and add money
            self.money += possible_death_enemy.money_value
            self.level.update(1, current_position=possible_death_enemy.previous_waypoint)

    def enemy_actions(self):
        # Go through all the enemies and try to move them forward
        # For enemy to know which next block to go calculate the shortest path using A* algorithm

        # For now this will be little clunky because if the order of moving enemies is not right,
        # enemies will block each other for now because they cannot yet overlap
        for enemy in self.level.enemies:
            # Move enemy
            enemy_reach_end = enemy.move_forward(self.level.terrain, self.level.end_blocks, self.frame)

            # Print enemy shortest path
            if abs(enemy.movement_vector[0]) > 0 and abs(enemy.movement_vector[1]) > 0:
                # print("Current waypoint: ", enemy.previous_waypoint)
                # print("Next waypoint: ", enemy.shortest_path[0])
                # print("movement vector: ", enemy.movement_vector)
                pass

            if enemy_reach_end:
                # If enemy reached the end, remove enemy from the list, remove 0 terrain block from the position
                # and remove 1 life from the player
                self.lives -= 1
                self.level.update(1, current_position=enemy.previous_waypoint)
                print(f"Enemy reached the end! Lives left: {self.lives}")

    def update(self):
        """
        1. Move all enemies forward
        1.1 Check if enemy reach the end --> lose life if so

        2. Check tower actions
        2.1 Deal damage to enemies, if enemy dies remove it, add money

        3. Check if new enemy should spawn
        3.1 Run the level class which has logic how to spawn enemies
        """
        if self.lives <= 0:
            print("Game over! You lost all your lives!")
            self.game_running = False

        self.enemy_actions()
        self.tower_actions()
        self.level.spawn_enemy_wave(self.frame)

        self.frame += 1
