import os
import pygame
from entity.Entity import Entity
from utils import sprites_path
from game.tools.settings import *


class Enemy(Entity):
    sprite_path = os.path.join(sprites_path(), 'hero')
    clock = pygame.time.get_ticks()

    def move_left(self):
        self.moving_left = True

    def move_right(self):
        self.moving_left = True

    def stay_idle(self):
        self.moving_left = False
        self.moving_right = False

    def update(self):
        super(Enemy, self).update()
        self.logic()

    def logic(self):
        if pygame.time.get_ticks() - self.clock < 1500:
            self.move_left()
        if 1500 < pygame.time.get_ticks() - self.clock < 4000:
            self.stay_idle()
        if pygame.time.get_ticks() - self.clock > 4000:
            self.move_right()
        if pygame.time.get_ticks() - self.clock > 5500:
            self.clock = pygame.time.get_ticks()
