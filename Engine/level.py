import random

from typing import Optional, List
from Engine.tower import Tower


class TerrainBlock:
    """
    Class for terrain block attributes and methods
    Block types:
    0 = enemy area blocks
    1 = tower placements
    2 = static block
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
                "normal": 2,
                "buff": 0
            },
            1: {
                "normal": 10,
                "buff": 0
            }
        }

        # Current wave
        self.current_wave = 0
        # Boolean to know whether to keep checking if more enemies need to be spawned
        self.spawn_enemies = True
        # Spawn timer set to 120 ticks
        self.spawn_timer = 120
        self.previous_spawn_frame = 0

        # Start end block positions
        self.start_blocks = []
        self.end_blocks = []

        # Terrain blocks of objects. Consists of terrain block objects, enemy objects and tower objects
        self.terrain: List[List] = []

        # List of enemies and towers
        self.enemies: List = []
        self.towers: List[Tower] = []
        self.tower_slots: List[List[int]] = []

        # Create terrain
        # self.create_terrain()
        self.create_terrain_2()

    def create_random_level(self):
        random_enemy_path = []

        # Start from random position on the left wall
        current_pos = [random.randint(0, 9), 0]
        random_enemy_path.append(current_pos.copy())

        # From starting_pos move randomly only to right or up or down, also cannot go to visited position
        while current_pos[1] < 19:
            # Randomly choose direction and make certain it is valid
            new_pos = None
            while True:
                random_direction = random.randint(0, 2)

                if random_direction == 0:
                    if current_pos[1] + 1 < 20:
                        new_pos = [current_pos[0], current_pos[1] + 1]
                        break
                elif random_direction == 1:
                    if current_pos[0] - 1 >= 0:
                        new_pos = [current_pos[0] - 1, current_pos[1]]
                        break
                elif random_direction == 2:
                    if current_pos[0] + 1 < 10:
                        new_pos = [current_pos[0] + 1, current_pos[1]]
                        break

            # Make certain that the path does not go back to the same position
            if new_pos in random_enemy_path:
                continue

            current_pos = new_pos
            random_enemy_path.append(current_pos.copy())

        return random_enemy_path

    def create_terrain_2(self):
        random_enemy_path = self.create_random_level()

        # First fill terrain with static blocks
        for i in range(10):
            self.terrain.append([TerrainBlock(2) for _ in range(20)])

        # Place enemy path
        for path in random_enemy_path:
            self.terrain[path[0]][path[1]] = TerrainBlock(0)

        # Set the start and end blocks
        self.start_blocks.append(random_enemy_path[0])
        self.end_blocks.append(random_enemy_path[-1])

        # Randomly put two tower placements on any of the static blocks
        for _ in range(2):
            x = random.randint(0, 9)
            y = random.randint(0, 19)

            while self.terrain[x][y].block_type != 2:
                x = random.randint(0, 9)
                y = random.randint(0, 19)

            self.terrain[x][y] = TerrainBlock(1)

            # Save the tower slot
            self.tower_slots.append([x, y])

    def create_terrain(self):
        self.create_random_level()
        # Create terrain based on the level design
        # For now create a simple terrain for testing and dev purposes
        # 10x20 grid with straight path from top to bottom for enemies, and some tower placements
        # Static blocks to make the path
        # Only one start and end block
        for i in range(10):
            self.terrain.append([TerrainBlock(2) for _ in range(20)])

        # Place path for enemies in the middle
        for i in range(20):
            self.terrain[4][i] = TerrainBlock(0)

        # Save start and end block positions
        self.start_blocks.append([4, 0])
        self.end_blocks.append([4, 19])

        # Place some tower placements next to the path
        self.terrain[3][10] = TerrainBlock(1)
        self.terrain[5][10] = TerrainBlock(1)

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

    def spawn_enemy_wave(self, current_frame: int):
        from Engine.enemy import Enemy
        # Make certain that the spawn timer is met
        if current_frame - self.previous_spawn_frame < self.spawn_timer:
            return

        # Check if enemies still to spawn in the current wave, if there are choose randomly enemy to spawn
        wave_enemies = self.get_current_wave_enemies()

        enemy = None
        for enemy_type, amount in wave_enemies.items():
            if amount == 0:
                continue

            # Create enemy object
            enemy = Enemy(enemy_type)
            break

        # If no enemies to spawn anymore, return
        if enemy is None:
            self.spawn_enemies = False
            return

        # Reduce the amount of enemies to spawn
        wave_enemies[enemy.enemy_type] -= 1

        # Choose random start and make certain it is empty
        random_start = None
        possible_starts = self.start_blocks.copy()

        while random_start is None:
            # If no possible spawns are available, return
            if len(possible_starts) == 0:
                return

            # Choose random start
            random_start = random.choice(possible_starts)

            # Make certain the block is terrain block and 0 to have valid start
            start_block = self.terrain[random_start[0]][random_start[1]]
            if isinstance(start_block, TerrainBlock) and start_block.block_type == 0:
                break
            else:
                # Remove the start from possible starts
                possible_starts.remove(random_start)
                random_start = None

        # Save enemy position
        enemy.previous_waypoint = random_start
        enemy.real_position = random_start

        # Add enemy to the list of enemies
        self.enemies.append(enemy)

        # Update the terrain
        self.terrain[random_start[0]][random_start[1]] = enemy

        self.previous_spawn_frame = current_frame

        # Calculate the shortest path for enemy
        # TODO: Currently can only handle one end block
        enemy.calculate_shortest_path(self.terrain, self.end_blocks[0])

    def move_enemy(self, current_position: List[int], new_position: List[int]):
        from Engine.enemy import Enemy
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
        enemy = self.terrain[position[0]][position[1]]

        # Remove enemy from the list
        self.enemies.remove(enemy)

        # Remove enemy from the terrain
        self.terrain[position[0]][position[1]] = TerrainBlock(0)

        # Check if the wave is over
        if len(self.enemies) == 0:
            # If wave is over, check if it was the last wave
            if self.is_last_wave():
                print("Game over!")
            else:
                # If not last wave, spawn next wave
                self.spawn_enemies = True
                self.next_wave()

    def place_tower(self, position: List[int], tower: Tower):
        # Check if the position is empty tower placement
        if self.terrain[position[0]][position[1]].block_type != 1:
            raise ValueError("Position is not empty tower placement")

        # Place the tower to the position
        self.terrain[position[0]][position[1]] = tower

        # Add tower to the list of towers
        self.towers.append(tower)

    def remove_tower(self, position: List[int]):
        # Check if the position is tower
        if not isinstance(self.terrain[position[0]][position[1]], Tower):
            raise ValueError("Position is not tower")

        # Remove the tower from the list of towers
        tower = self.terrain[position[0]][position[1]]
        self.towers.remove(tower)

        # Remove the tower from the terrain
        self.terrain[position[0]][position[1]] = TerrainBlock(1)

    def update(self,
               event: int,
               tower: Optional[Tower] = None,
               enemy=None,
               current_position: Optional[List[int]] = None,
               new_position: Optional[List[int]] = None
               ):
        """
        Function that is called from outside if any changes happen to the level

        Changes:
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
                self.move_enemy(current_position, new_position)
            case 1:
                self.kill_enemy(current_position)
            case 2:
                self.place_tower(current_position, tower)
            case 3:
                self.remove_tower(current_position)
            case _:
                raise ValueError("Invalid event")


if __name__ == "__main__":
    level = Level()
    level.create_terrain()
    level.print_terrain()
