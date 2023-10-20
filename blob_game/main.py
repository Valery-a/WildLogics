import pygame
import math
import random
import time
import pymunk
from pymunk.pygame_util import DrawOptions
from food import Food
from blob import Blob
from configValues import *
from gui import toggle_gui_panel, draw_gui_panel, draw_game, draw_minimap

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Blob Steering")

space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.001
draw_options = DrawOptions(window)
gui_panel_visible = False
background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blob Steering")
font = pygame.font.Font(None, 36)

def generate_random_food():
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    size = random.uniform(1, 1.5)
    return Food(x, y, space, size)


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
    selected_object = None  # Add this variable
    
    while not done:
        current_time = time.time()
        if current_time - food_spawn_time >= 10:
            food_sprite = generate_random_food()
            food_objects.append(food_sprite)
            food_spawn_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                toggle_gui_panel()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                for blob in blob_objects:
                    if blob.is_clicked(event.pos):
                        selected_object = blob
                for food in food_objects:
                    if food.is_clicked(event.pos):
                        selected_object = food

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

        draw_gui_panel(selected_object, window)

        space.step(1 / 60.0)
        pygame.display.flip()
        minimap_x = WINDOW_WIDTH - MINIMAP_WIDTH - 10
        window.blit(minimap_surface, (minimap_x, 10))
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main(0, 0)