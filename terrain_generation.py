from PIL import Image, ImageDraw
import math
import noise
import random
import numpy as np


def update_point(coords, seed, map_size):
    return noise.snoise2(
        coords[0] / SCALE,
        coords[1] / SCALE,
        octaves=6,
        persistence=0.5,
        lacunarity=2,
        repeatx=map_size[0],
        repeaty=map_size[1],
        base=seed,
    )


SCALE = 256
EXPO_HEIGHT = 2
COLORS = {
    "grass": (34, 139, 34),
    "forest": (0, 100, 0),
    "sand": (238, 214, 175),
    "water": (65, 105, 225),
    "rock": (139, 137, 137),
    "snow": (255, 250, 250),
}

lut_vectors = ((-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1))


def normalize(input_map, minimum, maximum, expo, map_size):
    scale = maximum - minimum
    output_map = np.zeros(map_size)
    for x in range(map_size[0]):
        for y in range(map_size[1]):
            output_map[x][y] = ((input_map[x][y] - minimum) / scale) ** expo
    return output_map


def generate_heightmap(map_size):
    seed = int(random.random() * 1000)
    minimum = 0
    maximum = 0
    heightmap = np.zeros(map_size)

    for x in range(map_size[0]):
        for y in range(map_size[1]):
            new_value = update_point((x, y), seed, map_size)
            heightmap[x][y] = new_value
            if new_value < minimum:
                minimum = new_value
            if new_value > maximum:
                maximum = new_value
    print("Height map generated with seed:", seed)
    return normalize(heightmap, minimum, maximum, EXPO_HEIGHT, map_size)


def get_color(height, slope):
    if height > 0.15 and height < 0.9 and slope > 0.45:
        return COLORS["rock"]
    if height <= 0.15:
        return COLORS["water"]
    elif height > 0.15 and height <= 0.185:
        return COLORS["sand"]
    elif height > 0.185 and height <= 0.34:
        return COLORS["grass"]
    elif height > 0.34 and height <= 0.74:
        return COLORS["forest"]
    elif height > 0.74 and height <= 0.9:
        return COLORS["rock"]
    elif height > 0.9:
        return COLORS["snow"]


def export_texture(heightmap, slopemap, filename, map_size):
    image = Image.new("RGB", map_size, 0)
    draw = ImageDraw.ImageDraw(image)
    for x in range(map_size[0]):
        for y in range(map_size[1]):
            draw.point((x, y), get_color(heightmap[x][y], slopemap[x][y]))
    image.save(filename)
    print(filename, "saved")
    return


def out_of_bounds(coord, map_size):
    if coord[0] < 0 or coord[0] >= map_size[0]:
        return True
    if coord[1] < 0 or coord[1] >= map_size[1]:
        return True
    return False


def generate_slopemap(heightmap, map_size):
    slopemap = np.zeros(map_size)
    minimum = 0
    maximum = 0

    for x in range(map_size[0]):
        for y in range(map_size[1]):
            slope = 0
            for vector in lut_vectors:
                coord = (x + vector[0], y + vector[1])
                if out_of_bounds(coord, map_size):
                    continue
                slope += abs(heightmap[x][y] - heightmap[coord[0]][coord[1]])
            slope = slope / 8
            slopemap[x][y] = slope
            if slope < minimum:
                minimum = slope
            if slope > maximum:
                maximum = slope
    print("Slopemap generated")
    return normalize(slopemap, minimum, maximum, 1, map_size)


def generate_terrain(width, height):
    map_size = (width, height)
    heightmap = generate_heightmap(map_size)
    slopemap = generate_slopemap(heightmap, map_size)
    export_texture(heightmap, slopemap, "./resources/terrain.png", map_size)
    
    colors = []
    image = Image.open('./resources/terrain.png')
    for x in range(image.width):
        for y in range(image.height):
            colors.append(image.getpixel((x,y)))
    
    return colors