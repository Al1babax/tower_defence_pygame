import pygame
from Engine.level import Level
from typing import Optional, Tuple
import json

"""
Class to render the game to the screen
"""

# Read sprite map from json file
with open("Engine/sprite_map.json", "r") as file:
    sprite_map = json.load(file)


class Sprite:
    def __init__(
            self, sprite_category: str,
            sprite_type: str,
            enemy_action: Optional[str] = None,
            tower_level: Optional[int] = 0,
            size: Tuple[int, int] = (80, 80)
    ):
        self.sprite_sheet = pygame.image.load("Assets/main.png")
        self.sprite_category = sprite_category
        self.sprite_type = sprite_type
        self.size = size
        # Action determines which animation to play and will be none if there is no animation
        self.action = enemy_action
        self.tower_level = tower_level
        self.current_animation = 0

        self.sprite_object: Optional[pygame.Surface] = None
        self.init_sprite()

    def extract_sprite(self, sprite_sheet: pygame.Surface, x: int, y: int) -> pygame.Surface:
        sprite = pygame.Surface((16, 16))
        sprite.blit(sprite_sheet, (0, 0), (x * 16, y * 16, 16, 16))
        return sprite

    def init_sprite(self):
        sprite_position = sprite_map[self.sprite_category][self.sprite_type]
        if self.sprite_category == "enemies":
            sprite_position = sprite_position[self.action][self.current_animation]
        elif self.sprite_category == "towers":
            sprite_position = sprite_map[self.sprite_category][self.sprite_type][self.tower_level]

        sprite = self.extract_sprite(self.sprite_sheet, sprite_position[0], sprite_position[1])
        sprite = pygame.transform.scale(sprite, self.size)

        self.sprite_object = sprite

    def get_sprite(self):
        return self.sprite_object

    def upgrade_tower(self):
        if self.sprite_category != "towers":
            raise ValueError("Cannot upgrade a sprite that is not a tower")

        # Check if tower already max level and raise error
        if self.tower_level + 1 >= len(sprite_map[self.sprite_category][self.sprite_type]):
            raise ValueError("Tower is already at max level")

        self.tower_level += 1
        self.init_sprite()

    def select_next_animation(self):
        if self.action is None:
            raise ValueError("Action is not set for the sprite")

        # Make certain there is next animation in current action if not reset to 0
        if self.current_animation + 1 >= len(sprite_map[self.sprite_category][self.sprite_type][self.action]):
            self.current_animation = 0
        else:
            self.current_animation += 1

    def rotate_sprite(self, angle: int):
        self.sprite_object = pygame.transform.rotate(self.sprite_object, angle)


return_package = {
    "game_over": False,
    "new_tower": {
        "position": None,
        "type": None
    },
    "remove_tower": None
}


class Render:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tower Defense")

        self.return_package = return_package

        self.sprite_object = Sprite(
            sprite_category="ground",
            sprite_type="tower",
            enemy_action=None,
            tower_level=0,
            size=(80, 80)
        )
        # self.sprite_object.upgrade_tower()
        # self.sprite_object.upgrade_tower()

    def update(self, render_package: dict) -> dict:
        self.return_package = return_package

        # Update the screen
        self.screen.fill((0, 0, 0))

        # Deal with events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.return_package["game_over"] = True

        # Display normal enemy sprite in the middle
        self.screen.blit(self.sprite_object.get_sprite(), (self.screen_width // 2, self.screen_height // 2))

        # Example for updating the sprite animation
        # if render_package["current_frame"] % 20 == 0:
        #     self.sprite_object.select_next_animation()

        # Example for rotating the sprite
        # if render_package["current_frame"] % 20 == 0:
        #     self.sprite_object.rotate_sprite(90)

        # Game over
        # self.return_package["game_over"] = True

        pygame.display.flip()
        return self.return_package

    def close_window(self):
        pygame.quit()
