import json
from dataclasses import dataclass
from typing import Optional, Tuple, List

import pygame

"""
Class to render the game to the screen
"""

# TODO: Move all these to config file
CAPTION_TEXT = "Tower Defense"
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
SCREEN_X_POS, SCREEN_Y_POS = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = 1240, 680

# Read sprite map from json file
with open("Engine/sprite_map.json", "r") as file:
    sprite_map = json.load(file)

sprite_sheet = pygame.image.load("Assets/main.png")


class Sprite:
    def __init__(
            self, sprite_category: str,
            sprite_type: str,
            enemy_action: Optional[str] = None,
            tower_level: Optional[str] = "0",
            size: Tuple[int, int] = (80, 80)
    ):
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

        sprite = self.extract_sprite(sprite_sheet, sprite_position[0], sprite_position[1])
        sprite = pygame.transform.scale(sprite, self.size)

        self.sprite_object = sprite

    def get_sprite(self):
        return self.sprite_object

    def upgrade_tower(self):
        if self.sprite_category != "towers":
            raise ValueError("Cannot upgrade a sprite that is not a tower")

        # Check if tower already max level and raise error
        if int(self.tower_level) + 1 >= len(sprite_map[self.sprite_category][self.sprite_type]):
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

        self.init_sprite()

    def rotate_sprite(self, angle: int):
        self.sprite_object = pygame.transform.rotate(self.sprite_object, angle)


@dataclass
class ReturnPackage:
    game_over: bool = False
    new_tower_position: Optional[List[int]] = None
    new_tower_type: Optional[str] = None
    remove_tower_position: Optional[List[int]] = None


class Render:
    def __init__(self):
        # Create game window, and screen where game will be displayed
        self.window_width, self.window_height = WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.game_window: Optional[pygame.Surface] = None
        self.screen_rect = None

        self.return_package: Optional[ReturnPackage] = None
        self.sprite_dict = {}

        self.previous_terrain = []
        self.block_size: int = 0

        # Get the game window to show up
        self.create_game_window()

    def create_game_window(self):
        # Imports all pygame modules
        pygame.init()

        # Set caption (i.e. title for our game window)
        pygame.display.set_caption(CAPTION_TEXT)

        # Create [width * height] window and screen where our entire game window will be displayed
        self.game_window = pygame.display.set_mode((self.window_width, self.window_height))
        self.screen_rect = pygame.Rect(SCREEN_X_POS, SCREEN_Y_POS, self.screen_width, self.screen_height)

    def rotate_terrain(self, vertical_terrain):
        row_len = len(vertical_terrain[0])
        rotated_terrain = [[row[j] for row in vertical_terrain] for j in range(row_len - 1, -1, -1)]
        return rotated_terrain

    def render_game(self, level):
        from Engine.level import TerrainBlock
        from Engine.enemy import Enemy
        from Engine.tower import Tower

        # Rotate the terrain matrix so enemies move left to right
        rotated_terrain = self.rotate_terrain(level.terrain)

        self.block_size = min(self.screen_width // len(rotated_terrain[0]), self.screen_height // len(rotated_terrain))

        # List of towers, to show each tower's shooting range
        tower_list = []

        # Display terrain map on screen: 0 = enemy, 1 = tower, 2 = static block
        # TODO: Maybe better if sprites are created only once for each tile and only changed if needed vs created every frame
        # TODO: Save previous terrain and compare if changed to only update changed tiles/objects

        saved_previous_terrain = False
        if not self.previous_terrain:
            self.previous_terrain = rotated_terrain
            saved_previous_terrain = True

        for i, row in enumerate(rotated_terrain):
            for j, sq in enumerate(row):

                # If previous frame block is the same as current block
                if not saved_previous_terrain and sq == self.previous_terrain[i][j]:
                    sq_sprite = self.sprite_dict[(i, j)]
                    continue

                else:

                    sq_color = ""
                    # Sprite info
                    sprite_category = ""
                    sprite_type = ""
                    enemy_action = ""
                    tower_level = ""
                    size = (self.block_size, self.block_size)

                    if isinstance(sq, TerrainBlock):
                        if sq.block_type == 0:  # Enemy path
                            sq_color = "antiquewhite4"
                            sprite_category = "ground"
                            sprite_type = "dirt"
                        if sq.block_type == 1:  # Empty tower block
                            sq_color = "White"
                            sprite_category = "ground"
                            sprite_type = "tower"
                        if sq.block_type == 2:  # Static block
                            sq_color = "azure3"
                            sprite_category = "ground"
                            sprite_type = "grass"
                    elif isinstance(sq, Enemy):
                        sq_color = "Red"  # Enemy block
                        sprite_category = "enemies"
                        sprite_type = "normal"
                        enemy_action = "run"
                    elif isinstance(sq, Tower):
                        sq_color = "Blue"  # Tower block
                        sprite_category = "towers"
                        sprite_type = "normal"
                        tower_level = "0"

                    # Create current sprite, and save it to sprite dictionary
                    sq_sprite = Sprite(sprite_category=sprite_category, sprite_type=sprite_type,
                                       enemy_action=enemy_action,
                                       tower_level=tower_level, size=size)

                    self.sprite_dict[(i, j)] = sq_sprite
                    self.previous_terrain[i][j] = sq

                # Highlight player base in green
                # TODO: Highlight player base in some way, but only once
                # if [j, len(rotated_terrain) - 1 - i] in level.end_blocks:
                #     sq_color = "Green"

                # Create rectangle as container for the sprite
                sq_rect = pygame.Rect(SCREEN_X_POS + (j * self.block_size), SCREEN_Y_POS + (i * self.block_size),
                                      self.block_size, self.block_size)

                # Draw the sprite on the screen
                self.game_window.blit(sq_sprite.get_sprite(), sq_rect)

                # If current block is a tower, add it to the list of towers (to show shooting range)
                if isinstance(sq, Tower):
                    tower_list.append([sq, sq_rect, "Blue"])

        # For each tower placed, show shooting range
        for tower, tower_rect, tower_color in tower_list:
            pygame.draw.circle(self.game_window, tower_color, tower_rect.center, tower.range * self.block_size, width=1)

    def get_keyboard_input(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_ESCAPE]:
            self.return_package.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.return_package.game_over = True

    def update(self, render_package: dict) -> ReturnPackage:
        self.return_package = ReturnPackage()
        # self.game_window.fill("Black")

        # Handles keyboard inputs
        self.get_keyboard_input()

        # Handles pygame events
        self.handle_events()

        # Update various elements on screen
        self.render_game(render_package["level"])
        pygame.display.update()
        return self.return_package

    def close_window(self):
        pygame.quit()
