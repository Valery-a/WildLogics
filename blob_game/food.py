import pygame
import pymunk
import math

class Food():
    def __init__( self, x, y, space, size = 1):
        # stats
        self.size = size * 0.5 # 0.5 scaling for food (don't want to be too big)
        self.mass = size * 0.01 # mass is relative to size
        self.health = (size * 5) / 1.3
        
        # generating image
        self.generated_image = self.generate_food()
        self.rect = self.generated_image.get_rect()
        self.rot_img = []
        self.min_angle = 1
        
        for i in range( 360 ):
            rotated_image = pygame.transform.rotozoom( self.generated_image, 360-90-( i*self.min_angle ), 1 )
            self.rot_img.append( rotated_image )
        
        # setting up rigid body
        radius = self.rect.width / 4
        self.moment = pymunk.moment_for_circle(self.mass, 0, radius)
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        space.add(self.body, self.shape)
        
        self.heading = self.body.angle
        self.image = self.rot_img[int( self.heading / self.min_angle ) % len( self.rot_img )]
        self.rect.center = self.body.position
        self.mask = pygame.mask.from_surface(self.image)
        
    def generate_food(self):
        food_image = pygame.transform.scale_by(pygame.image.load('./resources/food_32.png'), self.size).convert_alpha()

        return food_image
    
    def update(self):
        self.heading = self.body.angle
        h_a = self.heading * 180 / math.pi
        # Decide which is the correct image to display
        image_index = int( h_a / self.min_angle ) % len( self.rot_img )
        # Only update the image if it's changed
        if ( self.image != self.rot_img[ image_index ] ):
                self.image = self.rot_img[ image_index ]
                
        self.rect = self.image.get_rect()
    
    def draw(self, win):
        pos = (self.body.position.x - self.rect.width / 2, self.body.position.y - self.rect.height / 2)
        win.blit(self.image, pos)
