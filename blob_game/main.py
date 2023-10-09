import pygame
import math
import random
import time

from pygame.locals import *
from blob import Blob
from food import Food

# Window size
WINDOW_WIDTH    = 1200
WINDOW_HEIGHT   = 750
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
GREY_COLOR = (122, 122, 122) # used for background


# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
BORDER_WIDTH = 10
GREY_COLOR = (122, 122, 122)  # used for background

# Calculate the actual display size including borders
DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH

# Initialize pygame
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
pygame.display.set_caption("blob Steering")

# Create a background surface
background_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
def check_for_collision_between_blob_and_food(blob_sprite, food_sprite):
    offset_x = food_sprite.rect.x - blob_sprite.rect.x
    offset_y = food_sprite.rect.y - blob_sprite.rect.y
    
    col_point = blob_sprite.mask.overlap(food_sprite.mask, (offset_x, offset_y))
    
    if col_point:
        # Calculate direction vector from blob to food
        direction = food_sprite.position - blob_sprite.position
        direction.normalize_ip()

        # Move the blob out of the collision
        while blob_sprite.mask.overlap(food_sprite.mask, (int(food_sprite.rect.x - blob_sprite.rect.x), int(food_sprite.rect.y - blob_sprite.rect.y))):
            blob_sprite.position -= direction
            blob_sprite.rect.center = blob_sprite.position

    
        blob_sprite.energy += blob_sprite.attack_power / 2
        food_sprite.health -= blob_sprite.attack_power
        if food_sprite.health <= 0:
            return True
    return False

def generate_random_food():
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    size = random.randint(1, 5)
    return Food(x, y, size)


### initialisation
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
pygame.display.set_caption("blob Steering")


### Sprites
black_blob = Blob( 200, 400, heading=5 )
blob_sprites = pygame.sprite.Group() #Single()
blob_sprites.add( black_blob )

food = Food(350, 450, 5)
food_sprites = pygame.sprite.Group()
food_sprites.add(food)

font = pygame.font.Font(None, 36)
def display_energy(window, energy):
    energy_text = font.render(f"Energy: {energy}", True, (255, 255, 255))  # White text
    window.blit(energy_text, (10, 10))  # Position the text at (10, 10)

def draw_borders(surface):
    pygame.draw.rect(surface, GREY_COLOR, (0, 0, WINDOW_WIDTH, BORDER_WIDTH))
    pygame.draw.rect(surface, GREY_COLOR, (0, 0, BORDER_WIDTH, WINDOW_HEIGHT))
    pygame.draw.rect(surface, GREY_COLOR, (0, WINDOW_HEIGHT - BORDER_WIDTH, WINDOW_WIDTH, BORDER_WIDTH))
    pygame.draw.rect(surface, GREY_COLOR, (WINDOW_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, WINDOW_HEIGHT))


# Main loop
clock = pygame.time.Clock()
done = False
food_spawn_time = time.time()
while not done:

    current_time = time.time()
    if current_time - food_spawn_time >= 10:
        food_sprite = generate_random_food()
        food_sprites.add(food_sprite)
        food_spawn_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.VIDEORESIZE:
            # Update the window size and re-calculate the display size
            WINDOW_WIDTH = event.w
            WINDOW_HEIGHT = event.h
            DISPLAY_WIDTH = WINDOW_WIDTH + 2 * BORDER_WIDTH
            DISPLAY_HEIGHT = WINDOW_HEIGHT + 2 * BORDER_WIDTH
            window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        black_blob.turn(-1.8)
    if keys[pygame.K_RIGHT]:
        black_blob.turn(1.8)
    if keys[pygame.K_UP]:
        black_blob.accelerate(0.5)
    if keys[pygame.K_DOWN]:
        black_blob.brake()

    blob_sprites.update()
    food_sprites.update()

    for blob in blob_sprites:
        for food in food_sprites:
            if check_for_collision_between_blob_and_food(blob, food):
                food_sprites.remove(food)
                print(blob.energy)

    for blob in blob_sprites:
        if blob.energy <= 0:
            blob_sprites.remove(blob)

    # Update the window
    background_surface.fill(GREY_COLOR)
    for blob in blob_sprites:
        display_energy(background_surface, blob.energy)

    window.blit(background_surface, (BORDER_WIDTH, BORDER_WIDTH))  # Draw background with borders
    blob_sprites.draw(window)
    food_sprites.draw(window)
    draw_borders(window)  # Draw borders on the main window

    pygame.display.flip()
    clock.tick_busy_loop(60)

pygame.quit()