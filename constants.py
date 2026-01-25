from enum import Enum
import os

# Настройка окна
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32
FPS = 60
UI_PANEL_HEIGHT = 150  # Высота панели UI

# Настройка карты
MAP_WIDTH = 60
MAP_HEIGHT = 40

# Пути к текстурам
TEXTURE_DIR = "textures"
TILE_TEXTURES = {
    "wall": f"{TEXTURE_DIR}/tiles/wall.png",
    "floor": f"{TEXTURE_DIR}/tiles/floor.png",
    "blood_vessel": f"{TEXTURE_DIR}/tiles/blood_vessel.png",
    "exit": f"{TEXTURE_DIR}/tiles/exit.png",
}

ENTITY_TEXTURES = {
    "player": f"{TEXTURE_DIR}/entities/virus.png",
    "virus_clone": f"{TEXTURE_DIR}/entities/virus_clone.png",
    "macrophage": f"{TEXTURE_DIR}/entities/macrophage.png",
    "neutrophil": f"{TEXTURE_DIR}/entities/neutrophil.png",
    "b_cell": f"{TEXTURE_DIR}/entities/b_cell.png",
    "t_cell": f"{TEXTURE_DIR}/entities/t_cell.png",
    "dendritic": f"{TEXTURE_DIR}/entities/dendritic.png",
    "mast_cell": f"{TEXTURE_DIR}/entities/mast_cell.png",
}

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (220, 200, 50)
PURPLE = (150, 50, 200)
ORANGE = (220, 150, 50)
CYAN = (50, 200, 200)
DARK_RED = (100, 20, 20)
DARK_GREEN = (20, 80, 20)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
PINK = (220, 100, 150)


class TileType(Enum):
    WALL = 0
    FLOOR = 1
    BLOOD_VESSEL = 2
    EXIT = 3


class EntityType(Enum):
    PLAYER = 0
    MACROPHAGE = 1
    NEUTROPHIL = 2
    B_CELL = 3
    T_CELL = 4
    DENDRITIC = 5
    MAST_CELL = 6
    VIRUS_CLONE = 7


class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    PLAYER_TURN = 2
    ENEMY_TURN = 3
    LEVEL_UP = 4
    GAME_OVER = 5
    VICTORY = 6
    PAUSED = 7
    GUIDE = 8


# Названия уровней
LEVEL_NAMES = {
    1: "Кровеносная система - Вход",
    2: "Кровеносная система - Артерии",
    3: "Кровеносная система - Вены",
    4: "Лимфатическая система - Узлы",
    5: "Лимфатическая система - Протоки",
    6: "Лимфатическая система - Центр",
    7: "Лёгкие - Бронхи",
    8: "Лёгкие - Альвеолы",
    9: "Лёгкие - Глубина",
    10: "Печень - Периферия",
    11: "Печень - Центр",
    12: "Печень - Ядро",
    13: "Мозг - Финальная битва",
}

MAX_LEVEL = 13