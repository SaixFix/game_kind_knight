import arcade.gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UILabel, UIOnChangeEvent


class MainMenuUiAssets:
    def __init__(self, manager: arcade.gui.UIManager, window: arcade.Window, media_player: arcade.load_sound):
        self.window = window
        self.manager = manager
        self.media_player = media_player

        # load textures
        self.template_button = arcade.load_texture("./data/textures/UI/template_button.png")
        self.template_hover = arcade.load_texture("./data/textures/UI/template_button_hover.png")
        self.template_pressed = arcade.load_texture("./data/textures/UI/template_button_pressed.png")

    def main_menu_gui(self):
        """
        create ui items, add in UIManager and return UIManager
        """
        # Create a vertical BoxGroup to align buttons
        v_box = arcade.gui.UIBoxLayout()

        # Create the buttons
        start_button = arcade.gui.UITextureButton(
            texture=self.template_button,
            texture_hovered=self.template_hover,
            texture_pressed=self.template_pressed,
            text="Start Game",
            width=200,
            height=50
        )
        v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UITextureButton(
            texture=self.template_button,
            texture_hovered=self.template_hover,
            texture_pressed=self.template_pressed,
            text="Settings",
            width=200,
            height=50
        )
        v_box.add(settings_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UITextureButton(
            texture=self.template_button,
            texture_hovered=self.template_hover,
            texture_pressed=self.template_pressed,
            text="Exit",
            width=200,
            height=50
        )
        v_box.add(exit_button.with_space_around(bottom=20))

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=v_box))

        # Create the audio slider
        style_slider = {'normal_bg': (255, 0, 0)}
        ui_slider = UISlider(
            x=0,
            y=50,
            value=50,
            width=200,
            height=30,
            style=style_slider
        )
        label_down = UILabel(text=f"{ui_slider.value:02.0f}")
        label_up = UILabel(text=f"Sound volume")

        self.manager.add(ui_slider)

        # background textures for audio slider
        slider_textures = arcade.gui.UITexturePane(
            tex=self.template_button,
            child=ui_slider
        )

        self.manager.add(slider_textures)

        # for sound slider
        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            label_down.text = f"{ui_slider.value:02.0f}"
            label_down.fit_content()
            self.media_player.volume = round((ui_slider.value / 100), 1)

        @start_button.event("on_click")
        def on_click_start(event):
            self.window.show_view(self.window.game_view)

        @exit_button.event("on_click")
        def on_click_exit(event):
            print("Exit:", event)
            arcade.exit()

        @settings_button.event("on_click")
        def on_click_settings(event):
            self.window.show_view(self.window.settings_view)

        return self.manager


