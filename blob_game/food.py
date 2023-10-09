import pygame

class Food(pygame.sprite.Sprite):
    def __init__( self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        
        self.size = size
        self.image = self.generate_food()
        self.rect = self.image.get_rect()
        self.rect.center = ( x, y )
        self.position = pygame.math.Vector2( x, y )
        self.health = 20
        self.mask = pygame.mask.from_surface(self.image)
    def generate_food(self):
        food_image = pygame.transform.scale(pygame.image.load('./resources/food_size_5_32.png'), (self.size * 32, self.size * 32)).convert_alpha()


        if self.size == 5:
            food_image = pygame.transform.scale(pygame.image.load('./resources/food_size_5_32.png'), (self.size * 32, self.size * 32)).convert_alpha()

        # TODO: add other food size 1 through 4

        if food_image is None:
            # Default food image if size condition is not met
            food_image = pygame.Surface((self.size * 32, self.size * 32))
            food_image.fill((255, 0, 0))  # Set a red color as a placeholder

        return food_image

        
    def update(self):
        self.rect.center = (self.position[0], self.position[1])
    
