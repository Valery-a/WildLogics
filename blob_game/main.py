import pygame
import math
import random
import time
import pymunk
from pymunk.pygame_util import DrawOptions
from food import Food
from blob import Blob

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BORDER_WIDTH = 10
GREY_COLOR = (122, 122, 122)

DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH

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

MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))

GUI_PANEL_WIDTH = 200
GUI_PANEL_COLOR = (50, 50, 50)
gui_panel_surface = pygame.Surface((GUI_PANEL_WIDTH, DISPLAY_HEIGHT))

zoom_factor = 1  # Adjust this value as needed for zooming in the camera view

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
        blob.draw(window, zoom_factor=zoom_factor)
        
    for food in food_objects:
        food.draw(window, zoom_factor=zoom_factor)

    draw_minimap(blob_objects, food_objects)
    minimap_x = WINDOW_WIDTH - MINIMAP_WIDTH - 10
    window.blit(minimap_surface, (minimap_x, 10))

def toggle_gui_panel():
    global gui_panel_visible
    gui_panel_visible = not gui_panel_visible
    
def draw_gui_panel(selected_object, win):
    if gui_panel_visible:
        gui_panel_surface.fill(GUI_PANEL_COLOR)

        # Define styles
        panel_padding = 10
        text_color = (255, 255, 255)
        header_color = (30, 144, 255)
        font = pygame.font.Font(None, 24)

        if selected_object is not None:
            text_y = panel_padding
            text_spacing = 30

            # Header
            header_text = font.render("Object Details", True, header_color)
            gui_panel_surface.blit(header_text, (panel_padding, text_y))
            text_y += text_spacing

            # Object type
            object_type_text = font.render("Type: " + selected_object.type, True, text_color)
            gui_panel_surface.blit(object_type_text, (panel_padding, text_y))
            text_y += text_spacing

            # Display specific attributes based on the object type
            if selected_object.type == "blob":
                energy_text = font.render("Energy: " + str(selected_object.energy), True, text_color)
                gui_panel_surface.blit(energy_text, (panel_padding, text_y))
                text_y += text_spacing
            elif selected_object.type == "food":
                health_text = font.render("Health: " + str(selected_object.health), True, text_color)
                gui_panel_surface.blit(health_text, (panel_padding, text_y))
                text_y += text_spacing
            
            # Create a camera view in the panel
            camera_width = 100
            camera_height = 75
            camera_x = panel_padding
            camera_y = text_y + text_spacing
            camera_rect = pygame.Rect(camera_x, camera_y, camera_width, camera_height)

            # Calculate the camera view position based on the selected object's position
            if selected_object:
                camera_center_x = int(selected_object.body.position.x * zoom_factor)
                camera_center_y = int(selected_object.body.position.y * zoom_factor)
            else:
                # If no object is selected, center the camera on a fixed point or a default position
                camera_center_x = camera_x + camera_width // 2
                camera_center_y = camera_y + camera_height // 2

            camera_view = pygame.Surface((camera_width, camera_height))
            camera_view_rect = pygame.Rect(0, 0, camera_width, camera_height)

            # Copy the region around the selected object to the camera view
            camera_view.blit(win, camera_view_rect, camera_view_rect.move(camera_center_x - camera_width // 2, camera_center_y - camera_height // 2))

            # Display the camera view in the GUI panel
            pygame.draw.rect(gui_panel_surface, (255, 255, 255), camera_rect, 2)
            gui_panel_surface.blit(camera_view, (camera_x + 2, camera_y + 2))

        win.blit(gui_panel_surface, (0, 0))

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

main(0, 0)
