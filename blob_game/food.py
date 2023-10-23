import pygame
import pymunk
import math
from configValues import *
class Food():
    def __init__( self, x, y, space, size = 1):
        # stats
        self.size = size * 0.5 # 0.5 scaling for food (don't want to be too big)
        self.mass = size * 0.01 # mass is relative to size
        self.health = (size * 10)
        self.type = "food"
        
        # generating image
        self.generated_image = self.generate_food()
        self.rect = self.generated_image.get_rect()
        self.min_angle = 1
        
        # setting up rigid body
        radius = self.rect.width / 4
        self.moment = pymunk.moment_for_circle(self.mass, 0, radius)
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.5
        space.add(self.body, self.shape)
        
        self.heading = self.body.angle
        self.image = pygame.transform.scale_by(pygame.transform.rotate(self.generated_image, -int( self.heading * 180 / math.pi / self.min_angle ) % 360), self.size)
        self.rect.center = self.body.position
        self.mask = pygame.mask.from_surface(self.image)
        
    def generate_food(self):
        food_image = pygame.image.load('./resources/food_32.png').convert_alpha()

        return food_image
    
    def update(self):
        self.heading = self.body.angle
        h_a = self.heading * 180 / math.pi
        # Decide which is the correct image to display
        image_index = int( h_a / self.min_angle ) % 360
        # Only update the image if it's changed
        self.image = pygame.transform.rotate(self.generated_image, -image_index)
                
        self.rect = self.image.get_rect()
    
    def draw(self, win, translation, zoom_factor=1):
        image = pygame.transform.scale_by(self.image, zoom_factor)
        pos = pymunk.Transform.translation(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) @ pymunk.Transform.scaling(zoom_factor) @ translation @ pymunk.Transform.translation(-WINDOW_WIDTH / 2, -WINDOW_HEIGHT / 2) @ pymunk.Vec2d(self.body.position.x, self.body.position.y)
        x = pos.x - image.get_rect().width / 2
        y = pos.y - image.get_rect().height / 2
        self.rect.x = x
        self.rect.y = y
        self.rect.center = (pos)
        self.rect.width = image.get_rect().width
        self.rect.height = image.get_rect().height
        win.blit(image, (x, y))


    def is_clicked(self, pos):
        # Check if the point (pos) is within the bounding box of the blob
        return (self.rect.center[0] - self.rect.width * 0.35) <= pos[0] <= (self.rect.center[0] + self.rect.width * 0.35) and \
               (self.rect.center[1] - self.rect.height * 0.35) <= pos[1] <= (self.rect.center[1] + self.rect.height * 0.35)