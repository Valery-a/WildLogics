import pygame
from noise import pnoise2

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 10

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
    if value < 0.4:
        return WATER_COLOR
    elif value < 0.5:
        return GRASS_COLOR
    elif value < 0.7:
        return FOREST_COLOR
    elif value < 0.85:
        return MOUNTAIN_COLOR
    else:
        return SNOW_COLOR

def draw_world(offset_x, offset_y, zoom):
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            noise_val = pnoise2((x + offset_x) * zoom / 50.0, (y + offset_y) * zoom / 50.0, octaves=3)
            color = biome_color(noise_val)
            pygame.draw.rect(world_surface, color, (x, y, TILE_SIZE, TILE_SIZE))

    return world_surface

zoom = 1.0
offset_x, offset_y = 0, 0
move_speed = 10

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 4:  # Mouse wheel up
                zoom += 0.1
                offset_x -= (mx - SCREEN_WIDTH // 2) * 0.1
                offset_y -= (my - SCREEN_HEIGHT // 2) * 0.1
            elif event.button == 5:  # Mouse wheel down
                zoom -= 0.1
                offset_x += (mx - SCREEN_WIDTH // 2) * 0.1
                offset_y += (my - SCREEN_HEIGHT // 2) * 0.1
            if zoom < 0.1:
                zoom = 0.1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        offset_y -= move_speed
    if keys[pygame.K_DOWN]:
        offset_y += move_speed
    if keys[pygame.K_LEFT]:
        offset_x -= move_speed
    if keys[pygame.K_RIGHT]:
        offset_x += move_speed

    screen.blit(draw_world(offset_x, offset_y, zoom), (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
