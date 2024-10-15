"""
Class for level attributes and methods
"""
from typing import Optional, List

class TerrainBlock:
    # Different terrain blocks between 0, 1, 2, 3, 4. 0 = enemy area blocks, 1 = tower placements, 2 = static block
    # 3 = start/spawn, 4 = end

    def __init__(self, block_type: str, asset_image: int):
       # Tells which kind of block this is
        self.block_type = block_type

       # Specify the image used for terrain
        self.asset_image = asset_image

class Level:
    def __init__(self):
        self.waves = [2, 4, 6, 8]
        self.current_wave = 0

        self.terrain: List[List[TerrainBlock]] = []
