import pygame
import math

class Blob( pygame.sprite.Sprite ):
    """ blob Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, blob_image, x, y, rotations=360, heading = 0 ):
        """ A blob Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base blob-image should be pointing North/Up.          """
        pygame.sprite.Sprite.__init__(self)
        # Pre-make all the rotated versions
        # This assumes the start-image is pointing up-screen
        # Operation must be done in degrees (not radians)
        self.rot_img   = []
        self.min_angle = ( 360 / rotations ) 
        for i in range( rotations ):
            # This rotation has to match the angle in radians later
            # So offet the angle (0 degrees = "north") by 90° to be angled 0-radians (so 0 rad is "east")
            rotated_image = pygame.transform.rotozoom( blob_image, 360-90-( i*self.min_angle ), 1 )
            self.rot_img.append( rotated_image )
        self.min_angle = math.radians( self.min_angle )   # don't need degrees anymore
        # define the image used
        self.heading   = heading                           # pointing right (in radians)
        self.image       = self.rot_img[int( self.heading / self.min_angle ) % len( self.rot_img )]
        self.rect        = self.image.get_rect()
        self.rect.center = ( x, y )
        # movement
        self.reversing = False
        self.speed     = 0
        self.max_speed = 4
        self.max_reverse_speed = -1.5    
        self.velocity  = pygame.math.Vector2( 0, 0 )
        self.position  = pygame.math.Vector2( x, y )

    def turn( self, angle_degrees ):
        """ Adjust the angle the blob is heading, if this means using a 
            different blob-image, select that here too """
        self.heading += math.radians( angle_degrees ) 
        # Decide which is the correct image to display
        image_index = int( self.heading / self.min_angle ) % len( self.rot_img )
        # Only update the image if it's changed
        if ( self.image != self.rot_img[ image_index ] ):
            x,y = self.rect.center
            self.image = self.rot_img[ image_index ]
            self.rect  = self.image.get_rect()
            self.rect.center = (x,y)

    def accelerate( self, amount ):
        """ Increase the speed either forward or reverse """
        if ( not self.reversing ):
            self.speed += amount
            if self.speed > self.max_speed:
                self.speed = self.max_speed

    def brake( self ):
        self.speed -= 0.4
        if self.speed < self.max_reverse_speed:
            self.speed = self.max_reverse_speed

    def update( self ):
        """ Sprite update function, calcualtes any new position """
        lower_acceleration_speed = self.speed - 0.05
        lower_reverse_speed = self.speed + 0.05
        if self.speed > 0:
            self.speed = max(lower_acceleration_speed, 0)
        else:
            self.speed = min(lower_reverse_speed, 0)
        self.velocity.from_polar( ( self.speed, math.degrees( self.heading ) ) )
        self.position += self.velocity
        self.rect.center = ( round(self.position[0]), round(self.position[1] ) )