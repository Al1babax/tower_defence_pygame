"""
Class for enemy attributes and methods
"""
class Normal:
    def run_actions (self):
        pass

class Buff:
    def buff_allies(self):
        pass

    def run_actions(self):
        self.buff_allies()

all_enemies = {
    0: Normal,
    1: Buff
}

class Enemy:
    def __init__(self, enemy_type):
        self.hp = 100
        self.money_value = 100
        self.position = [5, 5] # x, y

        # When this spawn_frame gets to 0 it means the enemy should spawn
        self.spawn_frame = -7
        self.enemy_type = enemy_type

        self.enemy_class_object = all_enemies[enemy_type]()

    def apply_actions(self):
        self.enemy_class_object.run_actions()
        pass

    def move_forward(self, next_block):
        pass
