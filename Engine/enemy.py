from typing import Optional, List
from Engine.level import TerrainBlock
import math
import os

"""
File for enemy classes and logic.
Currently, enemies cannot overlap so speed is not a factor.
"""
# TODO: Enemy movement vector or real position has to be calculate differently, currently with slow speed goes through walls
# TODO: The movement vector is not calculate correctly, somehow it is bigger than 1

ENEMY_PATH = "assets/enemies"

# Template enemy values
template_enemies = {
    "normal": {
        "health": 100,
        "speed": 60,
        "money_value": 50,
        "armor": 0,
        "enemy_asset": ""
    },
    "buff": {
        "health": 150,
        "speed": 50,
        "money_value": 100,
        "armor": 5,
        "enemy_asset": ""
    },
    "fast": {
        "health": 80,
        "speed": 40,
        "money_value": 75,
        "armor": 2,
        "enemy_asset": ""
    },
}


class Node:
    def __init__(self, parent=None, position=None):
        # Node parent and position
        self.parent = parent
        # Position is used as unique identifier for the node
        self.position = position

        # Node attributes
        self.travel_cost = 0
        self.heuristic = 0
        self.total_cost = 0


def euclidean_distance(position: List[int], end_position: List[int]) -> float:
    # Calculate the Euclidean distance between two points
    return math.sqrt((position[0] - end_position[0]) ** 2 + (position[1] - end_position[1]) ** 2)


def get_neighbors(node: Node, terrain: List[List]) -> List[List[int]]:
    # Get the neighbors of the current node
    neighbors = []

    # Check node to every position to every direction (up, down, left, right)
    # Check if the position is within the terrain
    # If position is open block for enemy or enemy block, add to neighbors
    starting_position = node.position
    offsets = [[0, 1], [1, 0], [0, -1], [-1, 0]]

    for offset in offsets:
        new_position = [starting_position[0] + offset[0], starting_position[1] + offset[1]]

        if new_position[0] < 0 or new_position[0] >= len(terrain):
            continue

        if new_position[1] < 0 or new_position[1] >= len(terrain[0]):
            continue

        new_block = terrain[new_position[0]][new_position[1]]

        if isinstance(new_block, TerrainBlock) and new_block.block_type == 0:
            neighbors.append(new_position)
        elif isinstance(new_block, Enemy):
            neighbors.append(new_position)

    return neighbors


def a_star_algorithm(current_position: List[int], terrain: List[List], end_position: List[int]) -> List[List[int]]:
    # Calculate the shortest path using A* algorithm
    # Return the shortest path as a list

    # Allowed nodes to move to are terrain blocks of type 0 and enemy blocks
    # Distance between nodes is 1
    stack = []
    visited = []
    path = []
    node_distance = 1

    # Create start and end nodes
    start_node = Node(None, current_position)
    end_node = Node(None, end_position)

    # Calculate heuristic for the start node
    start_node.heuristic = euclidean_distance(start_node.position, end_node.position)

    # Add start node to the stack
    stack.append(start_node)

    current_node = stack.pop(0)

    while current_node.position != end_node.position:
        # Get the neighbors of the current node
        neighbors_positions = get_neighbors(current_node, terrain)

        # Check all the neighbors
        for neighbor_pos in neighbors_positions:
            # Create a new node
            new_node = Node(current_node, neighbor_pos)

            # Calculate the travel cost
            new_node.travel_cost = current_node.travel_cost + node_distance

            # Calculate the heuristic
            new_node.heuristic = euclidean_distance(new_node.position, end_node.position)

            # Calculate the total cost
            new_node.total_cost = new_node.travel_cost + new_node.heuristic

            # Check if the node has been visited
            if new_node.position in visited:
                continue

            # Add the node to the stack
            stack.append(new_node)

        # Add the current node to the visited list
        visited.append(current_node.position)

        # Sort the stack based on the total cost
        stack = sorted(stack, key=lambda x: x.total_cost)

        # Get the next node
        current_node = stack.pop(0)

    # Reconstruct the path from the end node
    while current_node is not None:
        path.append(current_node.position)
        current_node = current_node.parent

    # Reverse path and remove itself start from path
    path = path[::-1][1:]

    return path


