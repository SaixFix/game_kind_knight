# Параметры окна
SCREEN_WIDTH = 1920  # ширина
SCREEN_HEIGHT = 1080  # высота
SCREEN_TITLE = "Kind knight"  # название
FULL_SCREEN = False  # полный экран

# Размеры
TILE_SCALING = 2  # размер плитки
CHARACTER_SCALING = 2  # размер игрока
SPRITE_PIXEL_SIZE = 128  # размер спрайтов
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING  # Размер сетки

# Сколько пикселей оставить в качестве минимального поля между символами
# и краем экрана.
VIEWPORT_MARGIN_TOP = 60  # Верх
VIEWPORT_MARGIN_BOTTOM = 60  # Низ
VIEWPORT_RIGHT_MARGIN = 270  # Право
VIEWPORT_LEFT_MARGIN = 270  # Лево

# Физика
MOVEMENT_SPEED = 5  # Скорость передвижения
JUMP_SPEED = 15  # скорость прыжка
GRAVITY = 1.0  # сила гравитации/притяжения

# Player starting position
PLAYER_START_X = 64
PLAYER_START_Y = 225

# Константа отслеживающая куда смотрит персонаж игрока
RIGHT_FACING = 0  # На право
LEFT_FACING = 1  # На лево

# Название слоев из TileMap
LAYER_NAME_SKY = "sky"
LAYER_NAME_GROUND = "ground"
LAYER_NAME_BACKGROUND = "BackGround"
LAYER_NAME_BACKGROUND2 = "Background2"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_DIE_BLOCK = "DieBlocks"
LAYER_NAME_CHEST = "chest"
LAYER_NAME_MOVING_DIE_BLOCK = "die_block_moving"

# слой игрока для мейн функции
LAYER_NAME_PLAYER = "Player"
