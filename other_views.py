import arcade
from arcade.experimental.uislider import UISlider
from arcade.gui import UILabel, UIOnChangeEvent, UITextureButton

from settings import *


class MainMenu(arcade.View):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()

        # Background image
        self.background = arcade.load_texture("./data/textures/background.png") \
 \
            # Background music
        self.music = arcade.load_sound('./data/sounds/background_music_menu.mp3')
        self.media_player = self.music.play()
        self.media_player.volume = 0.5

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()

        # Load button textures
        start = arcade.load_texture("./data/textures/UI/start.png")
        start_hover = arcade.load_texture("./data/textures/UI/start_hover.png")
        start_pressed = arcade.load_texture("./data/textures/UI/start_pressed.png")

        settings = arcade.load_texture("./data/textures/UI/settings_main_menu.png")
        settings_hover = arcade.load_texture("./data/textures/UI/settings_main_menu_hover.png")
        settings_pressed = arcade.load_texture("./data/textures/UI/settings_main_menu_pressed.png")

        exit_button = arcade.load_texture("./data/textures/UI/exit.png")
        exit_hover = arcade.load_texture("./data/textures/UI/exit_hover.png")
        exit_pressed = arcade.load_texture("./data/textures/UI/exit_pressed.png")

        template_button = arcade.load_texture("./data/textures/UI/template_button.png")

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UITextureButton(
            texture=start,
            texture_hovered=start_hover,
            texture_pressed=start_pressed,
            text="Start Game",
            width=200,
            height=50
        )
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UITextureButton(
            texture=settings,
            texture_hovered=settings_hover,
            texture_pressed=settings_pressed,
            text="Settings",
            width=200,
            height=50
        )
        self.v_box.add(settings_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UITextureButton(
            texture=exit_button,
            texture_hovered=exit_hover,
            texture_pressed=exit_pressed,
            text="Exit",
            width=200,
            height=50
        )
        self.v_box.add(exit_button.with_space_around(bottom=20))

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box))

        # Create the audio slider
        style_slider = {'normal_bg': (255, 0, 0)}
        self.ui_slider = UISlider(
            x=0,
            y=50,
            value=50,
            width=200,
            height=30,
            style=style_slider
        )
        label_down = UILabel(text=f"{self.ui_slider.value:02.0f}")
        label_up = UILabel(text=f"Sound volume")

        self.manager.add(self.ui_slider)

        # background textures for audio slider
        slider_textures = arcade.gui.UITexturePane(
            tex=template_button,
            child=self.ui_slider
        )

        self.manager.add(slider_textures)

        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start
        settings_button.on_click = self.on_click_settings
        exit_button.on_click = self.on_click_exit

        # for sound slider
        @self.ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label_down.text = f"{self.ui_slider.value:02.0f}"
            label_down.fit_content()
            self.media_player.volume = round((self.ui_slider.value / 100), 1)

    def on_show_view(self):
        """Called when switching to this view."""
        self.manager.enable()
        self.media_player.play()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        """Draw the menu"""
        self.clear()

        # Draw background image
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.manager.draw()

    def on_click_start(self, event):
        print("Start:", event)
        self.window.show_view(self.window.game_view)

    @staticmethod
    def on_click_exit(event):
        print("Exit:", event)
        arcade.exit()

    def on_click_settings(self, event):
        self.window.show_view(self.window.settings_view)


# class GameOverView(arcade.View):
#     """Class to manage the game overview"""
#
#     def __init__(self, game_view: 'GameView'):
#         super().__init__()
#
#         # Main Game view
#         self.game_view: Optional['GameView'] = game_view
#
#     def on_show_view(self):
#         """Called when switching to this view"""
#         arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
#
#     def on_draw(self):
#         """Draw the game overview"""
#         self.clear()
#         arcade.draw_text(
#             "Game Over - Click to restart",
#             SCREEN_WIDTH / 2,
#             SCREEN_HEIGHT / 2,
#             arcade.color.WHITE,
#             30,
#             anchor_x="center",
#         )
#
#     def on_mouse_press(self, _x, _y, _button, _modifiers):
#         """Use a mouse press to advance to the 'game' view."""
#         self.window.show_view(self.game_view())


class PauseView(arcade.View):
    """Shown when the game is paused"""

    def __init__(self, game_view: arcade.View) -> None:
        """Create the pause screen"""
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semitransparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self) -> None:
        """Draw the underlying screen, blurred, then the Paused text"""

        # First, draw the underlying view
        # This also calls start_render(), so no need to do it again
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            left=self.window.width - self.window.width,
            right=SCREEN_WIDTH,
            top=SCREEN_HEIGHT,
            bottom=SCREEN_HEIGHT - SCREEN_HEIGHT,
            color=self.fill_color,
        )

        # Now show the Pause text
        arcade.draw_text(
            "PAUSED - ESC TO CONTINUE",
            start_x=0 + 500,
            start_y=0 + 300,
            color=arcade.color.INDIGO,
            font_size=40,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Resume the game when the user presses ESC again

        Arguments:
            key -- Which key was pressed
            modifiers -- What modifiers were active
        """
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)


class SettingsView(arcade.View):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        template_button = arcade.load_texture("./data/textures/UI/template_button.png")
        template_hover = arcade.load_texture("./data/textures/UI/template_button_hover.png")
        template_pressed = arcade.load_texture("./data/textures/UI/template_button_pressed.png")

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # create buttons
        main_menu_button = arcade.gui.UITextureButton(
            texture=template_button,
            texture_hovered=template_hover,
            texture_pressed=template_pressed,
            text="Main Menu",
            width=200,
            height=50
        )
        self.v_box.add(main_menu_button.with_space_around(bottom=20))

        back_to_game_button = arcade.gui.UITextureButton(
            texture=template_button,
            texture_hovered=template_hover,
            texture_pressed=template_pressed,
            text="Game",
            width=200,
            height=50
        )
        self.v_box.add(back_to_game_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UITextureButton(
            texture=template_button,
            texture_hovered=template_hover,
            texture_pressed=template_pressed,
            text="Exit",
            width=200,
            height=50
        )
        self.v_box.add(exit_button.with_space_around(bottom=20))

        # assign self.on_click_start as callback
        main_menu_button.on_click = self.main_menu_button_on
        back_to_game_button.on_click = self.game_button_on
        exit_button.on_click = self.on_click_exit

        # Create the audio slider
        self.ui_slider = UISlider(value=50, width=300, height=50)
        label_down = UILabel(text=f"{self.ui_slider.value:02.0f}")
        label_up = UILabel(text=f"Sound volume")

        self.v_box.add(child=label_up, align_y=100)
        self.v_box.add(child=self.ui_slider)
        self.v_box.add(child=label_down, align_y=100)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box))

        # for sound slider
        @self.ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label_down.text = f"{self.ui_slider.value:02.0f}"
            label_down.fit_content()
            self.window.sound_value = round((self.ui_slider.value / 100), 1)

    @staticmethod
    def on_click_exit(event):
        print("Exit:", event)
        arcade.exit()

    def main_menu_button_on(self, event):
        self.window.show_view(self.window.main_menu)

    def game_button_on(self, event):
        self.window.show_view(self.window.game_view)

    def on_show_view(self):
        """Called when switching to this view."""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
