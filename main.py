import pygame
from noise import pnoise2
import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 10

WATER_COLOR = (0, 0, 255)
GRASS_COLOR = (0, 255, 0)
FOREST_COLOR = (34, 139, 34)
MOUNTAIN_COLOR = (128, 128, 128)
SNOW_COLOR = (255, 255, 255)
Max_Width = 10000
Min_Width = 10000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics")
clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 36)
input_box = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 20, 140, 40)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
txt_surface = FONT.render(text, True, color)

def draw_input_box():
    pygame.draw.rect(screen, color, input_box, 2)
    screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
    draw_text("Enter world's generation boundary size (or 'infinite'):", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, FONT, pygame.Color('white'))

def draw_text(text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def get_world_boundaries():
    global active, text, color, txt_surface
    while True:
        screen.fill((0, 0, 0))
        draw_input_box()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text.lower() == 'infinite':
                            return Max_Width, Min_Width
                        try:
                            boundary_size = int(text)
                            if boundary_size > 0:
                                return boundary_size, boundary_size
                        except ValueError:
                            pass
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                    txt_surface = FONT.render(text, True, color)

gen_width, gen_height = get_world_boundaries()

def biome_color(value):
    if value < -0.05:
        return WATER_COLOR
    elif value < 0.2:
        return GRASS_COLOR
    elif value < 0.4:
        return FOREST_COLOR
    elif value < 0.6:
        return MOUNTAIN_COLOR
    else:
        return SNOW_COLOR

def draw_world(offset_x, offset_y, zoom):
    world_pixels = np.empty((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)

    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            world_x = (x + offset_x) * zoom / 100.0
            world_y = (y + offset_y) * zoom / 100.0
            if 0 <= world_x < gen_width and 0 <= world_y < gen_height:
                noise_val = pnoise2(world_x, world_y, octaves=6, persistence=0.5, lacunarity=2.0)
                world_pixels[y][x] = biome_color(noise_val)

    world_surface = pygame.surfarray.make_surface(world_pixels)
    return world_surface

zoom = 1.0
offset_x, offset_y = 0, 0
move_speed = 10
world_surface = draw_world(offset_x, offset_y, zoom)

running = True
world_needs_redraw = True
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

    screen.blit(pygame.transform.scale(world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()