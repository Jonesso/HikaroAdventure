import time

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
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=4, buffer=4096)  # frequency, size, amount of channels, buffer
        pygame.mixer.set_num_channels(64)  # default is 8, which is not enough
        self.clock = pygame.time.get_ticks()


    def play_level_sound(self, level):
        pygame.mixer.music.load(self.bg_level_sounds[level])
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)  # -1 = repeat infinitely

    def play_grass_sound(self):
        channel1 = pygame.mixer.Channel(1)
        channel2 = pygame.mixer.Channel(2)
        sound = self.grass_sounds[random.randint(0, 1)]
        if pygame.time.get_ticks() - self.clock > 300:
            self.clock = pygame.time.get_ticks()
            if channel1.get_busy():
                channel2.play(sound)
                channel2.fadeout(400)
            else:
                channel1.play(sound)
                channel1.fadeout(400)

    def play_jump_sound(self):
        pygame.mixer.Sound.play(self.jump_sound)

    def mute(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def set_sounds_volume(self, value):
        for sound in self.grass_sounds:
            sound.set_volume(value / 100)

    def get_music_volume(self):
        return pygame.mixer.music.get_volume() * 100

    def get_sound_volume(self):
        return self.grass_sounds[0].get_volume() * 100
