import os

import pygame as pg

from entity.Entity import Entity
from game.tools.settings import *
from pygame.locals import *
from utils import sprites_path


class Player(Entity):
    sprite_path = os.path.join(sprites_path(), 'hero')
    speed = 2

    def __init__(self, all_sprites, x, y, map):
        super().__init__(all_sprites, x, y, map)
        n_x = n_y = 0
        w, h = map.width // TILESIZE, map.height // TILESIZE
        if 0 <= x <= 22:
            n_x = 0
        elif 22 < x < w - WIDTH // 4 - self.rect.width:
            n_x = self.x - WIDTH // 4
        elif w - 22 <= x <= w:
            n_x = w * TILESIZE - WIDTH // 2 - self.rect.width

        if 0 <= y <= 22:
            n_y = self.rect.height * 2
        elif 22 < y < h - HEIGHT // 4 - self.rect.height:
            n_y = self.y - HEIGHT // 4
        elif w - 22 <= y <= w:
            n_y = h * TILESIZE - HEIGHT // 2 - self.rect.height

        self.true_scroll = [n_x, n_y]
        self.scroll = self.true_scroll.copy()

        self.key_up_pressed = False
        self.key_down_pressed = False
        self.key_z_pressed = False

    def update(self):
        super(Player, self).update()
        # Ladder
        if self.key_up_pressed and pg.sprite.spritecollide(self, self.map.ladders, False):
            self.y_momentum = -1
            self.move(self.rect, [0, -1], self.tile_rects)
        if self.key_down_pressed and pg.sprite.spritecollide(self, self.map.ladders, False):
            self.y_momentum = 1
            self.move(self.rect, [0, 1], self.tile_rects)

        if self.key_z_pressed:
            self.y_momentum = 0.3
            self.move(self.rect, [0, 1], self.tile_rects)

    def update_event(self, event):
        try:
            if event.key == K_RIGHT:
                self.moving_right = True
            if event.key == K_LEFT:
                self.moving_left = True
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.moving_right = False
                if event.key == K_LEFT:
                    self.moving_left = False
                if event.key == K_UP:
                    self.key_up_pressed = False
                if event.key == K_DOWN:
                    self.key_down_pressed = False
                if event.key == K_z:
                    self.key_z_pressed = False
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.key_up_pressed = True
                    if self.jump:
                        self.audioplayer.play_jump_sound()
                        self.y_momentum = -5
                        self.jump = False
                    if self.air_timer < 6:
                        self.audioplayer.play_jump_sound()
                        self.y_momentum = -5
                        self.jump = True
                if event.key == K_z:
                    self.key_z_pressed = True
                if event.key == K_DOWN:
                    self.key_down_pressed = True
        except AttributeError:
            pass

    def update_scroll(self, w, h):
        """
        Control camera limits

        :param w: map width
        :param h: map height
        :type w: int
        :type h: int
        """
        deltaY = abs(self.rect.y - self.true_scroll[1] - HEIGHT // 4)
        deltaX = abs(self.rect.x - self.true_scroll[0] - WIDTH // 4)

        if self.rect.x + deltaX > WIDTH // 4 and self.rect.x - deltaX < w - WIDTH // 4:
            self.true_scroll[0] += (self.rect.x - self.true_scroll[0] - WIDTH // 4) / 14

        if self.rect.y + deltaY >= HEIGHT // 4 and self.rect.y - deltaY + self.rect.height <= h - HEIGHT // 4:
            self.true_scroll[1] += (self.rect.y - self.true_scroll[1] - HEIGHT // 4) / 14
        scroll = self.true_scroll.copy()
        # for images to render correctly
        self.scroll[0] = int(scroll[0])
        self.scroll[1] = int(scroll[1])
