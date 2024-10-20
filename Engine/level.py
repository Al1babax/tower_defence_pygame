import random

from typing import Optional, List
from tower import Tower
from enemy import Enemy


class TerrainBlock:
    """
    Class for terrain block attributes and methods
    Block types:
    0 = enemy area blocks
    1 = tower placements
    2 = static block
    3 = start/spawn
    4 = end
    """

    def __init__(self, block_type: int, asset_image_path: Optional[str] = None):
        # Tells which kind of block this is
        self.block_type = block_type

        # Specify the image used for terrain
        self.asset_image = asset_image_path


class Level:
    """
    Class for level attributes and methods

    Level class is responsible for creating the terrain and holds the information about the waves of enemies
    """

    def __init__(self):
        # Define waves of enemies (Later defined on a separate file)
        self.waves = {
            0: {
                "normal": 5,
                "buff": 0
            },
            1: {
                "normal": 10,
                "buff": 0
            }
        }

        # Current wave
        self.current_wave = 0

        # Start end block positions
        self.start_blocks = []
        self.end_blocks = []

        # Terrain blocks of objects. Consists of terrain block objects, enemy objects and tower objects
        self.terrain: List[List] = []

        # List of enemies and towers
        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []

    def create_terrain(self):
        # Create terrain based on the level design
        # For now create a simple terrain for testing and dev purposes
        # 20x10 grid with straight path from top to bottom for enemies, and some tower placements
        # Static blocks to make the path
        # Only one start and end block
        for i in range(20):
            self.terrain.append([TerrainBlock(2) for _ in range(10)])

        # Place path for enemies in the middle
        for i in range(20):
            self.terrain[i][4] = TerrainBlock(0)

        # Save start and end block positions
        self.start_blocks.append([0, 4])
        self.end_blocks.append([19, 4])

        # Place some tower placements next to the path
        self.terrain[10][3] = TerrainBlock(1)
        self.terrain[10][5] = TerrainBlock(1)

    def print_terrain(self):
        for row in self.terrain:
            for block in row:
                print(block.block_type, end=" ")
            print()

    def get_terrain(self):
        return self.terrain

    def get_current_wave(self):
        return self.current_wave

    def get_current_wave_enemies(self):
        return self.waves[self.current_wave]

    def next_wave(self):
        self.current_wave += 1
        return self.waves[self.current_wave]

    def is_last_wave(self):
        return self.current_wave == len(self.waves) - 1

    def spawn_enemy(self, enemy: Enemy):
        # Choose randomly the start block and put the enemy object there
        random_start = random.choice(self.start_blocks)

        # Save enemy position
        enemy.position = random_start

        # Add enemy to the list of enemies
        self.enemies.append(enemy)

        # Update the terrain
        self.terrain[random_start[0]][random_start[1]] = enemy

    def move_enemy(self, current_position: List[int], new_position: List[int]):
        # Make sure current position is enemy
        if not isinstance(self.terrain[current_position[0]][current_position[1]], Enemy):
            raise ValueError("Current position is not enemy")

        # Make sure new position is empty path for enemy
        if self.terrain[new_position[0]][new_position[1]].block_type != 0:
            raise ValueError("New position is not empty path for enemy")

        # Move the enemy to the new position (Maybe can create error handling for this with references)
        self.terrain[new_position[0]][new_position[1]] = self.terrain[current_position[0]][current_position[1]]

        # Remove the enemy from the old position
        self.terrain[current_position[0]][current_position[1]] = TerrainBlock(0)

    def kill_enemy(self, position: List[int]):
        # Kill the enemy and then check if the wave is over
        pass

    def place_tower(self, position: List[int], tower: Tower):
        pass

    def remove_tower(self, position: List[int]):
        pass

    def update(self,
               event: int,
               tower: Optional[Tower] = None,
               enemy: Optional[Enemy] = None,
               current_position: Optional[List[int]] = None,
               new_position: Optional[List[int]] = None
               ):
        """
        Function that is called from outside if any changes happen to the level

        Changes:
        - Enemy is spawned
        - Enemy moves to next block
        - Enemy is killed
        - Tower is placed
        - Tower is removed

        :param event: Event that happened
        :param tower: Tower object if tower was placed
        :param enemy: Enemy object if enemy was spawned
        :param current_position: Current position of the object
        :param new_position: New position of the object
        """

        match event:
            case 0:
                self.spawn_enemy(enemy)
            case 1:
                self.move_enemy(current_position, new_position)
            case 2:
                self.kill_enemy(current_position)
            case 3:
                self.place_tower(current_position, tower)
            case 4:
                self.remove_tower(current_position)
            case _:
                raise ValueError("Invalid event")


if __name__ == "__main__":
    level = Level()
    level.create_terrain()
    level.print_terrain()
