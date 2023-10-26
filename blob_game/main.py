import pygame
import random
import time
import pymunk
import os
import neat
import numpy as np
from pymunk.pygame_util import DrawOptions
from pymunk import pygame_util
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


def eval_genome(genomes, config):
    networks = []
    genes = []
    blob_objects = []
    
    for _, g in genomes:
        random_coords = [random.randint(-WINDOW_WIDTH, WINDOW_WIDTH * 2), random.randint(-WINDOW_HEIGHT, WINDOW_HEIGHT * 2)]
        net = neat.nn.FeedForwardNetwork.create(g, config)
        networks.append(net)
        blob_objects.append(Blob(random_coords[0], random_coords[1], space))
        g.fitness = 0
        genes.append(g)
    
    amount_of_food_to_spawn = 200
    food_objects = []
    for i in range(amount_of_food_to_spawn):
        random_coords = [random.randint(-WINDOW_WIDTH, WINDOW_WIDTH * 2), random.randint(-WINDOW_HEIGHT, WINDOW_HEIGHT * 2)]
        random_size = (random.uniform(4, 6))
        food_objects.append(Food(random_coords[0], random_coords[1], space, random_size))
        
    clock = pygame.time.Clock()
    done = False
    food_spawn_time = time.time()
    selected_object = None  # Add this variable
    
    scaling = 0.3
    translation = pymunk.Transform()
    zoomed_in_on_selected_object = False
    fps = 60
    
    while not done:
        current_time = time.time()
        zoom_in = 0
        zoom_out = 0
        vector_of_translation = [0,0]

        if len(blob_objects) == 0:
            done = True
            break
        
        if current_time - food_spawn_time >= 10:
            food_sprite = generate_random_food()
            food_objects.append(food_sprite)
            food_spawn_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                toggle_gui_panel()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if selected_object and selected_object.type == "blob" and selected_object.energy > 30:
                    new_blob = Blob(selected_object.body.position.x, selected_object.body.position.y, space, size=selected_object.size / 2)
                    new_blob.energy = selected_object.energy / 2
                    selected_object.energy = selected_object.energy / 2
                    blob_objects.append(new_blob)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                pos = pygame_util.get_mouse_pos(window)
                for blob in blob_objects:
                    if blob.is_clicked(pos):
                        selected_object = blob
                        zoomed_in_on_selected_object = True
                for food in food_objects:
                    if food.is_clicked(pos):
                        selected_object = food
                        zoomed_in_on_selected_object = True  
            
            if event.type == pygame.MOUSEWHEEL:
                x, y = pygame.mouse.get_pos()
                vector_of_translation = [x - WINDOW_WIDTH / 2, y - WINDOW_HEIGHT / 2]
                if event.y == -1:
                    zoom_out = 1
                    zoomed_in_on_selected_object = False
                elif event.y == 1:
                    zoom_in = 1
                    zoomed_in_on_selected_object = False
        
        keys = pygame.key.get_pressed()   
        left = int(keys[pygame.K_a])
        up = int(keys[pygame.K_w])
        down = int(keys[pygame.K_s])
        right = int(keys[pygame.K_d])
        
        # if selected_object != None:
        #     if zoomed_in_on_selected_object:
        #         vector_of_translation = [selected_object.rect.center[0] - WINDOW_WIDTH / 2, selected_object.rect.center[1] - WINDOW_HEIGHT / 2]
        #         scaling = 3
            
        translate_speed = 10
        zoom_speed = 0.1
        scaling *= 1 + (zoom_speed * zoom_in - zoom_speed * zoom_out)
        zoom_translate_speed = 0.1
        
        translation = translation.translated(
            translate_speed * left - (translate_speed * right + vector_of_translation[0] * zoom_translate_speed),
            translate_speed * up - (translate_speed * down + vector_of_translation[1] * zoom_translate_speed),
        )
        draw_options.transform = (
            pymunk.Transform.translation(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            @ pymunk.Transform.scaling(scaling)
            @ translation
            @ pymunk.Transform.translation(-WINDOW_WIDTH // 2, -WINDOW_HEIGHT // 2)
        )

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     player_blob.turn(-0.05)
        # if keys[pygame.K_RIGHT]:
        #     player_blob.turn(0.05)
        # if keys[pygame.K_UP]:
        #     player_blob.accelerate(0.5)
        # if keys[pygame.K_DOWN]:
        #     player_blob.accelerate(-0.5)

        for i, blob in enumerate(blob_objects):
            blob.update()
            genes[i].fitness -= 0.2
            
            output = networks[i].activate((
                blob.health * 0.1, 
                blob.energy * 0.1, 
                blob.speed * 0.1, 
                blob.body.rotation_vector.x * 0.1, 
                blob.current_nearest_object_distance * 0.1, 
                blob.current_nearest_object_angle * 0.1,
                0 if blob.current_nearest_object_type == 'blob' else 1))

            blob.accelerate(output[0])
            blob.turn(output[1] * 0.1)

        for food in food_objects:
            food.update()

        all_objects = food_objects + blob_objects
        for i, blob in enumerate(blob_objects):
            objects_to_check = [object for object in all_objects if (blob.body.position.x - (100)) <= object.body.position.x <= (blob.body.position.x + (100)) and \
               (blob.body.position.y - (100)) <= object.body.position.y <= (blob.body.position.y + (100))]
            blob.nearest_object(objects_to_check)
            for food in food_objects:
                if blob.blob_is_eating(food, genes[i]):
                    food_objects.remove(food)
                    space.remove(food.shape, food.body)
        
        for i, blob in enumerate(blob_objects):
            for j, other_blob in enumerate(blob_objects):
                if blob.blob_is_eating(other_blob, genes[i]):
                    blob_objects.pop(j)
                    space.remove(other_blob.body, other_blob.shape, other_blob.mouth_shape, other_blob.field_of_view_shape)
                    genes.pop(j)
                    networks.pop(j)

        for i, blob in enumerate(blob_objects):
            if blob.energy <= 0:
                blob_objects.pop(i)
                space.remove(blob.body, blob.shape, blob.mouth_shape, blob.field_of_view_shape)
                genes.pop(i)
                networks.pop(i)

        draw_game(blob_objects, food_objects, space, draw_options, scaling, translation)

        draw_gui_panel(selected_object, window)

        minimap_x = WINDOW_WIDTH - MINIMAP_WIDTH - 10
        window.blit(minimap_surface, (minimap_x, 10))
        pygame.display.flip()
        space.step(1 / fps)
        clock.tick(fps)
    
def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genome, None)

if __name__ == "__main__":
    localdir = os.path.dirname(__file__)
    config_path = os.path.join(localdir, 'resources', 'config-feedforward.txt')
    run(config_path)