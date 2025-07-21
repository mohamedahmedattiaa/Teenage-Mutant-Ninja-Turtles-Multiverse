# constants.py
from enum import Enum

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# UI State Enum
class UIState(Enum):
    CHARACTER_SELECT = -1
    MAIN = 0
    PAUSED = 1
    INVENTORY = 2
    GAME_OVER = 3
    BOSS_WARNING = 4

# Game State Enum
class GameState(Enum):
    CHARACTER_SELECTION = 0
    LEVEL_ONE = 1
    LEVEL_TWO = 2
    LEVEL_THREE = 3
    GAME_OVER = 4

# UI Color scheme
UI_COLORS = {
    'background': (20, 20, 30, 200),
    'primary': (100, 150, 255),
    'secondary': (70, 130, 200),
    'danger': (255, 80, 80),
    'warning': (255, 200, 50),
    'success': (80, 220, 120),
    'text': (240, 240, 250),
    'text_dark': (30, 30, 40),
    'health': (220, 60, 60),
    'oxygen': (50, 180, 220),
    'stamina': (150, 220, 80)
}