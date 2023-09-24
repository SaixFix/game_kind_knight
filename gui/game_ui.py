import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UILabel, UIOnChangeEvent, UITextureButton

from settings import *


class GameUiAssets:
    def __init__(self, manager: arcade.gui.UIManager, window: arcade.Window):
        self.window = window
        self.manager = manager

        # Load button textures
        self.template_button = arcade.load_texture("./data/textures/UI/template_button_hover.png")
        self.settings = arcade.load_texture("./data/textures/UI/settings.png")
        self.settings_hover = arcade.load_texture("./data/textures/UI/settings_hover.png")
        self.settings_pressed = arcade.load_texture("./data/textures/UI/settings_pressed.png")

    def game_ui(self) -> arcade.gui.UIManager:
        """
        Create ui items, add in UIManager and return UIManager
        """

        settings_button = UITextureButton(
            self.window.width - 30,
            self.window.height - 35,
            texture=self.settings,
            texture_hovered=self.settings_hover,
            texture_pressed=self.settings_pressed
        )

        self.manager.add(settings_button)

        # button style
        style = {'bg_color': (139, 69, 19), "font_color": arcade.color.WHITE, "font_name": ("Comic Sans MS",)}

        @settings_button.event("on_click")
        def setting_button_on(event):
            self.window.show_view(self.window.settings_view)

        return self.manager

    def die_score_ui(self, die_score: int) -> arcade.gui.UILabel:
        die_score_ui = UILabel(
            text=f" Die Score: {die_score}   ",
            text_color=(255, 0, 0),
            font_size=18,
            x=250,
            y=self.window.height - 35,
            bold=True
        )

        self.manager.add(die_score_ui)

        die_score_textures = arcade.gui.UITexturePane(
            tex=self.template_button,
            child=die_score_ui
        )

        self.manager.add(die_score_textures)

        return die_score_ui

    def gold_scores_ui(self, gold_score: int) -> arcade.gui.UILabel:
        # Create gold scores ui
        gold_score_ui = UILabel(
            text=f" Gold Score: {gold_score}   ",
            text_color=arcade.csscolor.GOLD,
            font_size=18,
            x=5,
            y=self.window.height - 35,
            bold=True
        )

        self.manager.add(gold_score_ui)

        # background textures for score_text
        gold_score_textures = arcade.gui.UITexturePane(
            tex=self.template_button,
            child=gold_score_ui
        )

        self.manager.add(gold_score_textures)

        return gold_score_ui
