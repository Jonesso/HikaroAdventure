import pygame as pg
import glob
import os
from game.utils import sprites_path
from game.tools.settings import *


class Block(pg.sprite.Sprite):
    sprite_path = None
    animation = {}

    def __init__(self, group, sprite, x, y):
        self.group = group
        pg.sprite.Sprite.__init__(self, self.group)

        self.image = sprite
        self.image.set_colorkey(WHITE)

        self.animation_frames = {}
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def load_animation(self, action, frame_durations):
        """
        Loading animation for action with frame durations

        :param action: current entity action
        :type action: str
        :param frame_durations: list of int with frame durations
        :type frame_durations: list
        :return: list of frames
        :rtype: list
        """
        path = os.path.join(self.sprite_path, '{}_*.png')
        sprites = glob.glob(path.format(action))
        animation_frame_data = []
        n = 0
        for frame in frame_durations:
            animation_frame_id = sprites[n][sprites[n].rfind("\\") + 1: sprites[n].find(".")]
            animation_image = pg.image.load(sprites[n]).convert()
            animation_image.set_colorkey((255, 255, 255))
            self.animation_frames[animation_frame_id] = animation_image.copy()
            for i in range(frame):
                animation_frame_data.append(animation_frame_id)
            n += 1
        return animation_frame_data

    def change_action(self, action_var, frame, new_value):
        if action_var != new_value:
            action_var = new_value
            frame = 0
        return action_var, frame


class Ladder(Block):
    def __init__(self, groups, sprite, x, y):
        super(Ladder, self).__init__(groups, sprite, x, y)


class Ground(Block):
    def __init__(self, groups, sprite, x, y):
        super(Ground, self).__init__(groups, sprite, x, y)


class Coin(Block):
    sprite_path = os.path.join(sprites_path(), 'gold_coin')

    def __init__(self, groups, sprite, x, y):
        super(Coin, self).__init__(groups, sprite, x, y)

        self.animation = {'coin': self.load_animation("coin", [7 for _ in range(8)])}
        self.action = 'coin'
        self.frame = 0
        self.image = pg.image.load(os.path.join(self.sprite_path, 'coin_0.png')).convert()
        self.image.set_colorkey(WHITE)

    def update(self):
        self.frame += 1
        if self.frame >= len(self.animation[self.action]):
            self.frame = 0
        self.action, self.frame = self.change_action(self.action, self.frame, 'coin')
        self.image = self.animation_frames[self.animation[self.action][self.frame]]


class Lava(Block):
    def __init__(self, groups, sprite, x, y):
        super(Lava, self).__init__(groups, sprite, x, y)