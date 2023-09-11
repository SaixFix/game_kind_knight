import arcade

from gui import get_double_jump_message, start_message
from settings import *
import os
import arcade.gui

from utils import PlayerCharacter


class MyGame(arcade.Window):
    """ Main application class."""

    def __init__(self, screen_width: int, screen_height: int, screen_title: str, fullscreen: bool):
        # Вызываем родительский класс и передаем параметры окна
        super().__init__(screen_width, screen_height, screen_title, fullscreen)

        # Данное указание каталога требуется для запуска
        # запуска с помощью команды "python -m"
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Create and enable the UIManager
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        self.double_jump_get = False
        # The counter can be used for multi jump
        self.jumps_since_ground = 0

        # Keep track of the score
        self.die_score = 0
        self.gold_score = 0

        # Do we need to reset the score?
        self.reset_score = True

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = 1

        self.player_start_x = PLAYER_START_X
        self.player_start_y = PLAYER_START_Y

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        """Настройте игру здесь. Вызовите эту функцию, чтобы перезапустить игру."""
        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Map name
        map_name = f"./data/levels/level_{self.level}.tmx"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DISAPPEAR_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_DIE_BLOCK: {
                "use_spatial_hash": False,
            },

            LAYER_NAME_CHEST: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_CHECK_POINTS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_SKY: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_GROUND: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND2: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DIE_BLOCK: {
                "use_spatial_hash": True,
            },
        }

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score, make sure we keep the score if the player finishes a level
        if self.reset_score:
            self.die_score = 0
        self.reset_score = True

        # Add Player Spritelist before "Foreground" layer. This will make the foreground
        # be drawn after the player, making it appear to be in front of the Player.
        # Setting before using scene.add_sprite allows us to define where the SpriteList
        # will be in the draw order. If we just use add_sprite, it will be appended to the
        # end of the order.
        self.scene.add_sprite_list_after("Player", LAYER_NAME_PLATFORMS)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)
        start_message(arcade, self.manager)

        # --- Load in a map from the tiled editor ---

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_DIE_BLOCK],
            ladders=self.scene[LAYER_NAME_LADDERS],
            gravity_constant=GRAVITY,
            walls=self.scene[LAYER_NAME_PLATFORMS],
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # For draw GUI
        self.manager.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Die Score: {self.die_score}"
        arcade.draw_text(
            score_text,
            200,
            1050,
            arcade.csscolor.BLACK,
            18,
        )

        score_text = f"Gold Score: {self.gold_score}"
        arcade.draw_text(
            score_text,
            0,
            1050,
            arcade.csscolor.YELLOW,
            18,
        )

        # Draw hit boxes.

        # self.player_sprite.draw_hit_box(arcade.color.RED, 3)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = MOVEMENT_SPEED
            elif (
                    self.physics_engine.can_jump(y_distance=10)
                    and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = JUMP_SPEED
                # Активируем счетчик иначе прыжки будут бесконечны
                self.physics_engine.increment_jump_counter()
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """
        Вызывается при каждом движении мыши.
        """
        if key == arcade.key.SPACE or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """
        Вызывается, когда пользователь отпускает клавишу.
        """
        if key == arcade.key.SPACE or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        """
        Центрует камеру на персонаже игрока
        """
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
                self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered, 0.2)

    def on_update(self, delta_time):
        """Передвижение и игровая логика"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

            # Update Animations
            self.scene.update_animation(
                delta_time, [
                    LAYER_NAME_CHEST,
                    LAYER_NAME_BACKGROUND,
                    LAYER_NAME_PLAYER,
                    LAYER_NAME_CHECK_POINTS,
                    LAYER_NAME_DISAPPEAR_PLATFORMS,
                ]
            )

        # Update walls, used with moving platforms
        self.scene.update([LAYER_NAME_MOVING_DIE_BLOCK])

        # Add double jump
        if self.double_jump_get:
            self.physics_engine.enable_multi_jump(2)

        # See if we hit any chest
        chest_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_CHEST]
        )

        # Loop through each chest we hit (if any) and remove it
        for chest in chest_hit_list:
            if 'double_jump' in chest.properties:
                self.double_jump_get = True
                # get pop_up message
                get_double_jump_message(arcade, self.manager)
            if 'cost' in chest.properties:
                self.gold_score += int(chest.properties['cost'])
                # Play a sound
                arcade.play_sound(self.collect_coin_sound)
            # Remove the chest
            chest.remove_from_sprite_lists()

        # See if we hit any chest
        d_platforms_hit_list = arcade.check_for_collision_with_list(
             self.player_sprite, self.scene[LAYER_NAME_DISAPPEAR_PLATFORMS]
        )

        # Loop through each platforms we hit (if any) and remove it
        for platforms in d_platforms_hit_list:
            # platforms the chest
            platforms.remove_from_sprite_lists()


            # See if we hit any check_point
        check_point_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_CHECK_POINTS]
        )

        # Loop through each check_point we hit
        for check_point in check_point_hit_list:
            self.player_start_x = check_point.center_x
            self.player_start_y = check_point.center_y
            print(f'checkpoint x, y: {check_point.center_x}, {check_point.center_y}')
            print(f'player_start x, y: {self.player_start_x}, {self.player_start_y}')

            # Remove the coin
            # check_point.remove_from_sprite_lists()

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = self.player_start_x
            self.player_sprite.center_y = self.player_start_y

            arcade.play_sound(self.game_over)

        # Did the player touch something they should not?
        if arcade.check_for_collision_with_list(
                self.player_sprite, self.scene[LAYER_NAME_DIE_BLOCK]

        ) or arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_MOVING_DIE_BLOCK]

        ):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = self.player_start_x
            self.player_sprite.center_y = self.player_start_y
            self.die_score += 1

            arcade.play_sound(self.game_over)

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.end_of_map:
            # Advance to the next level
            self.level += 1

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

            # Load the next level
            self.setup()

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main функция"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULL_SCREEN)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
