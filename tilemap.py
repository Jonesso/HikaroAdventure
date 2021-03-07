import pygame as pg
from settings import *
import pygame
from pytmx.util_pygame import load_pygame
from os import path


class Map:
    def __init__(self, filename):
        self.tmx_data = load_pygame(path.join("res/maps/", filename))
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height

    def get_tile_properties(self, x, y):
        tile_x = x // TILESIZE
        tile_y = y // TILESIZE
        try:
            properties = self.tmx_data.get_tile_properties(tile_x, tile_y, 0)
        except ValueError:
            properties = {"ground": 0}
        if properties is None:
            properties = {"ground": 0}
        return properties

    def blit_all_tiles(self, display, scroll):
        tile_rects = []
        for layer in self.tmx_data:
            for tile in layer.tiles():
                x = tile[0] * TILESIZE - scroll[0]
                y = tile[1] * TILESIZE - scroll[1]
                display.blit(tile[2], (x, y))
                if self.get_tile_properties(tile[0] * TILESIZE, tile[1] * TILESIZE)['ground']:
                    tile_rects.append(pygame.Rect(tile[0] * TILESIZE, tile[1] * TILESIZE, TILESIZE, TILESIZE))
        return tile_rects


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.x + int(WIDTH / 2)
        y = -target.y + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
