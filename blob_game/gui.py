import pygame
import pymunk
from pymunk.pygame_util import DrawOptions
from configValues import *

def toggle_gui_panel():
    global gui_panel_visible
    gui_panel_visible = not gui_panel_visible
    
def draw_gui_panel(selected_object, win):
    if gui_panel_visible:
        gui_panel_surface.fill(GUI_PANEL_COLOR)

        panel_padding = 10
        text_color = (255, 255, 255)
        header_color = (30, 144, 255)
        font = pygame.font.Font(None, 24)

        if selected_object is not None:
            text_y = panel_padding
            text_spacing = 30

            header_text = font.render("Object Details", True, header_color)
            gui_panel_surface.blit(header_text, (panel_padding, text_y))
            text_y += text_spacing

            object_type_text = font.render("Type: " + selected_object.type, True, text_color)
            gui_panel_surface.blit(object_type_text, (panel_padding, text_y))
            text_y += text_spacing

            if selected_object.type == "blob":
                energy_text = font.render("Energy: " + str(selected_object.energy), True, text_color)
                gui_panel_surface.blit(energy_text, (panel_padding, text_y))
                # Draw a progress bar for energy
                pygame.draw.rect(gui_panel_surface, (0, 255, 0), (panel_padding, text_y + text_spacing, selected_object.energy, 10))
                text_y += text_spacing * 2
            elif selected_object.type == "food":
                health_text = font.render("Health: " + str(selected_object.health), True, text_color)
                gui_panel_surface.blit(health_text, (panel_padding, text_y))
                # Draw a progress bar for health
                pygame.draw.rect(gui_panel_surface, (255, 0, 0), (panel_padding, text_y + text_spacing, selected_object.health, 10))
                text_y += text_spacing * 2
            
            camera_width = 100
            camera_height = 75
            camera_x = panel_padding
            camera_y = text_y + text_spacing
            camera_rect = pygame.Rect(camera_x, camera_y, camera_width, camera_height)

            if selected_object:
                camera_center_x = int(selected_object.body.position.x * ZOOM_FACTOR)
                camera_center_y = int(selected_object.body.position.y * ZOOM_FACTOR)
            else:
                camera_center_x = camera_x + camera_width // 2
                camera_center_y = camera_y + camera_height // 2

            camera_view = pygame.Surface((camera_width, camera_height))
            camera_view_rect = pygame.Rect(0, 0, camera_width, camera_height)

            camera_view.blit(win, camera_view_rect, camera_view_rect.move(camera_center_x - camera_width // 2, camera_center_y - camera_height // 2))

            pygame.draw.rect(gui_panel_surface, (255, 255, 255), camera_rect, 2)
            gui_panel_surface.blit(camera_view, (camera_x + 2, camera_y + 2))

        win.blit(gui_panel_surface, (0, 0))

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