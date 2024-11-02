import json
from dataclasses import dataclass
from typing import Optional, Tuple, List
import pygame

"""
Class to render the game to the screen
"""

# TODO: Figure out why enemies not showing
# TODO: Health bars for enemies
# TODO: Show lives and money
# TODO: Rotate the tower sprite to point towards the enemy
# TODO: Render the bullet of the tower
# TODO: Features to add: upgrade tower, sell tower, buy tower
# TODO: menu to start new game, pause game, exit game


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
        sprite.set_colorkey((0, 0, 0))
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


class Background:
    """ Class to make the background of the game sprites"""

    def __init__(self, object_terrain: List[List[object]]):
        self.bg_width = SCREEN_WIDTH
        self.bg_height = SCREEN_HEIGHT

        self.bg: pygame.Surface = pygame.Surface((self.bg_width, self.bg_height))
        self.object_terrain = object_terrain
        self.block_size = self.calculate_block_size()

    def calculate_block_size(self):
        block_size_x = self.bg_width // len(self.object_terrain[0])
        block_size_y = self.bg_height // len(self.object_terrain)
        return min(block_size_x, block_size_y)


    def construct_sprite_matrix(self) -> List[List[Sprite]]:
        from Engine.level import TerrainBlock

        object_sprite_map = {
            0: ["ground", "dirt"],
            1: ["ground", "tower"],
            2: ["ground", "grass"],
        }

        sprite_matrix = []
        for row in self.object_terrain:
            sprite_row = []
            for sprite_object in row:
                if isinstance(sprite_object, TerrainBlock):
                    sprite_category, sprite_type = object_sprite_map[sprite_object.block_type]
                    sprite = Sprite(sprite_category, sprite_type)
                    sprite_row.append(sprite)
                else:
                    # Just render grass for now
                    sprite = Sprite("ground", "grass")
                    sprite_row.append(sprite)

            sprite_matrix.append(sprite_row)

        return sprite_matrix

    def construct_background(self, sprite_matrix: List[List[Sprite]]):
        for y, row in enumerate(sprite_matrix):
            for x, sprite in enumerate(row):
                self.bg.blit(sprite.get_sprite(), (x * self.block_size, y * self.block_size))

    def create_background(self):
        sprite_matrix = self.construct_sprite_matrix()
        self.construct_background(sprite_matrix)

    def get_background(self):
        return self.bg


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
        self.terrain_dict = {}
        self.updated_terrain = False

        self.block_size: int = 0

        # Get the game window to show up
        self.create_game_window()

        # Make background object
        self.background: Optional[Background] = None

    def turn_tower(self, tower, sprite: Sprite):
        from Engine.tower import Tower
        tower: Tower = tower

        # Get the current angle and rotate back to 0
        old_angle = tower.old_rotation
        sprite.rotate_sprite(-old_angle)

        # Now rotate to the new angle
        new_angle = tower.new_rotation
        sprite.rotate_sprite(new_angle)

        return sprite

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

        # TODO: move this, so we do it only once
        self.block_size = min(self.screen_width // len(level.terrain[0]), self.screen_height // len(level.terrain))

        # List of towers, to show each tower's shooting range
        tower_list = []

        # Sprite info
        sprite_category = ""
        sprite_type = ""
        enemy_action = ""
        tower_level = ""
        size = (self.block_size, self.block_size)

        for i, row in enumerate(level.terrain):
            for j, sq in enumerate(row):

                # If previous block = current block, skip it
                if self.updated_terrain and self.terrain_dict[(i, j)] == sq and not (isinstance(sq, Tower)):
                    # TODO: circle ?
                    continue

                # Prepare relevant sprite info to be displayed
                if isinstance(sq, TerrainBlock):
                    if sq.block_type == 0:  # Enemy path
                        sprite_category = "ground"
                        sprite_type = "dirt"
                    if sq.block_type == 1:  # Empty tower block
                        sprite_category = "ground"
                        sprite_type = "tower"
                    if sq.block_type == 2:  # Static block
                        sprite_category = "ground"
                        sprite_type = "grass"
                elif isinstance(sq, Enemy):
                    sprite_category = "enemies"
                    sprite_type = "normal"
                    enemy_action = "run"
                elif isinstance(sq, Tower):
                    sprite_category = "towers"
                    sprite_type = "normal"
                    tower_level = "0"

                # Create current sprite, and save it to sprite dictionary
                sq_sprite = Sprite(sprite_category=sprite_category, sprite_type=sprite_type,
                                   enemy_action=enemy_action,
                                   tower_level=tower_level, size=size)

                # If the sprite is a tower handle rotation
                if isinstance(sq, Tower):
                    sq_sprite = self.turn_tower(sq, sq_sprite)
                    print(sq.old_rotation, sq.new_rotation)

                self.sprite_dict[(i, j)] = sq_sprite
                self.terrain_dict[(i, j)] = sq

                # TODO: Highlight player base in some way, but only once

                # Create rectangle as container for the sprite
                sq_rect = pygame.Rect(SCREEN_X_POS + (j * self.block_size), SCREEN_Y_POS + (i * self.block_size),
                                      self.block_size, self.block_size)

                # Draw the sprite on the screen
                self.game_window.blit(sq_sprite.get_sprite(), sq_rect)

                # If current block is a tower, add it to the list of towers (to show shooting range)
                if isinstance(sq, Tower):
                    tower_list.append([sq, sq_rect, "Blue"])

        self.updated_terrain = True

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
        self.game_window.fill("Red")

        # Handles keyboard inputs
        self.get_keyboard_input()

        # Handles pygame events
        self.handle_events()

        # Create background if it is not created
        if self.background is None:
            self.background = Background(render_package["level"].terrain)
            self.background.create_background()

        self.game_window.blit(self.background.get_background(), (SCREEN_X_POS, SCREEN_Y_POS))

        enemy_sprite = Sprite("enemies", "normal", "run")
        self.game_window.blit(enemy_sprite.get_sprite(), (SCREEN_X_POS + 100, SCREEN_Y_POS + 230))

        # Update various elements on screen
        # self.render_game(render_package["level"])
        pygame.display.update()

        # Draw shooting line
        # turret_pos = render_package["level"].towers[0].position
        # bullet_vector = render_package["level"].towers[0].bullet_vector
        #
        # pygame.draw.line(self.game_window, "Red", (
        # turret_pos[1] * self.block_size + self.block_size // 2, turret_pos[0] * self.block_size + self.block_size // 2),
        #                  (turret_pos[1] * self.block_size + self.block_size // 2 + bullet_vector[
        #                      1] * self.block_size * 2,
        #                   turret_pos[0] * self.block_size + self.block_size // 2 + bullet_vector[
        #                       0] * self.block_size * 2), width=2)

        return self.return_package

    def close_window(self):
        pygame.quit()
