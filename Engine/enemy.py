"""
File for enemy classes and logic.
Currently, enemies cannot overlap so speed is not a factor.
"""

# Template enemy values
template_enemies = {
    "normal": {
        "health": 100,
        "speed": 10,
        "money_value": 50,
        "armor": 0
    },
    "buff": {
        "health": 150,
        "speed": 8,
        "money_value": 100,
        "armor": 5
    },
    "fast": {
        "health": 80,
        "speed": 20,
        "money_value": 75,
        "armor": 2
    },
}


# General Enemy class with shared actions
# MAYBE REMOVE SPAWN FRAME ATTRIBUTE
class Enemy:
    def __init__(self, enemy_type, position=None, spawn_frame=0):
        if position is None:
            position = [0, 0]

        self.hp = template_enemies[enemy_type]["health"]
        self.speed = template_enemies[enemy_type]["speed"]
        self.money_value = template_enemies[enemy_type]["money_value"]
        self.armor = template_enemies[enemy_type]["armor"]
        self.position = position
        self.spawn_frame = spawn_frame
        self.enemy_type = enemy_type

    def move_forward(self, next_block):
        # General movement logic for all enemies
        self.position = next_block
        print(f"Moving to {self.position}")

    def take_damage(self, damage):
        # General damage logic for all enemies, total_damage = damage - armor
        total_damage = damage - self.armor

        if total_damage > 0:
            self.hp -= total_damage
            print(f"Taking {total_damage} damage! HP: {self.hp}")

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
    normal_enemy = Enemy(enemy_type="normal")
    buff_enemy = Enemy(enemy_type="buff")
    fast_enemy = Enemy(enemy_type="fast")
    fast_buff_enemy = Enemy(enemy_type="fast_buff")

    # Test enemy actions
    normal_enemy.apply_actions()  # Normal action
    buff_enemy.apply_actions()  # Buffing action
    fast_enemy.apply_actions()  # Speed increase action
    fast_buff_enemy.apply_actions()  # Both speed increase and buffing actions
