import pygame
from entity.Player import Player

pygame.init()


class Enemy(Player):
    def __init__(self):
        self.image = pygame.image.load('').convert()
        self.animation_database = {'idle': None,
                                   'run': None
                                   }
