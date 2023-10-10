from turtle import position
from networkx import center
import pygame
import math
import sys

class Blob( ):
    """ blob Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, x, y, rotations=360, heading = 0 ):
        """ A blob Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base blob-image should be pointing North/Up.          """
        # Pre-make all the rotated versions
        # This assumes the start-image is pointing up-screen
        # Operation must be done in degrees (not radians)
        self.images = {}
        self.generate_blob()
        self.rot_img = {}
        self.min_angle = ( 360 / rotations )
        for name, image in self.images.items():
            current_image_array = []
            for i in range( rotations ):
                # This rotation has to match the angle in radians later
                # So offet the angle (0 degrees = "north") by 90° to be angled 0-radians (so 0 rad is "east")
                rotated_image = pygame.transform.rotozoom( image, 360-90-( i*self.min_angle ), 1 )
                current_image_array.append( rotated_image )
            
            self.rot_img[name] = current_image_array
            
        self.min_angle = math.radians( self.min_angle )   # don't need degrees anymore
        # define the image used
        self.heading = heading                           # pointing right (in radians)
        self.images['full_image'] = self.rot_img['full_image'][int( self.heading / self.min_angle ) % len( self.rot_img['full_image'] )]
        self.images['mouth_image'] = self.rot_img['mouth_image'][int( self.heading / self.min_angle ) % len( self.rot_img['mouth_image'] )]
        self.images['body_image'] = self.rot_img['body_image'][int( self.heading / self.min_angle ) % len( self.rot_img['body_image'] )]
        self.rect = self.images['full_image'].get_rect()
        self.body_mask = pygame.mask.from_surface(self.images['full_image'])
        self.rect.center = ( x, y )
        # movement
        self.reversing = False
        self.speed = 0
        self.max_speed = 4
        self.max_reverse_speed = -1.5    
        self.velocity = pygame.math.Vector2( 0, 0 )
        self.position = pygame.math.Vector2( x, y )
        #stats
        self.energy = 100
        self.attack_power = 1
        
    def generate_blob(self):
        body_image = pygame.transform.scale_by(pygame.image.load( './resources/blob_32.png' ), 2).convert_alpha()
        mouth_image = pygame.transform.scale_by(pygame.image.load( './resources/blob_mouth_32.png' ), 2).convert_alpha()
        self.images['body_image'] = body_image
        self.images['mouth_image'] = mouth_image
        
        full_image = body_image.copy()
        for name, image in self.images.items():
            full_image.blit(image, (0,0))
            
        self.images['full_image'] = full_image.convert_alpha()


    def turn( self, angle_degrees ):
        """ Adjust the angle the blob is heading, if this means using a 
            different blob-image, select that here too """
        self.heading += math.radians( angle_degrees ) 
        # Decide which is the correct image to display
        image_index = int( self.heading / self.min_angle ) % len( self.rot_img['full_image'] )
        # Only update the image if it's changed
        if ( self.images['full_image'] != self.rot_img['full_image'][ image_index ] ):
            for name, image in self.rot_img.items():
                self.images['full_image'] = self.rot_img['full_image'][ image_index ]
                self.images['mouth_image'] = self.rot_img['mouth_image'][ image_index ]
                self.images['body_image'] = self.rot_img['body_image'][ image_index ]
                
            self.rect = self.images['full_image'].get_rect()

    def accelerate(self, amount):
        """ Increase the speed either forward or reverse """
        if not self.reversing:
            self.speed += amount
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            if self.speed > 0:
                self.energy -= 0.1

    def brake(self):
        if self.speed > self.max_reverse_speed:
            self.speed -= 0.4
        if self.speed < 0:
            self.energy -= 0.1
        if self.speed < self.max_reverse_speed:
            self.speed = self.max_reverse_speed
            
    def blob_is_eating(self, food):
        offset_x = food.rect.x - self.rect.x
        offset_y = food.rect.y - self.rect.y
        mouth_mask = pygame.mask.from_surface(self.images['mouth_image'])
        col_point = mouth_mask.overlap(food.mask, (offset_x, offset_y))
        
        if col_point:
            self.energy += self.attack_power / 2
            food.health -= self.attack_power
            if food.health <= 0:
                return True
            
        return False

    def update( self ):
        """ Sprite update function, calcualtes any new position """
        lower_acceleration_speed = self.speed - 0.05
        lower_reverse_speed = self.speed + 0.05
        if self.speed > 0:
            self.speed = max(lower_acceleration_speed, 0)
        else:
            self.speed = min(lower_reverse_speed, 0)
        
        self.rect.center = ( round(self.position[0]), round(self.position[1] ) )
        
    def draw(self, win):
        self.velocity.from_polar( ( self.speed, math.degrees( self.heading ) ) )
        self.position += self.velocity
        position = (self.position[0] - self.images['full_image'].get_rect().width / 2, self.position[1] - self.images['full_image'].get_rect().height / 2)
        for name, image in self.images.items():
            win.blit(image, position)

class BlobMenu:
    def __init__(self, blob):
        self.blob = blob
        self.font = pygame.font.Font(None, 36)
        self.closed = False
        self.close_menu = False
        self.menu_width = 200
        self.menu_height = 100

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def render(self, surface):
        menu_x = self.blob.rect.centerx
        menu_y = self.blob.rect.centery - self.blob.rect.height // 2 - self.menu_height
        menu_rect = pygame.Rect(menu_x, menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(surface, (255, 255, 255), menu_rect, 0)
        pygame.draw.rect(surface, (0, 0, 0), menu_rect, 2)
        text = self.font.render(f"Energy: {self.blob.energy}", True, (0, 0, 0))
        text_rect = text.get_rect(center=menu_rect.center)
        surface.blit(text, text_rect)
