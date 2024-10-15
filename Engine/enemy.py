"""
Class for enemy attributes and methods
"""

class Enemy:
    def __init__(self):
        self.hp = 100
        self.money_value = 100
        self.position = [] # x, y

        # When this spawn_frame gets to 0 it means the enemy should spawn
        self.spawn_frame = 0