# General Enemy class with shared actions
class Enemy:
    def __init__(self, enemy_type: str):
        self.movement_vector: Optional[List[int]] = None
        self.enemy_type = enemy_type

        # Shortest path for the enemy to follow
        self.shortest_path: List[List[int]] = []
        self.previous_waypoint = None

        # Real position will be the actual pixel the enemy is at with every frame
        self.real_position = None

        # Init enemy attributes
        self.max_hp = template_enemies[enemy_type]["health"]
        self.current_hp = template_enemies[enemy_type]["health"]
        self.speed = template_enemies[enemy_type]["speed"]
        self.money_value = template_enemies[enemy_type]["money_value"]
        self.armor = template_enemies[enemy_type]["armor"]
        self.enemy_asset_path = os.path.join(ENEMY_PATH, template_enemies[enemy_type]["enemy_asset"])

        self.node_speed: int = 60 / self.speed

        # TODO: Activate check paths once have some assets
        # if not os.path.exists(self.enemy_asset_path):
        #     raise ValueError(f"Enemy asset path not found for enemy type: {enemy_type}")

        # Frame corresponding to the latest move
        self.last_move_frame = 0

    def calculate_shortest_path(self, terrain: List[List], end_pos: List[int]) -> None:
        # Calculate shortens path and save to self.shortest_path
        self.shortest_path = a_star_algorithm(self.previous_waypoint, terrain, end_pos)

        # Based on where the next shortest path is calculate the movement vector
        next_block = self.shortest_path[0]
        self.movement_vector = (next_block[0] - self.previous_waypoint[0], next_block[1] - self.previous_waypoint[1])

    def real_position_change(self):
        # print(F"Movement vector: {self.enemy_movement_vector}")
        enemy_movement_unit_vector = (self.movement_vector[0] / self.speed, self.movement_vector[1] / self.speed)

        # Real position change based on enemy movement vector
        self.real_position = (self.real_position[0] + enemy_movement_unit_vector[0], self.real_position[1] + enemy_movement_unit_vector[1])

    def move_forward(self, terrain: List[List], end_pos: List[List[int]], current_frame: int) -> bool:
        """
        Move enemy to the next block
        :param current_frame:
        :param end_pos:
        :param terrain:
        :return: True if enemy reaches the end block and False otherwise
        """
        self.real_position_change()

        # Make certain that enemy can move, use movement_speed of the enemy and frame difference
        # Use last move frame to calculate the time difference
        if current_frame - self.last_move_frame < self.speed:
            return False

        # Move enemy to the next block
        # TODO: Base on the movement speed of the enemy check if it is supposed to move now
        next_block = self.shortest_path.pop(0)

        # Calculate the movement vector
        self.movement_vector = (next_block[0] - self.previous_waypoint[0], next_block[1] - self.previous_waypoint[1])

        # Make certain next block is not occupied by another enemy
        if isinstance(terrain[next_block[0]][next_block[1]], Enemy):
            return False

        # Move enemy to the next block
        terrain[next_block[0]][next_block[1]] = self
        terrain[self.previous_waypoint[0]][self.previous_waypoint[1]] = TerrainBlock(0)

        # Update enemy position
        self.previous_waypoint = next_block

        # Update last move frame
        self.last_move_frame = current_frame

        # Check if enemy reached the end
        return self.previous_waypoint in end_pos

    def take_damage(self, damage: int) -> bool:
        # General damage logic for all enemies, total_damage = damage - armor
        total_damage = damage - self.armor

        if total_damage > 0:
            self.current_hp -= total_damage
            print(f"Taking {total_damage} damage! HP: {self.current_hp}")

        # Check if enemy is dead
        if self.current_hp <= 0:
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
