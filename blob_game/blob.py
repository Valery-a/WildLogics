import pygame
import math

from sympy import true
from configValues import *
import pymunk
from pymunk.autogeometry import march_hard, simplify_curves

class Blob( ):
    """ blob Sprite with basic acceleration, turning, braking and reverse """

    def __init__( self, x, y, space, mass=0.01, rotations=360, heading = 0, size = 1, view_distance = 85, view_angle = 45, attack_power = 0.5 ):
        """ A blob Sprite which pre-rotates up to <rotations> lots of
            angled versions of the image.  Depending on the sprite's
            heading-direction, the correctly angled image is chosen.
            The base blob-image should be pointing North/Up.          """
                
        # stats
        self.energy = 100
        self.health = 40
        self.attack_power = attack_power
        self.attack_power_to_blobs = attack_power / 2
        self.size = size
        self.view_distance = view_distance * size
        self.view_angle = view_angle
        self.current_nearest_object_distance = 0
        self.current_nearest_object_angle = 0
        self.current_nearest_object_type = "none"
        self.speed = 0
        self.max_speed = 10
        self.max_reverse_speed = -self.max_speed / 2
        self.type = "blob"  
        
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
        self.shape.friction = 0.5
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
    
    def is_clicked(self, pos):
        # Check if the point (pos) is within the bounding box of the blob
        return (self.rect.center[0] - self.rect.width * 0.35) <= pos[0] <= (self.rect.center[0] + self.rect.width * 0.35) and \
               (self.rect.center[1] - self.rect.height * 0.35) <= pos[1] <= (self.rect.center[1] + self.rect.height * 0.35)
    
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
        self.energy -= 0.025
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
        self.energy -= 0.05
        self.body.apply_force_at_local_point((self.speed, 0), (0, 0))
            
    def blob_is_eating(self, object, gene):
        if object == self:
            return False
        
        if self.mouth_shape.shapes_collide(object.shape).normal != pymunk.Vec2d(-0,-0):
            if object.type == 'food':
                self.energy += self.attack_power / 2
                object.health -= self.attack_power
                gene.fitness += 1
            elif object.type == 'blob':
                self.energy += self.attack_power / 10
                object.health -= self.attack_power_to_blobs
                gene.fitness += 0.01
                
            if object.health < 0:
                return True
            
        return False
    
    def nearest_object(self, objects):
        found_object = False
        for object in objects:
            if object == self:
                continue
            distance_to_object = self.field_of_view_shape.point_query(object.body.position)
            if round(distance_to_object.distance, 2) < 0:
                found_object = True
                a = object.body.position.y - self.body.position.y
                b = object.body.position.x - self.body.position.x
                angle_to_object = math.atan2(a, b) - math.atan2(self.body.rotation_vector.y, self.body.rotation_vector.x)
                self.current_nearest_object_distance = round(distance_to_object.distance, 2)
                self.current_nearest_object_angle = round(abs(angle_to_object), 2)
                self.current_nearest_object_type = object.type
                if round(distance_to_object.distance, 2) <= self.current_nearest_object_distance:
                    a = object.body.position.y - self.body.position.y
                    b = object.body.position.x - self.body.position.x
                    angle_to_object = math.atan2(a, b) - math.atan2(self.body.rotation_vector.y, self.body.rotation_vector.x)
                    self.current_nearest_object_distance = round(distance_to_object.distance, 2)
                    self.current_nearest_object_angle = round(angle_to_object, 2)
                    self.current_nearest_object_type = object.type
        
        if not found_object:
            self.current_nearest_object_distance = 0
            self.current_nearest_object_angle = 0
            self.current_nearest_object_type = "none"
            
        #print(f"{self.current_nearest_object_distance} - {self.current_nearest_object_angle} - {self.current_nearest_object_type}")
            
    def update( self ):
        """ Sprite update function, calcualtes any new position """
        self.energy -= 0.01
        lower_acceleration_speed = self.speed - 0.3
        lower_reverse_speed = self.speed + 0.3
        if self.speed > 0:
            self.speed = max(lower_acceleration_speed, 0)
        else:
            self.speed = min(lower_reverse_speed, 0)
            
        self.turn(0)
        
    def draw(self, win, translation, zoom_factor=1):
        for name, image in self.images.items():
            current_image = pygame.transform.scale_by(image, zoom_factor)
            img_width, img_height = current_image.get_rect().size
            pos = pymunk.Transform.translation(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) @ pymunk.Transform.scaling(zoom_factor) @ translation @ pymunk.Transform.translation(-WINDOW_WIDTH / 2, -WINDOW_HEIGHT / 2) @ pymunk.Vec2d(self.body.position.x, self.body.position.y)
            x = pos.x - img_width / 2
            y = pos.y - img_height / 2
            self.rect.x = x
            self.rect.y = y
            self.rect.center = (pos)
            self.rect.width = current_image.get_rect().width
            self.rect.height = current_image.get_rect().height
            win.blit(current_image, (x, y))
