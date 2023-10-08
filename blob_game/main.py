import pygame
import math
from blob import Blob

# Window size
WINDOW_WIDTH    = 1200
WINDOW_HEIGHT   = 750
WINDOW_SURFACE  = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

GREY_COLOR = (122, 122, 122)

### initialisation
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), WINDOW_SURFACE )
pygame.display.set_caption("blob Steering")


### Bitmaps
blob_image  = pygame.transform.scale_by(pygame.image.load( 'blob_32.png' ), 2).convert_alpha()


### Sprites
black_blob = Blob( blob_image, 300, 400, heading=5 )
blob_sprites = pygame.sprite.Group() #Single()
blob_sprites.add( black_blob )


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
        print( 'accelerate' )
        black_blob.accelerate( 0.5 )
    if ( keys[pygame.K_DOWN] ):  
        print( 'brake' )
        black_blob.brake( )

    # Update the blob(s)
    blob_sprites.update()

    # Update the window
    window.fill(GREY_COLOR) # backgorund
    blob_sprites.draw( window )
    pygame.display.flip()

    # Clamp FPS
    clock.tick_busy_loop(60)

pygame.quit()