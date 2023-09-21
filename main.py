from typing import Optional

import arcade
from arcade.experimental.uislider import UISlider
from arcade.gui import UILabel, UIOnChangeEvent, UITextureButton

from gui import get_double_jump_message, start_message
from other_views import MainMenu, PauseView
from settings import *
import os
import arcade.gui

from units import PlayerCharacter


class GameView(arcade.View):
    """ Main application class."""

    def __init__(self):
        # Вызываем родительский класс и передаем параметры окна
        super().__init__()

        # Данное указание каталога требуется для запуска
        # запуска с помощью команды "python -m"
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        # Create and enable the UIManager
        self.manager: 'UIManager' = arcade.gui.UIManager()
        self.manager.enable()

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.jump_needs_reset: bool = False

        # Our TileMap Object
        self.tile_map: Optional['TileMap'] = None

        # Our Scene Object
        self.scene: Optional['Scene'] = None

        # Separate variable that holds the player sprite
        self.player_sprite: Optional[PlayerCharacter] = None

        # Our physics engine
        self.physics_engine: Optional['PhysicsEnginePlatformer'] = None

        # A Camera that can be used for scrolling the screen
        self.camera: Optional['Camera'] = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera: Optional['Camera'] = None

        self.double_jump_get: bool = False
        # The counter can be used for multi jump
        self.jumps_since_ground: int = 0

        # Keep track of the score
        self.die_score: int = 0
        self.gold_score: int = 0

        # Do we need to reset the score?
        self.reset_score: bool = True

        # Where is the right edge of the map?
        self.end_of_map: int = 0

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
            start_x=SCREEN_WIDTH // 2,
            start_y=1050,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_x="center"
        )
        # settings sound volume
        self.sound_volume: float = 0.5

        # Load button textures
        settings = arcade.load_texture("./data/textures/UI/settings.png")
        settings_hover = arcade.load_texture("./data/textures/UI/settings_hover.png")

        # bottons settings

        # # sound slider
        # self.v_box = arcade.gui.UIBoxLayout()
        # self.ui_slider = UISlider(value=50, width=300, height=50)
        #
        # label_down = UILabel(text=f"{self.ui_slider.value:02.0f}")
        # label_up = UILabel(text=f"Sound volume")
        #
        # self.v_box.add(child=label_up, align_y=100)
        # self.v_box.add(child=self.ui_slider)
        # self.v_box.add(child=label_down, align_y=100)

        self.settings_button = UITextureButton(SCREEN_WIDTH - 30, SCREEN_HEIGHT - 35, texture=settings,
                                               texture_hovered=settings_hover)
        self.manager.add(self.settings_button)

        # button style
        style = {'bg_color': (139, 69, 19), "font_color": arcade.color.WHITE, "font_name": ("Comic Sans MS",)}

        # Load sounds
        self.collect_coin_sound: 'Sound' = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound: 'Sound' = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over: 'Sound' = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.trap_dead: 'Sound' = arcade.load_sound("./data/sounds/scream_hurt.mp3")

        # for sound slider
        # @self.ui_slider.event()
        # def on_change(event: UIOnChangeEvent):
        #     label_down.text = f"{self.ui_slider.value:02.0f}"
        #     label_down.fit_content()

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

    def on_show_view(self):
        self.setup()

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

        # Draw the timer text
        self.timer_text.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text: str = f"Die Score: {self.die_score}"
        arcade.draw_text(
            score_text,
            200,
            1050,
            arcade.csscolor.RED,
            18,
        )

        score_text: str = f"Gold Score: {self.gold_score}"
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
                arcade.play_sound(self.jump_sound, volume=self.sound_volume)
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
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered, 0.2)

    def on_update(self, delta_time):
        """Передвижение и игровая логика"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # sounds volume
        # self.sound_volume = round((self.ui_slider.value / 100), 1)

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
                arcade.play_sound(self.collect_coin_sound, volume=self.sound_volume)
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

            # Remove the coin
            # check_point.remove_from_sprite_lists()

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = self.player_start_x
            self.player_sprite.center_y = self.player_start_y

            arcade.play_sound(self.trap_dead, volume=self.sound_volume)

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

            arcade.play_sound(self.trap_dead, volume=self.sound_volume)

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
    # window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # menu_view = MainMenu(GameView())
    # window.show_view(menu_view)
    # print('hello')
    # arcade.run()

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_menu_view = MainMenu(GameView())
    window.show_view(main_menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
