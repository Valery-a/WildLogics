import random
import pygame
from terrain_generation import COLORS

class Entity:
    def __init__(self, x, y, terrain_type=None):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type

    def move(self, dx, dy, terrain_colors, sw, sh):
        new_x = self.x + dx
        new_y = self.y + dy

        # Ensure the entity doesn't move out of bounds
        new_x = max(0, min(new_x, sw - 1))
        new_y = max(0, min(new_y, sh - 1))

        # Ensure the entity only moves on its specified terrain
        if self.terrain_type:
            target_terrain = COLORS[self.terrain_type]
            if terrain_colors[new_y * sw + new_x] != target_terrain:
                return

        self.x = new_x
        self.y = new_y

    def draw(self, surface, tile_size, color=(255, 0, 0)):
        rect = (self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        pygame.draw.rect(surface, color, rect)


# Example usage:
# fish = Entity(10, 10, "water")
# fish.move(1, 0, terrain_colors, sw, sh)  # Moves right if the next tile is water
