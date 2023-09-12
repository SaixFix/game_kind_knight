from typing import Optional

import arcade

from settings import *


class MainMenu(arcade.View):
    """Class that manages the 'menu' view."""

    def __init__(self, game_view: 'GameView'):
        super().__init__()
        self.game_view: Optional['GameView'] = game_view

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings(в разработке)", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=200)
        self.v_box.add(exit_button.with_space_around(bottom=20))

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box))

        # assign self.on_click_start as callback
        start_button.on_click = self.on_click_start
        settings_button.on_click = self.on_click_settings
        exit_button.on_click = self.on_click_exit

    def on_show_view(self):
        """Called when switching to this view."""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        """Draw the menu"""
        self.clear()

        self.manager.draw()

    def on_click_start(self, event):
        print("Start:", event)
        self.window.show_view(self.game_view)

    @staticmethod
    def on_click_exit(event):
        print("Exit:", event)
        arcade.exit()

    @staticmethod
    def on_click_settings(event):
        print("Settings:", event)


class GameOverView(arcade.View):
    """Class to manage the game overview"""

    def __init__(self, game_view: 'GameView'):
        super().__init__()

        # Main Game view
        self.game_view: Optional['GameView'] = game_view

    def on_show_view(self):
        """Called when switching to this view"""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        """Draw the game overview"""
        self.clear()
        arcade.draw_text(
            "Game Over - Click to restart",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """Use a mouse press to advance to the 'game' view."""
        self.window.show_view(self.game_view)
