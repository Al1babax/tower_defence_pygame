from typing import Optional, List
from level import TerrainBlock
import os

"""
File for enemy classes and logic.
Currently, enemies cannot overlap so speed is not a factor.
"""

ENEMY_PATH = "assets/enemies"

# Template enemy values
template_enemies = {
    "normal": {
        "health": 100,
        "speed": 10,
        "money_value": 50,
        "armor": 0,
        "enemy_asset": None
    },
    "buff": {
        "health": 150,
        "speed": 8,
        "money_value": 100,
        "armor": 5,
        "enemy_asset": None
    },
    "fast": {
        "health": 80,
        "speed": 20,
        "money_value": 75,
        "armor": 2,
        "enemy_asset": None
    },
}

def a_star_algorithm(current_position: List[int], terrain: List[List]) -> List[List[int]]:
    # Calculate shortest path using A* algorithm
    # Return the shortest path as a list

    # Allowed nodes to move to are terrain blocks of type 0 and enemy blocks
    #
    return []

# General Enemy class with shared actions
class Enemy:
    def __init__(self, enemy_type, current_frame: int):
        self.position = None
        self.enemy_type = enemy_type

        # Shortest path for the enemy to follow
        self.shortest_path: List[List[int]] = []

        # Init enemy attributes
        self.hp = template_enemies[enemy_type]["health"]
        self.speed = template_enemies[enemy_type]["speed"]
        self.money_value = template_enemies[enemy_type]["money_value"]
        self.armor = template_enemies[enemy_type]["armor"]
        self.enemy_asset_path = os.path.join(ENEMY_PATH, template_enemies[enemy_type]["enemy_asset"])

        if not os.path.exists(self.enemy_asset_path):
            raise ValueError(f"Enemy asset path not found for enemy type: {enemy_type}")

        # Frame corresponding to the latest move
        self.last_move_frame = 0

    def move_forward(self, terrain: List[List], end_pos: List[int]) -> bool:
        """
        Move enemy to the next block
        :param end_pos:
        :param terrain:
        :return: True if enemy reaches the end block and False otherwise
        """

        # Calculate shortens path and save to self.shortest_path
        self.shortest_path = a_star_algorithm(self.position, terrain)

        # Move enemy to the next block
        next_block = self.shortest_path.pop(0)

        # Make certain next block is not occupied by another enemy
        if isinstance(terrain[next_block[0]][next_block[1]], Enemy):
            return False

        # Move enemy to the next block
        terrain[next_block[0]][next_block[1]] = self
        terrain[self.position[0]][self.position[1]] = TerrainBlock(0)

        # Update enemy position
        self.position = next_block

        return self.position == end_pos

    def take_damage(self, damage: int) -> bool:
        # General damage logic for all enemies, total_damage = damage - armor
        total_damage = damage - self.armor

        if total_damage > 0:
            self.hp -= total_damage
            print(f"Taking {total_damage} damage! HP: {self.hp}")

        # Check if enemy is dead
        if self.hp <= 0:
            print("Enemy is dead!")
            return True

        return False

    def apply_actions(self):
        # Apply actions based on enemy type
        if self.enemy_type == "normal":
            self._normal_actions()
        elif self.enemy_type == "buff":
            self._buff_allies()  # Shared buff action
        elif self.enemy_type == "fast":
            self._increase_speed()
        elif self.enemy_type == "fast_buff":
            self._increase_speed()  # Fast action
            self._buff_allies()  # Shared buff action

    # Shared action: Buff allies
    def _buff_allies(self):
        print("Buffing allies!")
        # Add buff logic

    # Shared action: Increase speed
    def _increase_speed(self):
        print("Increasing speed!")
        # Add speed logic

    # Unique action: Normal enemy behavior
    def _normal_actions(self):
        print("Normal enemy: No special action.")


if __name__ == "__main__":
    # Example usage:
    normal_enemy = Enemy(enemy_type="normal", current_frame=0)
    buff_enemy = Enemy(enemy_type="buff", current_frame=0)
    fast_enemy = Enemy(enemy_type="fast", current_frame=0)
    fast_buff_enemy = Enemy(enemy_type="fast_buff", current_frame=0)

    # Test enemy actions
    normal_enemy.apply_actions()  # Normal action
    buff_enemy.apply_actions()  # Buffing action
    fast_enemy.apply_actions()  # Speed increase action
    fast_buff_enemy.apply_actions()  # Both speed increase and buffing actions
