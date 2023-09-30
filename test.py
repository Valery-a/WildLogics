from pandas import wide_to_long
import pygame
from noise import pnoise2
import random
from enum import Enum

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
TILE_SIZE = 5


WATER_COLOR = (0, 0, 255)
GRASS_COLOR = (0, 255, 0)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (128, 128, 128)
SNOW_COLOR = (255, 255, 255)

current_zoom_width = 800
current_zoom_height = 600

can_go_up = False
can_go_left = False
can_go_right = False
can_go_down = False

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

def get_surrounding_pixels(world_surface, x, y, radius=1):
    surrounding_pixels = []
    
    # Iterate through the surrounding area
    for i in range(x - TILE_SIZE * radius, x + TILE_SIZE *(radius + 1)):
        for j in range(y - TILE_SIZE * radius, y + TILE_SIZE *(radius + 1)):
            # Check if the pixel coordinates are within the world_surface boundaries
            if i == x and j == y:
                continue
            if 0 <= i < world_surface.get_width() and 0 <= j < world_surface.get_height():
                color = world_surface.get_at((i, j))  # Get the color at (i, j)
                surrounding_pixels.append(tuple(color))

    return surrounding_pixels

def most_frequent(List):
    return max(set(List), key = List.count)

def draw_world(offset_x, offset_y, zoom):
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            noise_val = random.uniform(0, 1)
            color = biome_color(noise_val)
            pygame.draw.rect(world_surface, color, (x, y, TILE_SIZE, TILE_SIZE))

    for i in range(5):
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            for x in range(0, SCREEN_WIDTH, TILE_SIZE):
                colors = get_surrounding_pixels(world_surface, x, y)
                most_frequent_color = most_frequent(colors)
                pygame.draw.rect(world_surface, most_frequent_color, (x, y, TILE_SIZE, TILE_SIZE))
            

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 4:
                zoom += 0.1
                offset_x -= (mx - SCREEN_WIDTH // 2) * 0.1
                offset_y -= (my - SCREEN_HEIGHT // 2) * 0.1
                world_needs_redraw = True
            elif event.button == 5:
                zoom -= 0.1
                offset_x += (mx - SCREEN_WIDTH // 2) * 0.1
                offset_y += (my - SCREEN_HEIGHT // 2) * 0.1
                world_needs_redraw = True
            if zoom < 0.1:
                zoom = 0.1

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
