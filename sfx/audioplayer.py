import pygame
import random

pygame.mixer.init()


class AudioPlayer:
    # All sound effects in game
    bg_level_sounds = ['res/music/levels/bg_music.wav']
    grass_sounds = [
        pygame.mixer.Sound('res/music/sounds/grass_0.wav'),
        pygame.mixer.Sound('res//music/sounds/grass_1.wav'),
    ]
    jump_sound = pygame.mixer.Sound('res//music/sounds/jump.wav')

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)  # frequency, size, amount of channels, buffer
        pygame.mixer.set_num_channels(64)  # default is 8, which is not enough

    def play_level_sound(self, level):
        pygame.mixer.music.load(self.bg_level_sounds[level])
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)  # -1 = repeat infinitely

    def play_grass_sound(self):
        pygame.mixer.Sound.play(self.grass_sounds[random.randint(0, 1)]).set_volume(0.2)

    def play_jump_sound(self):
        pygame.mixer.Sound.play(self.jump_sound).set_volume(0.4)

    def mute(self):
        pygame.mixer.music.fadeout(1000)

    def resume(self):
        pygame.mixer.music.play(-1)


