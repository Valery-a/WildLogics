import pygame
import math
from blob import Blob

# Window size
WINDOW_WIDTH    = 1200
WINDOW_HEIGHT   = 750
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
GREY_COLOR = (122, 122, 122) # used for background

class Food(pygame.sprite.Sprite):
    def __init__( self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        
        self.size = size
        self.image = self.generate_food()
        self.rect = self.image.get_rect()
        self.rect.center = ( x, y )
        self.position = pygame.math.Vector2( x, y )
        self.health = 20
        
    def generate_food(self):
        if self.size == 5:
            food_image  = pygame.transform.scale_by(pygame.image.load( 'food_size_5_32.png' ), 2).convert_alpha()
        
        # TODO: add other food size 1 trough 4
            
        return food_image  
        
    def update(self):
        self.rect.center = (self.position[0], self.position[1])
    

def check_for_collision_between_blob_and_food(blob_sprite, food_sprite):
    col = pygame.sprite.collide_rect(blob_sprite, food_sprite)
    if col == True:
        blob_sprite.energy += blob_sprite.attack_power / 2
        food_sprite.health -= blob_sprite.attack_power
        if food_sprite.health <= 0:
            return True
    
    return False

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

### Main Loop
clock = pygame.time.Clock()
done = False
while not done:

    # Handle user-input
    for event in pygame.event.get():
        if ( event.type == pygame.QUIT ):
            done = True
        elif ( event.type == pygame.VIDEORESIZE ):
            WINDOW_WIDTH  = event.w
            WINDOW_HEIGHT = event.h
            window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
        elif ( event.type == pygame.MOUSEBUTTONUP ):
            # On mouse-click
            pass

    # Continuous Movement keys
    keys = pygame.key.get_pressed()
    if ( keys[pygame.K_LEFT] ):
        black_blob.turn( -1.8 )  # degrees
    if ( keys[pygame.K_RIGHT] ):
        black_blob.turn( 1.8 )
    if ( keys[pygame.K_UP] ):  
        black_blob.accelerate( 0.5 )
    if ( keys[pygame.K_DOWN] ):  
        black_blob.brake( )

    # Update the blob(s)
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
    window.fill(GREY_COLOR) # backgorund
    blob_sprites.draw( window )
    food_sprites.draw( window )
    pygame.display.flip()

    # Clamp FPS
    clock.tick_busy_loop(60)

pygame.quit()