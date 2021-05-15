import pygame
import random
from utils import music_levels_path, sounds_path

pygame.mixer.init()


class AudioPlayer:
    """
    Class that is responsible for all sound effects in game
    """
    bg_level_sounds = [music_levels_path('bg_music')]
    grass_sounds = [
        pygame.mixer.Sound(sounds_path('grass_0')),
        pygame.mixer.Sound(sounds_path('grass_1')),
    ]
    jump_sound = pygame.mixer.Sound(sounds_path('jump'))

    def __init__(self):
        """
        Constructor of AudioPlayer class
        
        :return: AudioPlayer object
        :rtype:  AudioPlayer
        """
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=4,
                              buffer=4096)  # frequency, size, amount of channels, buffer
        pygame.mixer.set_num_channels(64)  # default is 8, which is not enough
        self.set_music_volume(0.1 * 100)  # TODO load from cfg all settings
        self.set_sounds_volume(0.3 * 100)
        self.clock = pygame.time.get_ticks()

    def play_level_sound(self, level):
        """
        Plays background music of each level

        :param level: level index
        """
        pygame.mixer.music.load(self.bg_level_sounds[level])
        self.set_music_volume(0.1 * 100)
        pygame.mixer.music.play(-1)  # -1 = repeat infinitely

    def play_grass_sound(self):
        """
        Plays sound of hero when he's walking on grass sprite
        """
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
        """
        Plays sound of hero when he's jumping
        """
        pygame.mixer.Sound.play(self.jump_sound)

    def mute(self):
        """
        Mutes background music
        """
        pygame.mixer.music.pause()

    def resume(self):
        """
        Replays background music
        """

        pygame.mixer.music.unpause()

    def set_music_volume(self, value):
        """
        Sets volume of background music

        :param value: volume percent
        """
        pygame.mixer.music.set_volume(value / 100)

    def set_sounds_volume(self, value):
        """
        Sets volume of sound effects

        :param value: volume percent
        """
        for sound in self.grass_sounds:
            sound.set_volume(value / 100)
        self.jump_sound.set_volume(value / 100)

    def get_music_volume(self):
        """
        Gets background music volume percent

        :rtype: float
        :return: background music volume percent
        """
        return pygame.mixer.music.get_volume() * 100

    def get_sound_volume(self):
        """
        Gets sound effects volume percent

        :rtype: float
        :return: sound effects volume percent
        """
        return self.grass_sounds[0].get_volume() * 100
