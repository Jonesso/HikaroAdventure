import os
import pygame
from game.entity.Entity import Entity
from game.utils import sprites_path
from game.tools.settings import *


class Enemy(Entity):
    sprite_path = os.path.join(sprites_path(), 'hero')
    clock = pygame.time.get_ticks()
    speed = 1
    view_range = 7

    def __init__(self, all_sprites, x, y, map):
        super().__init__(all_sprites, x, y, map)
        self.player = None
        self.animation_database.update({'attack': self.load_animation('attack', [8, 8, 5])})
        self.kill_player = False

    def move_left(self):
        self.moving_right = False
        self.moving_left = True

    def move_right(self):
        self.moving_left = False
        self.moving_right = True

    def stay_idle(self):
        self.moving_left = False
        self.moving_right = False

    def update(self):
        super(Enemy, self).update()
        self.logic()

    def logic(self):
        x, y = self.player.rect.x, self.player.rect.y
        ex, ey = self.rect.x, self.rect.y
        self.attack = abs(x - ex) < TILESIZE and abs(y - ey) < TILESIZE
        self.flip = self.attack and x < ex

        if pygame.sprite.spritecollide(self, self.map.lava, False):
            self.map.enemies.remove(self)

        if self.kill_player:
            if pygame.time.get_ticks() - self.clock > 500:
                self.player.is_dead = True
            return

        if abs(x - ex) < self.view_range * TILESIZE and abs(y - ey) < self.view_range * TILESIZE:
            if x < ex:
                if not self.attack:
                    self.flip = True
                    self.move_left()
            else:
                if not self.attack:
                    self.flip = False
                    self.move_right()
        else:
            self.stay_idle()

        if pygame.sprite.collide_rect(self, self.player):
            self.kill_player = True

        if pygame.time.get_ticks() - self.clock > 1000 and not self.kill_player:
            self.clock = pygame.time.get_ticks()

