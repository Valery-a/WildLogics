from pandas import wide_to_long
import pygame
from noise import pnoise2
import random
from enum import Enum
from diamondGeneration import get_terrain_color_array

n = 1 + 2**9
ds = 0.6
terrain_color, screen_width, screen_height = get_terrain_color_array(n, ds)

TILE_SIZE = 2
SCREEN_WIDTH = screen_width * TILE_SIZE
SCREEN_HEIGHT = screen_height * TILE_SIZE

WATER_COLOR = (0, 0, 255)
GRASS_COLOR = (0, 255, 0)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (128, 128, 128)
SNOW_COLOR = (255, 255, 255)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics")
clock = pygame.time.Clock()


def biome_color(value):
    if value < 0.17:
        return WATER_COLOR
    elif value < 0.4:
        return GRASS_COLOR
    elif value < 0.6:
        return FOREST_COLOR
    elif value < 0.8:
        return MOUNTAIN_COLOR
    else:
        return SNOW_COLOR

def draw_world(offset_x, offset_y, zoom):
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    index = 0
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            color = terrain_color[index]
            pygame.draw.rect(world_surface, color, (x, y, TILE_SIZE, TILE_SIZE))
            index+=1
            
    return world_surface


zoom = 1.0
offset_x, offset_y = 0, 0
move_speed = 10
world_surface = draw_world(offset_x, offset_y, zoom)

running = True
world_needs_redraw = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        offset_y -= move_speed
        world_needs_redraw = True
    if keys[pygame.K_DOWN]:
        offset_y += move_speed
        world_needs_redraw = True
    if keys[pygame.K_LEFT]:
        offset_x -= move_speed
        world_needs_redraw = True
    if keys[pygame.K_RIGHT]:
        offset_x += move_speed
        world_needs_redraw = True

    if world_needs_redraw:
        world_surface = draw_world(offset_x, offset_y, zoom)
        world_needs_redraw = False

    screen.blit(
        pygame.transform.scale(world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
    )
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
