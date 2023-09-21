from typing import Optional

import arcade
from arcade.experimental.uislider import UISlider
from arcade.gui import UILabel, UIOnChangeEvent, UITextureButton

from settings import *


class MainMenu(arcade.View):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()
        # self.game_view: arcade.View = game_view

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings(в разработке)", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=200)
        self.v_box.add(exit_button.with_space_around(bottom=20))

        # Create the slider
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

        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start
        settings_button.on_click = self.on_click_settings
        exit_button.on_click = self.on_click_exit

        @self.ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label_down.text = f"{self.ui_slider.value:02.0f}"
            label_down.fit_content()
            self.window.sound_value = round((self.ui_slider.value / 100), 1)

    def on_show_view(self):
        """Called when switching to this view."""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        """Draw the menu"""
        self.clear()
        self.manager.draw()

    def on_click_start(self, event):
        print("Start:", event)
        self.window.show_view(self.window.game_view)

    @staticmethod
    def on_click_exit(event):
        print("Exit:", event)
        arcade.exit()

    @staticmethod
    def on_click_settings(event):
        print("Settings:", event)


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

        # Load button textures
        cross = arcade.load_texture("./data/textures/UI/quit.png")
        cross_hover = arcade.load_texture("./data/textures/UI/quit_hover.png")

        # buttons settings
        self.settings_button = UITextureButton(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 35, texture=cross,
                                               texture_hovered=cross_hover)
        self.settings_button.on_click = self.quit_button_on
        self.manager.add(self.settings_button)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the slider
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

    def quit_button_on(self, event):
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
