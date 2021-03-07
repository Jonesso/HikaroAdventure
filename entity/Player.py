import pygame as pg
from settings import *


class Player(pg.sprite.Sprite):
    def __init__(self, all_sprites, x, y):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load('res/sprites/hero/run_1.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = pg.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.moving_right = False
        self.moving_left = False
        self.y_momentum = 0
        self.air_timer = 0
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]
        self.movement = [0, 0]
        self.tile_rects = []

    def update(self):
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += 2
        if self.moving_left:
            self.movement[0] -= 2
        self.movement[1] += self.y_momentum
        self.y_momentum += 0.2
        if self.y_momentum > 3:
            self.y_momentum = 3

        self.rect, collisions = self.move(self.rect, self.movement, self.tile_rects)

        if collisions['bottom']:
            self.y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

    def collision_test(self, rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, rect, movement, tiles):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
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

    def update_scroll(self, w, h):
        if 0 <= self.rect.x - WIDTH // 4 and self.rect.x + WIDTH // 4 <= w:
            self.true_scroll[0] += (self.rect.x - self.true_scroll[0] - WIDTH // 4) / 14
        if 0 <= self.rect.y - HEIGHT // 4 and self.rect.y + HEIGHT // 4 <= h:
            self.true_scroll[1] += (self.rect.y - self.true_scroll[1] - HEIGHT // 4) / 14
        scroll = self.true_scroll.copy()
        # for images to render correctly
        self.scroll[0] = int(scroll[0])
        self.scroll[1] = int(scroll[1])
