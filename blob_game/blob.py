from turtle import position
from networkx import center
import pygame
import math
import sys
import pymunk

class Blob( ):
    """ blob Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, x, y, space, mass=0.05, rotations=360, heading = 0 ):
        """ A blob Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base blob-image should be pointing North/Up.          """
        # Pre-make all the rotated versions
        # This assumes the start-image is pointing up-screen
        # Operation must be done in degrees (not radians)
        self.mass = mass
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
        
        # Setting up rigit body
        self.shape = pymunk.Poly.create_box(None, (self.rot_img['full_image'][0].get_rect().width, self.rot_img['full_image'][0].get_rect().height))
        self.moment = pymunk.moment_for_box(self.mass, (self.rot_img['full_image'][0].get_rect().width, self.rot_img['full_image'][0].get_rect().height))
        self.body = pymunk.Body(self.mass, self.moment)  
        self.shape.body = self.body
        self.shape.elasticity = 0.7  # Bounciness
        self.body.position = x, y
        space.add(self.body, self.shape)
        
        # define image used
        self.heading = self.body.angle                           # pointing right (in radians)
        self.images['full_image'] = self.rot_img['full_image'][int( self.heading / self.min_angle ) % len( self.rot_img['full_image'] )]
        self.images['mouth_image'] = self.rot_img['mouth_image'][int( self.heading / self.min_angle ) % len( self.rot_img['mouth_image'] )]
        self.images['body_image'] = self.rot_img['body_image'][int( self.heading / self.min_angle ) % len( self.rot_img['body_image'] )]
        self.rect = self.images['full_image'].get_rect()
        
        # masks and position
        self.body_mask = pygame.mask.from_surface(self.images['full_image'])
        self.rect.center = ( x, y )
        
        # movement
        self.reversing = False
        self.speed = 0
        self.max_speed = 20
        self.max_reverse_speed = -self.max_speed / 2    
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
        
        self.body.angle += angle_degrees
        self.heading = self.body.angle
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
        self.speed += amount
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < self.max_reverse_speed:
            self.speed = self.max_reverse_speed
        if self.speed > 0:
            self.energy -= 0.1
        self.body.apply_force_at_local_point((self.speed, 0), (0, 0))
            
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
            win.blit(image, (self.body.position.x - self.images['full_image'].get_rect().width / 2, self.body.position.y - self.images['full_image'].get_rect().height / 2))

class BlobMenu:
    def __init__(self, blob):
        self.closed = False
        self.close_menu = False
        self.blob = blob
        self.menu_width = 200
        self.menu_height = 100
        self.background_color = (50, 50, 50)  # Change to your preferred background color
        self.border_color = (0, 0, 0)  # Change to your preferred border color
        self.font = pygame.font.Font("./resources/font.ttf", 14)  # Change to your preferred font and size

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def render(self, surface):
        menu_x = self.blob.rect.centerx
        menu_y = self.blob.rect.centery - self.blob.rect.height // 2 - self.menu_height
        menu_rect = pygame.Rect(menu_x, menu_y, self.menu_width, self.menu_height)

        # Draw the background
        pygame.draw.rect(surface, self.background_color, menu_rect)

        # Draw the border
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)

        # Format the energy to have 4 decimal places
        energy_text = "{:.4f}".format(self.blob.energy)

        # Render text with a margin
        text = self.font.render(f"Energy: {energy_text}", True, (255, 255, 255))  # Change text color as needed
        text_rect = text.get_rect(center=(menu_rect.centerx, menu_rect.centery + 10))  # Add some vertical margin
        surface.blit(text, text_rect)
