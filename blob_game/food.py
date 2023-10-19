import pygame
import pymunk

class Food():
    def __init__( self, x, y, space, size = 1):
        # stats
        self.size = size * 0.5 # 0.5 scaling for food (don't want to be too big)
        self.mass = size * 0.01 # mass is relative to size
        
        # generating image
        self.image = self.generate_food()
        self.rect = self.image.get_rect()
        
        # setting up rigid body
        radius = self.rect.width / 4
        self.moment = pymunk.moment_for_circle(self.mass, 0, radius)
        self.body = pymunk.Body(self.mass, self.moment)
        self.shape = pymunk.Circle(self.body, radius)
        self.body.position = x, y
        self.shape.friction = 0.5
        space.add(self.body, self.shape)
        
        self.rect.center = self.body.position
        self.health = 20
        self.mask = pygame.mask.from_surface(self.image)
        
    def generate_food(self):
        food_image = pygame.transform.scale_by(pygame.image.load('./resources/food_32.png'), self.size).convert_alpha()

        return food_image
    
    def draw(self, win):
        pos = (self.body.position.x - self.rect.width / 2, self.body.position.y - self.rect.height / 2)
        win.blit(self.image, pos)
