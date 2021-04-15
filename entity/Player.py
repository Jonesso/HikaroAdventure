import pygame as pg
import pytmx

from settings import *
from pygame.locals import *
import glob
from sfx.audioplayer import AudioPlayer


class Player(pg.sprite.Sprite):
    """
    Player object, inited by sprite group and start coords
    """

    def __init__(self, all_sprites, x, y, map):
        """
        Constructor for Player

        :param all_sprites: sprite group for Player
        :param x: start X coordinate
        :param y: start Y coordinate
        :type all_sprites: pygame.sprite.Group
        :type x: int
        :type y: int
        :return: Player object
        :rtype: Player
        """
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.image.load('res/sprites/hero/idle_0.png').convert()
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
        self.movement = [0, 0]
        self.tile_rects = []

        self.animation_frames = {}
        self.animation_database = {'idle': self.load_animation("idle", [7, 40, 40, 20]),
                                   'run': self.load_animation("run", [7, 7, 7, 7, 7, 7])}

        self.action = 'idle'
        self.frame = 0
        self.flip = False

        self.audioplayer = AudioPlayer()

        self.key_up_pressed = False
        self.key_down_pressed = False

    def collide_floor(self, col_obj):
        return self.y - col_obj.y < 5

    def update(self):
        """
        Updates the player position on screen, draw animation
        """
        # Movement
        self.movement = [0, 0]
        if self.moving_right:
            self.movement[0] += 2
        if self.moving_left:
            self.movement[0] -= 2
        self.movement[1] += self.y_momentum
        self.y_momentum += 0.2
        if self.y_momentum > 3:
            self.y_momentum = 3

        # Frames update
        self.frame += 1
        if self.frame >= len(self.animation_database[self.action]):
            self.frame = 0

        if self.movement[0] > 0:
            self.action, self.frame = self.change_action(self.action, self.frame, 'run')
            self.flip = False
        if self.movement[0] < 0:
            self.action, self.frame = self.change_action(self.action, self.frame, 'run')
            self.flip = True
        if self.movement[0] == 0:
            self.action, self.frame = self.change_action(self.action, self.frame, 'idle')
        self.image = self.animation_frames[self.animation_database[self.action][self.frame]]

        # Moving and collisions
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
                pg.sprite.spritecollide(self, self.map.ground, False, collided=pg.sprite.collide_circle):
            self.audioplayer.play_grass_sound()

        # Ladder
        if self.key_up_pressed and pg.sprite.spritecollide(self, self.map.ladders, False):
            self.y_momentum = -1
            self.move(self.rect, [0, -1], self.tile_rects)
        if self.key_down_pressed and pg.sprite.spritecollide(self, self.map.ladders, False):
            self.y_momentum = 1
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
                if event.key == K_DOWN:
                    self.key_down_pressed = True
        except AttributeError:
            pass

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
        Player movement by offsets

        :param rect: player block object
        :param movement: x and y offset
        :param tiles: all blocks in map
        :type rect: pygame.Rect
        :type movement: list
        :type tiles: list
        :return: new player rectangle and collision types(bottom, right, ...)
        :rtype: (pygame.Rect, list)
        """
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

    def load_animation(self, action, frame_durations):
        """
        Loading animation for action with frame durations

        :param action: current player action
        :type action: str
        :param frame_durations: list of int with frame durations
        :type frame_durations: list
        :return: list of frames
        :rtype: list
        """
        path = "res/sprites/hero/{}_*.png"
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
