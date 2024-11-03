import json
from dataclasses import dataclass
from typing import Optional, Tuple, List
import pygame

"""
Class to render the game to the screen
"""

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


def calculate_block_size():
    block_size_x = SCREEN_WIDTH // 20
    block_size_y = SCREEN_HEIGHT // 10
    return min(block_size_x, block_size_y)


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
        self.rotated_sprite_object: Optional[pygame.Surface] = None
        self.init_sprite()

    def extract_sprite(self, sprite_sheet: pygame.Surface, x: int, y: int) -> pygame.Surface:
        sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
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
        self.rotated_sprite_object = sprite

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

    def rotate_sprite(self, angle: int) -> pygame.Rect:
        # First rotate the object then get the previous center point because
        # when the rect of the sprite is rotated anything else than 90 degrees it cannot fit into original rect
        # And thus will be off centered: max off center is square root of 2 times the original rect
        self.rotated_sprite_object = pygame.transform.rotate(self.sprite_object, angle)
        original_rect = self.sprite_object.get_rect()
        return self.rotated_sprite_object.get_rect(center=original_rect.center)


class Background:
    """ Class to make the background of the game sprites"""

    def __init__(self, object_terrain: List[List[object]]):
        self.bg_width = SCREEN_WIDTH
        self.bg_height = SCREEN_HEIGHT

        self.bg: pygame.Surface = pygame.Surface((self.bg_width, self.bg_height))
        self.object_terrain = object_terrain
        self.block_size = calculate_block_size()

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

        self.block_size: int = calculate_block_size()

        self.lives: int = 0
        self.lives_font: object = None
        self.lives_text: object = None
        self.money: int = 0
        self.money_font: object = None
        self.money_text: object = None

        # Get the game window to show up
        self.create_game_window()

        # Make background object
        self.background: Optional[Background] = None

        self.temp_tower = Sprite("towers", "normal", tower_level="0")

    def turn_tower(self, tower, sprite: Sprite) -> Tuple[Sprite, pygame.Rect]:
        """
        Turns the tower then returns the sprite and the new x,y position needed for correct alignment
        :param tower:
        :param sprite:
        :return:
        """
        from Engine.tower import Tower
        tower: Tower = tower

        # Now rotate to the new angle
        new_angle = tower.angle
        rotated_rect = sprite.rotate_sprite(new_angle)

        return sprite, rotated_rect

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

    def draw_health_bar(self, enemy):

        health_bar_width = int((enemy.current_hp / enemy.max_hp) * self.block_size)
        health_bar_height = self.block_size // 6

        health_bar_x_pos = SCREEN_X_POS + (enemy.position[1] * self.block_size)
        health_bar_y_pos = SCREEN_Y_POS + (enemy.position[0] * self.block_size)
        health_rect = pygame.Rect(health_bar_x_pos, health_bar_y_pos, health_bar_width, health_bar_height)

        return health_rect

    def render_enemies(self, enemies: List[object]):
        from Engine.enemy import Enemy
        enemies: List[Enemy] = enemies

        sprite_category = "enemies"

        for enemy in enemies:
            sprite_type = "normal"
            enemy_action = "run"

            enemy_sprite = Sprite(sprite_category=sprite_category, sprite_type=sprite_type, enemy_action=enemy_action,
                                  size=(self.block_size, self.block_size))

            enemy_x_pos = self.block_size * enemy.position[1] + SCREEN_X_POS
            enemy_y_pos = self.block_size * enemy.position[0] + SCREEN_Y_POS

            self.game_window.blit(enemy_sprite.get_sprite(), (enemy_x_pos, enemy_y_pos))

            health_bar = self.draw_health_bar(enemy)

            pygame.draw.rect(self.game_window, "Red", health_bar)

    def render_towers(self, towers: List[object]):
        from Engine.tower import Tower
        towers: List[Tower] = towers

        sprite_category = "towers"

        for tower in towers:
            sprite_type = "normal"
            tower_level = str(tower.tower_level)

            tower_sprite = Sprite(sprite_category=sprite_category, sprite_type=sprite_type, tower_level=tower_level,
                                  size=(self.block_size, self.block_size))

            # Check turret rotation
            tower_sprite, rotated_rect = self.turn_tower(tower, tower_sprite)

            tower_x_pos = self.block_size * tower.position[1] + SCREEN_X_POS
            tower_y_pos = self.block_size * tower.position[0] + SCREEN_Y_POS

            # TODO: If condition might not be needed because rotated_rect is never None
            if rotated_rect is not None:
                self.game_window.blit(tower_sprite.rotated_sprite_object, (tower_x_pos + rotated_rect.topleft[0], tower_y_pos + rotated_rect.topleft[1]))
            else:
                self.game_window.blit(tower_sprite.rotated_sprite_object, (tower_x_pos, tower_y_pos))

            tower_center_pos = (tower_x_pos + self.block_size // 2, tower_y_pos + self.block_size // 2)

            pygame.draw.circle(self.game_window, "Blue", tower_center_pos, tower.range * self.block_size, width=1)

    def render_player_info(self, cur_lives, cur_money):
        if not self.lives and not self.money:
            self.lives_font = pygame.font.Font(None, self.block_size // 2)
            self.money_font = pygame.font.Font(None, self.block_size // 2)

        self.lives = cur_lives
        self.money = cur_money

        # Display current lives and gold
        self.lives_text = self.lives_font.render(f"Lives : {self.lives}", True, "Red")
        self.money_text = self.money_font.render(f"Gold : {self.money}", True, "darkgoldenrod1")

        # TODO: Draw a rectangle where money and lives will be displayed so it is easier to read

        self.game_window.blit(self.lives_text, (self.block_size, self.block_size // 2))
        self.game_window.blit(self.money_text, (self.block_size, self.block_size))

    def render_game(self, render_package: dict):
        # Render enemies
        enemy_list = render_package["level"].enemies
        self.render_enemies(enemy_list)

        # Render towers, and their current shooting range
        tower_list = render_package["level"].towers
        self.render_towers(tower_list)

        # Render current lives and money
        cur_lives = render_package["lives"]
        cur_money = render_package["money"]
        self.render_player_info(cur_lives, cur_money)

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

        # enemy_sprite = Sprite("enemies", "normal", "run")
        # self.game_window.blit(enemy_sprite.get_sprite(), (SCREEN_X_POS + 100, SCREEN_Y_POS + 230))

        # self.game_window.blit(self.temp_tower.rotated_sprite_object, (SCREEN_X_POS + 100, SCREEN_Y_POS + 230))
        # self.temp_tower.rotate_sprite(90)

        # Update various elements on screen
        self.render_game(render_package)
        pygame.display.update()

        return self.return_package

    def close_window(self):
        pygame.quit()
