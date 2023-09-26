from typing import Optional

import arcade
from arcade.gui import UILabel
from pyglet.math import Vec2
from arcade.experimental.lights import Light, LightLayer

from gui.game_ui import GameUiAssets
from ui_message import get_double_jump_message, start_message
from other_views import MainMenu, PauseView, SettingsView, LoadingView
from settings import *
import os
import arcade.gui

from units import PlayerCharacter


class GameWindow(arcade.Window):
    def __init__(self, screen_wight, screen_height, screen_title, full_screen):
        super().__init__(screen_wight, screen_height, screen_title, full_screen)

        # all views
        self.loading_view = LoadingView()
        self.main_menu = MainMenu()
        self.game_view = GameView()
        self.settings_view = SettingsView()
        self.show_view(self.main_menu)

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.sound_value: float = 0.5


class GameView(arcade.View):
    """ Main application class."""

    def __init__(self):
        # Вызываем родительский класс и передаем параметры окна
        super().__init__()

        # Данное указание каталога требуется для запуска
        # запуска с помощью команды "python -m"
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Used for scrolling
        self.view_left = 0
        self.view_bottom = 0

        # --- Light related ---
        # List of all the lights
        self.light_layer = None
        # Individual light we move with player, and turn on/off
        self.player_light = None

        # Create the UIManager
        self.manager = arcade.gui.UIManager()
        # GameUiAssets consist of all UI elements
        gui_items = GameUiAssets(self.manager, self.window)
        # Get manager with all UI elements
        self.manager = gui_items.game_ui()

        # Keep track of the score
        self.die_score: int = 0
        self.gold_score: int = 0

        # UI scores elements
        self.gold_score_ui = gui_items.gold_scores_ui(self.gold_score)
        self.die_score_ui = gui_items.die_score_ui(self.die_score)

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.jump_needs_reset: bool = False

        # Our TileMap Object
        self.tile_map: Optional[arcade.TileMap] = None

        # Height and wight map in pixels
        self.map_height: int = 0
        self.map_width: int = 0

        # Our Scene Object
        self.scene: Optional[arcade.Scene] = None

        # Separate variable that holds the player sprite
        self.player_sprite: Optional[PlayerCharacter] = None

        # Our physics engine
        self.physics_engine: Optional[arcade.PhysicsEnginePlatformer] = None

        # A Camera that can be used for scrolling the screen
        self.camera: Optional[arcade.Camera] = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera: Optional[arcade.Camera] = None

        self.double_jump_get: bool = False
        # The counter can be used for multi jump
        self.jumps_since_ground: int = 0

        # Do we need to reset the score?
        self.reset_score: bool = True

        # Level
        self.level: int = 1

        # Player start position
        self.player_start_x: int = PLAYER_START_X
        self.player_start_y: int = PLAYER_START_Y

        # For timer on screen
        self.total_time: float = 0.0
        # Timer on-screen, spend time.
        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=self.window.width // 2,
            start_y=self.window.height - 35,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_x="center"
        )

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.trap_dead = arcade.load_sound("./data/sounds/scream_hurt.mp3")

    def on_message_box_close(self, button_text):
        print(f"User pressed {button_text}.")

    def setup(self):
        """Настройте игру здесь. Вызовите эту функцию, чтобы перезапустить игру."""
        # Set up the Cameras
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)

        # Map name
        map_name: str = f"./data/levels/level_{self.level}.tmx"

        # Layer Specific Options for the Tilemap
        layer_options: dict = LAYER_OPTIONS

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Create a light layer, used to render things to, then post-process and
        # add lights. This must match the screen size.
        self.light_layer = LightLayer(self.window.width, self.window.height)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.light_layer.set_background_color(arcade.color.BLACK)

        # Create a small white light
        x = 2855
        y = 127
        radius = 30
        mode = 'soft'
        color = arcade.csscolor.LIGHT_GOLDENROD_YELLOW
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        # Create a light to follow the player around.
        # We'll position it later, when the player moves.
        # We'll only add it to the light layer when the player turns the light
        # on. We start with the light off.
        radius = 150
        mode = 'soft'
        color = arcade.csscolor.WHITE_SMOKE
        self.player_light = Light(0, 0, radius, color, mode)

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

        # Calculate and set height and wight map in pixels
        self.map_height = self.tile_map.height * 64
        self.map_width = self.tile_map.width * 64

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

    def on_show_view(self):
        """
        Activate when call
        """
        # call self setup
        self.window.game_view.setup()
        # UI manager enable
        self.manager.enable()

    def on_hide_view(self):
        """
         Activate when call other view
        """
        # UI manager disable
        self.manager.disable()

    def on_draw(self):
        """Render the screen."""

        # # Clear the screen to the background color
        # self.clear()
        #
        # # Activate the game camera
        # self.camera.use()
        #
        # # Draw our Scene
        # self.scene.draw()
        #
        # # Activate the GUI camera before drawing GUI elements
        # self.gui_camera.use()
        #
        # # For draw GUI
        # self.manager.draw()
        #
        # # Draw the timer text
        # self.timer_text.draw()

        # Activate the game camera
        self.camera.use()
        # --- Light related ---
        # Everything that should be affected by lights gets rendered inside this
        # 'with' statement. Nothing is rendered to the screen yet, just the light
        # layer.
        with self.light_layer:
            self.scene[LAYER_NAME_BACKGROUND].draw()
            self.scene.draw()
            self.scene[LAYER_NAME_PLAYER].draw()

        # Draw the light layer to the screen.
        # This fills the entire screen with the lit version
        # of what we drew into the light layer above.
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        # Now draw anything that should NOT be affected by lighting.
        arcade.draw_text("Press F to turn character light on/off.",
                         10 + self.view_left, 10 + self.view_bottom,
                         arcade.color.WHITE, 20)

        # Activate the game camera
        self.camera.use()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # For draw GUI
        self.manager.draw()

        # Draw the timer text
        self.timer_text.draw()

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
                arcade.play_sound(self.jump_sound, volume=self.window.sound_value)
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
        elif key == arcade.key.F:
            # --- Light related ---
            # We can add/remove lights from the light layer. If they aren't
            # in the light layer, the light is off.
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)

        # Did the user want to pause?
        elif key == arcade.key.ESCAPE:
            # Pass the current view to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)

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
        if screen_center_x > self.map_width - self.window.width:
            screen_center_x = self.map_width - self.window.width
        if screen_center_y > self.map_height - self.window.height:
            screen_center_y = self.map_height - self.window.height
        player_centered = Vec2(screen_center_x, screen_center_y)

        self.camera.move_to(player_centered, 0.2)

    def on_update(self, delta_time):
        """Передвижение и игровая логика"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # --- Light related ---
        # We can easily move the light by setting the position,
        # or by center_x, center_y.
        self.player_light.position = self.player_sprite.position

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

        # Accumulate the total time
        self.total_time += delta_time

        # Calculate minutes
        minutes: int = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds: int = int(self.total_time) % 60

        # Calculate 100s of a second
        seconds_100s: int = int((self.total_time - seconds) * 100)

        # Use string formatting to create a new text string for our timer
        self.timer_text.text = f"Wasted time: {minutes:02d}:{seconds:02d}:{seconds_100s:02d}"

        self.die_score_ui.text = f" Die Score: {self.die_score} "

        self.gold_score_ui.text = f" Gold Score: {self.gold_score} "

        # Add double jump
        if self.double_jump_get:
            self.physics_engine.enable_multi_jump(2)

        # See if we hit any chest
        chest_hit_list: list = arcade.check_for_collision_with_list(
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
                arcade.play_sound(self.collect_coin_sound, volume=self.window.sound_value)
            # Remove the chest
            chest.remove_from_sprite_lists()

        # See if we hit any chest
        d_platforms_hit_list: list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_DISAPPEAR_PLATFORMS]
        )

        # Loop through each platforms we hit (if any) and remove it
        for platforms in d_platforms_hit_list:
            # platforms the chest
            platforms.remove_from_sprite_lists()

            # See if we hit any check_point
        check_point_hit_list: list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_CHECK_POINTS]
        )

        # Loop through each check_point we hit
        for check_point in check_point_hit_list:
            self.player_start_x = check_point.center_x
            self.player_start_y = check_point.center_y
            print(f'checkpoint x, y: {check_point.center_x}, {check_point.center_y}')
            print(f'player_start x, y: {self.player_start_x}, {self.player_start_y}')

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = self.player_start_x
            self.player_sprite.center_y = self.player_start_y

            arcade.play_sound(self.trap_dead, volume=self.window.sound_value)

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

            arcade.play_sound(self.trap_dead, volume=self.window.sound_value)

        # See if the user got to the end of the level
        if self.player_sprite.center_x >= self.map_width:
            # Advance to the next level
            # self.level += 1
            #
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = self.player_start_x
            self.player_sprite.center_y = self.player_start_y

            # Make sure to keep the score from this level when setting up the next level
            self.reset_score = False

            # Load the next level
            self.setup()

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULL_SCREEN)
    arcade.run()


if __name__ == "__main__":
    main()
