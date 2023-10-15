import pygame
import math
import random
import time
from pygame.locals import *
from blob import Blob, BlobMenu
from food import Food
import pymunk
from pymunk.pygame_util import DrawOptions

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BORDER_WIDTH = 10
WINDOW_SURFACE = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
GREY_COLOR = (122, 122, 122)

DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
pygame.display.set_caption("blob Steering")

space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.01
draw_options = DrawOptions(window)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

def generate_random_food():
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    size = random.randint(1, 5)
    return Food(x, y, space, size)

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW_SURFACE)
pygame.display.set_caption("blob Steering")

black_blob = Blob(600, 400, space)
blob_sprites = []
blob_sprites.append(black_blob)

food = Food(350, 450, space, 5)
food_sprites = []
food_sprites.append(food)

font = pygame.font.Font(None, 36)

def display_energy(window, energy):
    energy_text = font.render(f"Energy: {energy}", True, (255, 255, 255))
    window.blit(energy_text, (10, 10))

def draw_borders(surface):
    pygame.draw.rect(surface, GREY_COLOR, (0, 0, WINDOW_WIDTH, BORDER_WIDTH))
    pygame.draw.rect(surface, GREY_COLOR, (0, 0, BORDER_WIDTH, WINDOW_HEIGHT))
    pygame.draw.rect(surface, GREY_COLOR, (0, WINDOW_HEIGHT - BORDER_WIDTH, WINDOW_WIDTH, BORDER_WIDTH))
    pygame.draw.rect(surface, GREY_COLOR, (WINDOW_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, WINDOW_HEIGHT))

MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))

def draw_minimap():
    minimap_surface.fill(GREY_COLOR)
    
    for blob in blob_sprites:
        pygame.draw.circle(minimap_surface, (255, 0, 0),
                           (int(blob.body.position.x * MINIMAP_WIDTH / WINDOW_WIDTH),
                            int(blob.body.position.y * MINIMAP_HEIGHT / WINDOW_HEIGHT)), 2)

    for food in food_sprites:
        pygame.draw.circle(minimap_surface, (0, 255, 0),
                           (int(food.body.position.x * MINIMAP_WIDTH / WINDOW_WIDTH),
                            int(food.body.position.y * MINIMAP_HEIGHT / WINDOW_HEIGHT)), 2)
    
    pygame.draw.rect(minimap_surface, (255, 255, 255), (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)

clock = pygame.time.Clock()
done = False
food_spawn_time = time.time()
blob_menus = []
while not done:

    current_time = time.time()
    if current_time - food_spawn_time >= 10:
        food_sprite = generate_random_food()
        food_sprites.append(food_sprite)
        food_spawn_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH = event.w
            WINDOW_HEIGHT = event.h
            DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
            DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH
            window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT),
                                             pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        black_blob.turn(-0.05)
    if keys[pygame.K_RIGHT]:
        black_blob.turn(0.05)
    if keys[pygame.K_UP]:
        black_blob.accelerate(0.5)
    if keys[pygame.K_DOWN]:
        black_blob.accelerate(-0.5)

    for blob in blob_sprites:
        blob.update()

    for blob in blob_sprites:
        for food in food_sprites:
            if blob.blob_is_eating(food):
                food_sprites.remove(food)
                space.remove(food.shape, food.body)

    for blob in blob_sprites:
        if blob.energy <= 0:
            blob_sprites.remove(blob)
            space.remove(blob.body, blob.shape)

    background_surface.fill(GREY_COLOR)
    for blob in blob_sprites:
        display_energy(background_surface, blob.energy)

    window.blit(background_surface, (BORDER_WIDTH, BORDER_WIDTH))
    space.debug_draw(draw_options)
    for blob in blob_sprites:
        blob.draw(window)
        
    for food in food_sprites:
        food.draw(window)
        
    draw_borders(window)

    draw_minimap()
    minimap_x = WINDOW_WIDTH - MINIMAP_WIDTH - 10
    window.blit(minimap_surface, (minimap_x, 10))

    for blob in blob_sprites:
        blob.update()
        if blob.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            for menu in blob_menus:
                if menu.blob == blob:
                    menu.close_menu = not menu.closed
            if not any(menu.blob == blob for menu in blob_menus):
                blob_menus.append(BlobMenu(blob))

    for menu in blob_menus:
        menu.handle_events()
        if menu.close_menu:
            menu.closed = True
            blob_menus.remove(menu)

    for menu in blob_menus:
        menu.render(window)

    # Step the Pymunk space
    space.step(1 / 60.0)  # 60 FPS
    pygame.display.flip()
    clock.tick_busy_loop(60)

pygame.quit()
