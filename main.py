"""Platformer Game"""
import arcade
from settings import *


class MyGame(arcade.Window):
    """ Main application class."""

    def __init__(self, screen_width, screen_height, screen_title, fullscreen):
        # Вызываем родительский класс и передаем параметры окна
        super().__init__(screen_width, screen_height, screen_title, fullscreen)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Настройте игру здесь. Вызовите эту функцию, чтобы перезапустить игру."""
        pass

    def on_draw(self):
        """Рендеринг экрана."""

        self.clear()
        # Code to draw the screen goes here


def main():
    """Main функция"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULL_SCREEN)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
