"""Platformer Game"""
import arcade
from settings import *
import os
import time


class MyGame(arcade.Window):
    """ Main application class."""

    def __init__(self, screen_width, screen_height, screen_title, fullscreen):
        # Вызываем родительский класс и передаем параметры окна
        super().__init__(screen_width, screen_height, screen_title, fullscreen)

        # Данное указание каталога требуется для запуска
        # запуска с помощью команды "python -m"
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Tilemap Object
        self.tile_map = None

        # Sprite lists
        self.player_list = None

        # Настройки персонажа
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        self.level = 1
        self.max_level = 2

    def setup(self):
        """Настройте игру здесь. Вызовите эту функцию, чтобы перезапустить игру."""
        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Настройки для игрока/персонажа
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            PLAYER_SCALING,
        )

        # Стартовая позиция игрока/персонажа
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)

        self.load_level(self.level)

        self.game_over = False

    def load_level(self, level):
        """Функция загрузки уровня"""
        # layer_options = {"Platforms": {"use_spatial_hash": True}}

        # Считывает tiled map
        self.tile_map = arcade.load_tilemap(
            f":resources:tiled_maps/level_{level}.json", scaling=TILE_SPRITE_SCALING
        )

        # --- Стены ---

        # Вычислияем правый край my_map в пикселях
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.tile_map.sprite_lists["Platforms"],
            gravity_constant=GRAVITY,
        )

        # --- Other stuff
        # Установка цвета фона
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Установите границы окна просмотра
        # Эти цифры указывают, куда мы «прокрутили».
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """Рендеринг экрана."""

        self.frame_count += 1

        # Эта команда должна выполнится до того, как мы начнем рисовать.
        self.clear()

        # Рисуем все спрайты.
        self.player_list.draw()
        self.tile_map.sprite_lists["Platforms"].draw()

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        if self.fps_message:
            arcade.draw_text(
                self.fps_message,
                self.view_left + 10,
                self.view_bottom + 40,
                arcade.color.BLACK,
                14,
            )

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Размещаем текст на экран.
        # Отрегулируйте положение текста в зависимости от области просмотра,
        # чтобы не прокручивать текст.
        distance = self.player_sprite.right
        output = f"Distance: {distance:.0f}"
        arcade.draw_text(
            output, self.view_left + 10, self.view_bottom + 20, arcade.color.BLACK, 14
        )

        if self.game_over:
            arcade.draw_text(
                "Game Over",
                self.view_left + 200,
                self.view_bottom + 200,
                arcade.color.BLACK,
                30,
            )

    def on_key_press(self, key, modifiers):
        """
        Вызывается при каждом движении мыши.
        """
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Вызывается, когда пользователь нажимает кнопку мыши.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Передвижение и игровая логика"""

        if self.player_sprite.right >= self.end_of_map:
            if self.level < self.max_level:
                self.level += 1
                self.load_level(self.level)
                self.player_sprite.center_x = 128
                self.player_sprite.center_y = 64
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            else:
                self.game_over = True

        # Вызоваем обновление для всех спрайтов (The sprites don't do much in this example though.)
        #
        if not self.game_over:
            self.physics_engine.update()

        # --- Управление прокруткой ---

        # Track if we need to change the view port

        changed = False

        # Прокрутка влево
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Прокрутка вправо
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Прокрутка вверх
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Прокрутка вниз
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        # Если нам нужно прокрутить, давайте сделаем это.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(
                self.view_left,
                SCREEN_WIDTH + self.view_left,
                self.view_bottom,
                SCREEN_HEIGHT + self.view_bottom,
            )


def main():
    """Main функция"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULL_SCREEN)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
