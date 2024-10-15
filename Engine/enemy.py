"""
Class for enemy attributes and methods
"""

class Enemy:
    def __init__(self):
        self.hp = 100
        self.money_value = 100
        self.position = [5, 5] # x, y

        # When this spawn_frame gets to 0 it means the enemy should spawn
        self.spawn_frame = -7

    def apply_damage(self):
        pass

    def move_forward(self, next_block):
        pass
