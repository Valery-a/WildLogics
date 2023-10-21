import pygame
import pymunk
from pymunk.pygame_util import DrawOptions

MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
GUI_PANEL_WIDTH = 200
GUI_PANEL_COLOR = (50, 50, 50)
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BORDER_WIDTH = 10
GREY_COLOR = (122, 122, 122)
DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH
ZOOM_FACTOR = 1

window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
gui_panel_visible = False
background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

gui_panel_surface = pygame.Surface((GUI_PANEL_WIDTH, DISPLAY_HEIGHT))
minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
