import pygame
import random
from noise import pnoise2

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 10

WATER_COLOR = (0, 0, 255)
GRASS_COLOR = (0, 255, 0)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (128, 128, 128)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics")
clock = pygame.time.Clock()

def biome_color(value):
    if value < 0.3:
        return WATER_COLOR
    elif value < 0.5:
        return GRASS_COLOR
    elif value < 0.7:
        return FOREST_COLOR
    else:
        return MOUNTAIN_COLOR

zoom = 1.0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                zoom += 0.1
            elif event.button == 5:
                zoom -= 0.1
            if zoom < 0.1:
                zoom = 0.1

    screen.fill((0, 0, 0))

    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            noise_val = pnoise2(x/100.0*zoom, y/100.0*zoom, octaves=2)
            color = biome_color(noise_val)
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
