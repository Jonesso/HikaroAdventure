import pygame as pg
from tools.settings import *
import pygame
from pytmx.util_pygame import load_pygame
from os import path
from game.world.sprites import *


class Map:
    """
    Game map with:
        tmx_data: current map

        width: map width in blocks * TILESIZE

        height: map height in block * TILESIZE
    """

    def __init__(self, filename, group):
        """
        Constructor for Map

        :param filename: file name in res/maps with '.tmx'
        :type filename: str
        """
        self.tmx_data = load_pygame(path.join("game/res/maps/", filename))
        self.width = self.tmx_data.width * TILESIZE
        self.height = self.tmx_data.height * TILESIZE
        self.group = group  # Sprite group

        self.ladders = []
        self.ground = []

        self.properties = {}
        self.fill_properties()

    def get_tile_properties(self, x, y):
        """
        Get properties for tile with coords x & y

        :param x: X coordinate
        :param y: Y coordinate
        :type x: int
        :type y: int
        :return: properties of tile
        :rtype: dict
        """
        tile_x = x // TILESIZE
        tile_y = y // TILESIZE
        try:
            properties = self.tmx_data.get_tile_properties(tile_x, tile_y, 0)
        except ValueError:
            properties = {"ground": 0, "ladder": 0}
        if properties is None:
            properties = {"ground": 0, "ladder": 0}
        keys = ['ground', 'ladder']
        for key in keys:
            if properties.get(key) is None:
                properties.update({key: 0})
        return properties

    def blit_all_tiles(self, display, px, py, scroll, enemies):
        """
        Return list of all interactive (e.g. ground) blocks

        :param display: game screen
        :type display: pygame.Surface
        :param scroll: camera scroll params
        :type scroll: list
        :return: list of all interactive blocks
        """
        # For Player
        self.ladders = []
        tile_rects = []
        nearest_blocks = []
        screen_tiles = self.find_nearest_tiles(px, py,
                                               43 if px < 24 or px > self.width // TILESIZE - 24 else 23,
                                               25 if py > self.height // TILESIZE - 13 or py < 13 else 15)
        for tile in screen_tiles:
            x = tile[0][0]
            y = tile[0][1]
            if not tile[1] is None:
                properties = tile[1][0]
                tile_image = tile[1][1]
                display.blit(tile_image, (x * TILESIZE - scroll[0], y * TILESIZE - scroll[1]))
                if abs(px - x) <= 2 and abs(py - y) <= 2:
                    if int(properties['ground']):
                        tile_rects.append(pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE))
                        nearest_blocks.append(Ground(self.group, tile_image, x, y))
                    if int(properties['ladder']):
                        self.ladders.append(Ladder(self.group, tile_image, x, y))
        # For Enemy
        for enemy in enemies:
            enemy.tile_rects = []
            enemy.nearest_blocks = []
            for tile in self.find_nearest_tiles(enemy.rect.x // TILESIZE, enemy.rect.y // TILESIZE, 2, 2):
                x = tile[0][0]
                y = tile[0][1]
                if not tile[1] is None:
                    properties = tile[1][0]
                    tile_image = tile[1][1]
                    if int(properties['ground']):
                        enemy.tile_rects.append(pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE))
                        enemy.nearest_blocks.append(Ground(self.group, tile_image, x, y))
        return tile_rects, nearest_blocks

    def fill_properties(self):
        for layer in self.tmx_data:
            for tile in layer.tiles():
                self.properties.update(
                    {(tile[0], tile[1]): (self.get_tile_properties(tile[0] * TILESIZE, tile[1] * TILESIZE), tile[2])})

    def find_nearest_tiles(self, x, y, range_x, range_y):
        tiles = []
        for x1 in range(x - range_x, x + range_x + 1):
            for y1 in range(y - range_y, y + range_y + 1):
                if 0 <= x1 < self.width // TILESIZE and 0 <= y1 < self.height // TILESIZE:
                    properties = self.properties.get((x1, y1))
                    if properties is not None:
                        tiles.append(((x1, y1), properties))
        return tiles
