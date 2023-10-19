import pygame
import math
import random
import time
from pygame.locals import *
from blob import Blob
from food import Food
import pymunk
from pymunk.pygame_util import DrawOptions

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BORDER_WIDTH = 10
GREY_COLOR = (122, 122, 122)

DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("blob Steering")

space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.001
draw_options = DrawOptions(window)

background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("blob Steering")
font = pygame.font.Font(None, 36)

MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))

def generate_random_food():
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    size = random.uniform(1, 1.5)
    return Food(x, y, space, size)

def draw_minimap(blob_objects, food_objects):
    minimap_surface.fill(GREY_COLOR)
    
    for blob in blob_objects:
        pygame.draw.circle(minimap_surface, (255, 0, 0),
                           (int(blob.body.position.x * MINIMAP_WIDTH / WINDOW_WIDTH),
                            int(blob.body.position.y * MINIMAP_HEIGHT / WINDOW_HEIGHT)), 2)

    for food in food_objects:
        pygame.draw.circle(minimap_surface, (0, 255, 0),
                           (int(food.body.position.x * MINIMAP_WIDTH / WINDOW_WIDTH),
                            int(food.body.position.y * MINIMAP_HEIGHT / WINDOW_HEIGHT)), 2)
    
    pygame.draw.rect(minimap_surface, (255, 255, 255), (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
    
def draw_game(blob_objects, food_objects):
    background_surface.fill(GREY_COLOR)
    window.blit(background_surface, (0, 0))
    space.debug_draw(draw_options)
    for blob in blob_objects:
        blob.draw(window)
        
    for food in food_objects:
        food.draw(window)

    draw_minimap(blob_objects, food_objects)
    minimap_x = WINDOW_WIDTH - MINIMAP_WIDTH - 10
    window.blit(minimap_surface, (minimap_x, 10))
    
def main(config, genomes):
    amount_of_food_to_spawn = 100
    food_objects = []
    for i in range(amount_of_food_to_spawn):
        random_coords = [random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)]
        random_size = (random.uniform(1, 2))
        food_objects.append(Food(random_coords[0], random_coords[1], space, random_size))
    
    blob_objects = []
    player_blob = Blob(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), space)
    blob_objects.append(player_blob)    
        
    clock = pygame.time.Clock()
    done = False
    food_spawn_time = time.time()
    while not done:
        current_time = time.time()
        if current_time - food_spawn_time >= 10:
            food_sprite = generate_random_food()
            food_objects.append(food_sprite)
            food_spawn_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_blob.turn(-0.05)
        if keys[pygame.K_RIGHT]:
            player_blob.turn(0.05)
        if keys[pygame.K_UP]:
            player_blob.accelerate(0.5)
        if keys[pygame.K_DOWN]:
            player_blob.accelerate(-0.5)

        for blob in blob_objects:
            blob.update()
            
        for food in food_objects:
            food.update()

        print(player_blob.energy)
        for blob in blob_objects:
            blob.nearest_object(food_objects)
            for food in food_objects:
                if blob.blob_is_eating(food):
                    food_objects.remove(food)
                    space.remove(food.shape, food.body)

        for i, blob in enumerate(blob_objects):
            if blob.energy <= 0:
                blob_objects.pop(i)
                space.remove(blob.body, blob.shape, blob.mouth_shape, blob.field_of_view_shape)

        draw_game(blob_objects, food_objects)

        # Step the Pymunk space
        space.step(1 / 60.0)  # 60 FPS
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
main(0,0)