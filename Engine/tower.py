from typing import Optional, List, Tuple
import os
import math

"""
Class for handling towers attributes and methods:
- Initialize class (position, type)
- Methods: shoot, upgrade,  
 
"""

PROJECTILE_PATH = "assets/projectiles"
TOWER_PATH = "assets/towers"

towers_template = {
    "standard": {
        0: {
            "hp": 100,
            "cost": 150,
            "range": 3.0,
            "shot_cooldown": 60,
            "damage": 10,
            "damage_type": "base",
            "projectile_asset": "",
            "tower_asset": "",
        },
        1: {
            "hp": 150,
            "cost": 250,
            "range": 4.0,
            "shot_cooldown": 50,
            "damage": 15,
            "damage_type": "base",
            "projectile_asset": "",
            "tower_asset": "",
        }
    }
}
# TODO: write functions to figure out projectile angle and turret angle
def euclidean_distance(position: List[int], end_position: List[int]) -> float:
    return math.sqrt((position[0] - end_position[0]) ** 2 + (position[1] - end_position[1]) ** 2)

def calculate_tower_angle(tower_position: List[int],
                          enemy_position: List[int],
                          projectile_speed: int,
                          enemy_movement_speed: int
                          ) -> int:
    pass


class Tower:
    def __init__(self, tower_type: str, tower_position: List[int]):
        self.position = tower_position  # x, y
        self.type = tower_type
        self.tower_level = 0

        # Tower properties
        self.hp: int = 0
        self.cost: int = 0
        self.range: float = 0
        self.shot_cooldown: int = 0
        self.damage: int = 0
        self.damage_type: int = 0
        self.rotation: int = 90

        # Paths for Tower and Projectiles assets
        self.projectile_asset_path = ""
        self.tower_asset_path = ""

        self.set_tower_properties()

        # Frame corresponding to the latest shot
        self.last_shot_frame = 0

    def set_tower_properties(self):
        self.hp = towers_template[self.type][self.tower_level]["hp"]
        self.cost = towers_template[self.type][self.tower_level]["cost"]
        self.range = towers_template[self.type][self.tower_level]["range"]
        self.shot_cooldown = towers_template[self.type][self.tower_level]["shot_cooldown"]
        self.damage = towers_template[self.type][self.tower_level]["damage"]
        self.damage_type = towers_template[self.type][self.tower_level]["damage_type"]

        self.projectile_asset_path = os.path.join(PROJECTILE_PATH,
                                                  towers_template[self.type][self.tower_level]["projectile_asset"])

        # TODO: Activate check paths once have some assets
        # if not os.path.exists(self.projectile_asset_path):
        #     raise (f"Error with asset path: {self.projectile_asset_path}")

        self.tower_asset_path = os.path.join(TOWER_PATH, towers_template[self.type][self.tower_level]["tower_asset"])
        # if not os.path.exists(self.tower_asset_path):
        #     raise (f"Error with asset path: {self.tower_asset_path}")

    def upgrade_tower(self):
        if self.tower_level + 1 > max(towers_template[self.type].keys()):
            raise ("Tower should not be upgradable")

        self.tower_level += 1
        self.set_tower_properties()

    def shoot(self, enemy_list: List, cur_frame: int) -> Optional:
        """
        Shoot at the enemy if it is in range
        Return True if enemy died, False otherwise
        :param enemy_list:
        :param cur_frame:
        :return:
        """
        # If shot cooldown has not elapsed, tower cannot shoot
        if cur_frame - self.last_shot_frame < self.shot_cooldown:
            return None

        for enemy in enemy_list:
            enemy_row, enemy_col = enemy.position[0], enemy.position[1]
            tower_row, tower_col = self.position[0], self.position[1]
            row_dist, col_dist = abs(tower_row - enemy_row), abs(tower_col - enemy_col)

            dist_to_enemy = math.sqrt(row_dist ** 2 + col_dist ** 2)
            if dist_to_enemy > self.range:
                continue

            # If an enemy is shot, cooldown starts over and we exit the loop
            enemy_died: bool = enemy.take_damage(self.damage)

            self.last_shot_frame = cur_frame

            print(f"Shot at enemy! Enemy life left {enemy.hp}")
            return enemy if enemy_died else None
