from turtle import position
from networkx import center
import pygame
import math
import sys
import pymunk
from pymunk.autogeometry import march_hard, simplify_curves

class Blob( ):
    """ blob Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, x, y, space, mass=0.01, rotations=360, heading = 0, size = 3, view_distance = 30, view_angle = 20 ):
        """ A blob Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base blob-image should be pointing North/Up.          """
        
        # stats
        self.energy = 100
        self.attack_power = 1
        self.size = size
        self.view_distance = view_distance * size
        self.view_angle = view_angle
        
        # setting up blob images
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
        
        # Setting up rigid body
        self.mass = mass
        width = self.rot_img['full_image'][0].get_rect().width * 0.3
        height = self.rot_img['full_image'][0].get_rect().height * 0.46
        self.shape = pymunk.Circle(None, width)
        self.moment = pymunk.moment_for_circle(self.mass, 0, width)
        self.body = pymunk.Body(self.mass, self.moment)  
        self.shape.body = self.body
        self.shape.elasticity = 0.7  # Bounciness
        self.body.position = x, y     
        body_size = [
            (width / 2 , -height / 5), 
            (width / 2 + width * 0.5, -height / 5), 
            (width / 2 + width * 0.5, height / 5), 
            (width / 2, height / 5)
            ]
        self.mouth_shape = pymunk.Poly(self.body, body_size)
        points = []
        starting_angle = -(90 - self.view_angle)
        p = (0, self.view_distance)
        for i in range(self.view_angle * 2):
            theta = (starting_angle * (math.pi / 180))
            p_prime = (round((p[0]*math.cos(theta)-p[1]*math.sin(theta)), 2), round((p[0]*math.sin(theta)+ p[1]*math.cos(theta)), 2))
            points.append(p_prime)
            starting_angle -= 1
            
        points.append((0, 0))
        self.field_of_view_shape = pymunk.Poly(self.body, points)
        self.field_of_view_shape.filter = pymunk.ShapeFilter(0, 0)
        space.add(self.body, self.shape, self.mouth_shape, self.field_of_view_shape)     
        self.field_of_view_shape.color = (183, 183, 183, 1)
        self.body.angle = heading
        
        # define image used
        self.heading = self.body.angle                           # pointing right (in radians)
        self.images['full_image'] = self.rot_img['full_image'][int( self.heading / self.min_angle ) % len( self.rot_img['full_image'] )]
        #self.images['mouth_image'] = self.rot_img['mouth_image'][int( self.heading / self.min_angle ) % len( self.rot_img['mouth_image'] )]
        self.images['body_image'] = self.rot_img['body_image'][int( self.heading / self.min_angle ) % len( self.rot_img['body_image'] )]
        self.rect = self.images['full_image'].get_rect()
        
        # masks and position
        self.body_mask = pygame.mask.from_surface(self.images['full_image'])
        self.rect.center = ( x, y )
        
        # movement
        self.reversing = False
        self.speed = 0
        self.max_speed = 10
        self.max_reverse_speed = -self.max_speed / 2    
        self.position = pygame.math.Vector2( self.body.position.x, self.body.position.y )
        
    def generate_blob(self):
        body_image = pygame.transform.scale_by(pygame.image.load( './resources/blob_circle.png' ), self.size).convert_alpha()
        #mouth_image = pygame.transform.scale_by(pygame.image.load( './resources/blob_mouth_32.png' ), self.size).convert_alpha()
        self.images['body_image'] = body_image
        #self.images['mouth_image'] = mouth_image
        
        full_image = body_image.copy()
        for name, image in self.images.items():
            full_image.blit(image, (0,0))
            
        self.images['full_image'] = full_image.convert_alpha()

    def generate_geometry_points(self, surface):
        def sample_func(point):
            p = int(point[0]), int(point[1])
            color = surface.get_at(p)
            return color.hsla[2]

        line_set = march_hard(
            pymunk.BB(0, 0, surface.get_width()-1, surface.get_height()-1), 200, 200, 1, sample_func
        )
        
        points = []
        for polyline in line_set:
            line = simplify_curves(polyline, 1.0)
            for i in range(len(line) - 1):
                p1 = line[i]
                points.append((p1.x - surface.get_rect().width / 2, p1.y - surface.get_rect().height / 2))
        
        return points

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
                #self.images['mouth_image'] = self.rot_img['mouth_image'][ image_index ]
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
        if self.mouth_shape.shapes_collide(food.shape).normal != pymunk.Vec2d(-0,-0):
            self.energy += self.attack_power / 2
            food.health -= self.attack_power
            if food.health < 0:
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
            
        self.turn(0)
        
    def draw(self, win):
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
