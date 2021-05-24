import os

import pygame as pg
import glob

from game.tools.settings import *
from game.tools.sfx.audioplayer import AudioPlayer


class Entity(pg.sprite.Sprite):
    """
    Entity object, inited by sprite group and start coords
    """
    sprite_path = None
    audioplayer = AudioPlayer()
    speed = 0

    def __init__(self, all_sprites, x, y, map):
        """
        Constructor for any Entity

        :param all_sprites: sprite group for Entity
        :param x: start X coordinate
        :param y: start Y coordinate
        :type all_sprites: pygame.sprite.Group
        :type x: int
        :type y: int
        :return: Entity object
        :rtype: Entity
        """
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load(os.path.join(self.sprite_path, 'idle_0.png')).convert()
        self.image.set_colorkey(WHITE)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = pg.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.map = map

        self.moving_right = False
        self.moving_left = False
        self.y_momentum = 0
        self.air_timer = 0
        self.jump = False

        self.movement = [0, 0]
        self.tile_rects = []
        self.nearest_blocks = []

        self.animation_frames = {}
        self.animation_database = {'idle': self.load_animation("idle", [7, 40, 40, 20]),
                                   'run': self.load_animation("run", [7, 7, 7, 7, 7, 7]),
                                   'jump': self.load_animation("jump", [70, 30, 9, 9])}
        self.action = 'idle'
        self.frame = 0
        self.flip = False

    def update(self):
        """
        Updates the entity position on screen, draw animation
        """
        # Movement
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += self.speed
        if self.moving_left:
            self.movement[0] -= self.speed
        self.movement[1] += self.y_momentum
        self.y_momentum += 0.2
        if self.y_momentum > 3:
            self.y_momentum = 3

        # Frames update
        self.frame += 1
        if self.frame >= len(self.animation_database[self.action]):
            self.frame = 0
        # Moving and collisions
        ground_collide = pg.sprite.spritecollide(self, self.nearest_blocks, False, collided=pg.sprite.collide_circle)
        if self.movement[0] > 0 and ground_collide:
            self.action, self.frame = self.change_action(self.action, self.frame, 'run')
            self.flip = False
        if self.movement[0] < 0 and ground_collide:
            self.action, self.frame = self.change_action(self.action, self.frame, 'run')
            self.flip = True
        if self.movement[0] > 0 and not ground_collide:
            self.action, self.frame = self.change_action(self.action, self.frame, 'jump')
            self.flip = False
        if self.movement[0] < 0 and not ground_collide:
            self.action, self.frame = self.change_action(self.action, self.frame, 'jump')
            self.flip = True

        if self.movement[0] == 0 and ground_collide:
            self.action, self.frame = self.change_action(self.action, self.frame, 'idle')

        self.image = self.animation_frames[self.animation_database[self.action][self.frame]]

        self.rect, collisions = self.move(self.rect, self.movement, self.tile_rects)

        if collisions['bottom']:
            self.y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

        if collisions['top']:
            self.y_momentum = 0

        # Ground
        if (self.moving_left or self.moving_right) and collisions['bottom'] and \
                pg.sprite.spritecollide(self, self.nearest_blocks, False, collided=pg.sprite.collide_circle):
            self.audioplayer.play_grass_sound()

    def collision_test(self, rect, tiles):
        """
        Check for collisions

        :param rect: block object for collision check
        :type rect: pygame.Rect
        :param tiles: all blocks in map
        :type tiles: list
        :return: list of hit blocks
        """
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, rect, movement, tiles):
        """
        Entity movement by offsets

        :param rect: entity block object
        :param movement: x and y offset
        :param tiles: all blocks in map
        :type rect: pygame.Rect
        :type movement: list
        :type tiles: list
        :return: new entity rectangle and collision types(bottom, right, ...)
        :rtype: (pygame.Rect, dict)
        """
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

        # Check map borders
        if movement[0] > 0 and rect.x + TILESIZE + movement[0] >= self.map.width:
            rect.right = self.map.width
        elif movement[0] < 0 and rect.x - movement[0] <= 0:
            rect.left = 0

        rect.x += movement[0]

        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True
        rect.y += movement[1]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True

        return rect, collision_types

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
        """
        Change action from 'action_var' to 'new_value'

        :param action_var: Current action
        :type action_var: str
        :param frame: Current frame
        :type frame: int
        :param new_value: New action
        :type new_value: str
        :return: Tuple of new action and frame
        :rtype: (str, int)
        """
        if action_var != new_value:
            action_var = new_value
            frame = 0
        return action_var, frame
