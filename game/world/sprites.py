import pygame as pg
from tools.settings import *


class Block(pg.sprite.Sprite):
    def __init__(self, group, sprite, x, y):
        self.group = group
        pg.sprite.Sprite.__init__(self, self.group)

        self.image = sprite
        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Ladder(Block):
    def __init__(self, groups, sprite, x, y):
        super(Ladder, self).__init__(groups, sprite, x, y)


class Ground(Block):
    def __init__(self, groups, sprite, x, y):
        super(Ground, self).__init__(groups, sprite, x, y)
