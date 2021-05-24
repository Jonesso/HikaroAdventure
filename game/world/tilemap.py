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
        self.player_x = -999
        self.player_y = -999

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

    def blit_all_tiles(self, display, px, py, scroll, isPlayer):
        """
        Return list of all interactive (e.g. ground) blocks

        :param display: game screen
        :type display: pygame.Surface
        :param scroll: camera scroll params
        :type scroll: list
        :return: list of all interactive blocks
        """
        tile_rects = []
        nearest_blocks = []
        if isPlayer:
            if self.player_x == -999:
                self.player_x = px
                self.player_y = py
            if self.player_x != px or self.player_y != py:
                self.player_x = px
                self.player_y = py
            self.ladders = []
        for layer in self.tmx_data:
            for tile in layer.tiles():
                x = tile[0] * TILESIZE - scroll[0]
                y = tile[1] * TILESIZE - scroll[1]
                # For Enemy
                if not isPlayer:
                    if abs(px - tile[0]) <= 2 and abs(py - tile[1]) <= 2:
                        properties = self.get_tile_properties(tile[0] * TILESIZE, tile[1] * TILESIZE)
                        if properties['ground']:
                            tile_rects.append(pygame.Rect(tile[0] * TILESIZE, tile[1] * TILESIZE, TILESIZE, TILESIZE))
                            nearest_blocks.append(Ground(self.group, tile[2], tile[0], tile[1]))
                # For Player
                elif abs(px - tile[0]) <= 45 and abs(py - tile[1]) <= 40:
                    display.blit(tile[2], (x, y))
                    if abs(px - tile[0]) <= 2 and abs(py - tile[1]) <= 2:
                        properties = self.get_tile_properties(tile[0] * TILESIZE, tile[1] * TILESIZE)
                        if properties['ground']:
                            tile_rects.append(pygame.Rect(tile[0] * TILESIZE, tile[1] * TILESIZE, TILESIZE, TILESIZE))
                            nearest_blocks.append(Ground(self.group, tile[2], tile[0], tile[1]))
                        if properties['ladder']:
                            self.ladders.append(Ladder(self.group, tile[2], tile[0], tile[1]))
        return tile_rects, nearest_blocks
