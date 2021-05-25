import sys
from pygame.locals import *

from entity.Entity import Entity
from entity.mobs.Enemy import Enemy
from game.entity.heroes.Player import Player
from game.world.tilemap import *
from game.tools.sfx.audioplayer import AudioPlayer
from pygame_widgets import Slider, TextBox
from utils import background_path


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


class Game:
    """
    Main game class, contains all the logic of the game interface
    """

    def __init__(self):
        """
        Constructor, init pygame, screen, display, set caption, set FPS, load map data
        """
        pg.init()
        self.screen = pg.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen
        self.display = pg.Surface((WIDTH // 2, HEIGHT // 2))
        pg.display.set_caption(TITLE)  # set the window name
        self.clock = pg.time.Clock()  # set up the clock
        self.new()
        self.playing = False
        self.audioplayer = AudioPlayer()
        self.click = False

        self.username_textbox_active = False
        self.username_text = ''
        self.username_textbox = pg.Rect(100, 100, 140, 32)

    def load_data(self, level_name):
        """
        Loading all data for chosen map (e.g. music, start coords)

        :param level_name: current level name without '.tmx'
        :type level_name: str
        """
        self.all_sprites = pg.sprite.Group()
        self.bg = pg.image.load(background_path('bg_mnt-valley.jpg'))
        self.bg_x = self.bg_y = 0
        self.level_map = Map("{}.tmx".format(level_name), self.all_sprites)

        self.player = Player(self.all_sprites, 2, 36, self.level_map)  # x, y: start coord-s

        enemy = Enemy(self.all_sprites, 10, 36, self.level_map)
        self.enemies = [enemy]

        # TODO create a dict for levels and starting coords
        # Sounds
        # TODO choose bg_music by level
        self.audioplayer.play_level_sound(level=0)

    def new(self):
        """
        Setup for a new game, initialize variables
        """

        # Fonts
        self.font = pygame.font.Font(None, 40)

    def quit(self):
        """
        Exit from game
        """
        pg.quit()  # stop pygame
        sys.exit()  # stop script

    def update(self):
        """
        Update sprites and display, rendering background
        """
        self.player.update_scroll(self.level_map.width, self.level_map.height)
        self.display.blit(self.bg, (self.bg_x, self.bg_y))  # background move (actually no)
        self.all_sprites.empty()
        self.all_sprites.add(self.player, *self.enemies, *self.level_map.coins)
        player_x = self.player.rect.x // TILESIZE
        player_y = self.player.rect.y // TILESIZE
        self.player.tile_rects, self.player.nearest_blocks = self.level_map.blit_all_tiles \
            (self.display, player_x, player_y, self.player.scroll, self.enemies)
        self.all_sprites.update()

        if self.player.is_dead:
            self.playing = False
            pg.mixer.music.stop()
            self.show_death_screen()

    def draw(self):
        """
        Draws sprites to the display, update pygame display
        """
        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                self.display.blit(pg.transform.flip(sprite.image, self.player.flip, False), (
                    self.player.rect.x - self.player.scroll[0], self.player.rect.y - self.player.scroll[1]))
            if isinstance(sprite, Enemy):
                self.display.blit(pg.transform.flip(sprite.image, sprite.flip, False), (
                    sprite.rect.x - self.player.scroll[0], sprite.rect.y - self.player.scroll[1]))
            if isinstance(sprite, Coin):
                self.display.blit(pg.transform.flip(sprite.image, False, False), (
                    sprite.rect.x - self.player.scroll[0], sprite.rect.y - self.player.scroll[1]))
        score_surf = self.font.render(f'Score: {self.player.score}', False, (0, 0, 0))
        surf = pg.transform.scale(self.display, WINDOW_SIZE)
        self.screen.blit(surf, (0, 0))
        self.screen.blit(score_surf, (WIDTH - 200, 50))
        pg.display.update()  # update display

    def events(self):
        """
        Catch all events
        """
        for event in pg.event.get():  # event loop
            if event.type == QUIT:  # check for window quit
                self.quit()
            if event.type == KEYDOWN:
                # Music fading out on pressed "W" & playing again on pressed "E"
                if event.key == K_w:
                    self.audioplayer.mute()
                if event.key == K_e:
                    self.audioplayer.resume()
                if event.key == K_ESCAPE:
                    if self.playing:
                        self.click = False
                        self.show_pause_screen()
                if self.username_textbox_active:
                    if event.key == pg.K_BACKSPACE:
                        self.username_text = self.username_text[:-1]
                    else:
                        self.username_text += event.unicode
            if self.playing:
                self.player.update_event(event)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True
                if self.username_textbox.collidepoint(event.pos):
                    self.username_textbox_active = not self.username_textbox_active
                else:
                    self.username_textbox_active = False

        return pg.event.get()

    def show_menu_screen(self):
        bg = pg.image.load(background_path('japan_menu.png'))
        bg = pg.transform.scale(bg, WINDOW_SIZE)
        x = (WIDTH - button_width) // 2
        y = HEIGHT // 16
        while True:
            self.screen.blit(bg, (0, 0))
            draw_text('Hikaro Adventure', self.font, WHITE, self.screen,
                      WIDTH // 2 - len('Hikaro Adventure') * button_width // 30, y * 3)

            mx, my = pg.mouse.get_pos()

            button_game = pygame.Rect(x, y * 6, button_width, button_height)
            button_options = pygame.Rect(x, y * 8, button_width, button_height)
            button_exit = pygame.Rect(x, y * 10, button_width, button_height)

            if button_game.collidepoint((mx, my)):
                if self.click:
                    self.show_game_screen("level01")
            if button_options.collidepoint((mx, my)):
                if self.click:
                    self.show_options_screen()
            if button_exit.collidepoint((mx, my)):
                if self.click:
                    self.quit()
            pygame.draw.rect(self.screen, LIGHTGREY, button_game)
            pygame.draw.rect(self.screen, LIGHTGREY, button_options)
            pygame.draw.rect(self.screen, LIGHTGREY, button_exit)
            draw_text('Start', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Start') * button_width // 30,
                      y * 6 + button_height // 2 - 11)
            draw_text('Options', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Options') * button_width // 30,
                      y * 8 + button_height // 2 - 11)
            draw_text('Exit', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Exit') * button_width // 30,
                      y * 10 + button_height // 2 - 11)
            self.click = False
            self.events()
            pg.display.update()
            self.clock.tick(FPS)

    def show_game_screen(self, level_name):
        """
        Game cycle: update-draw-events-clock(fps)
        Running while playing == True
        """
        self.load_data(level_name)
        self.playing = True
        while self.playing:
            self.update()
            self.draw()
            self.events()
            self.clock.tick(FPS)  # maintain 60 fps

    def show_options_screen(self):
        bg = pg.image.load(background_path('japan_menu.png'))
        bg = pg.transform.scale(bg, WINDOW_SIZE)
        x = WIDTH // 16
        y = HEIGHT // 16
        sliderMusic = Slider(self.screen, WIDTH // 3, y * 5, WIDTH // 3, 40, min=0, max=100, step=1, colour=DARKGREY,
                             handleColour=LIGHTGREY, handleRadius=30, initial=self.audioplayer.get_music_volume())
        sliderSounds = Slider(self.screen, WIDTH // 3, y * 7, WIDTH // 3, 40, min=0, max=100, step=1, colour=DARKGREY,
                              handleColour=LIGHTGREY, handleRadius=30, initial=self.audioplayer.get_sound_volume())
        outputMusic = TextBox(self.screen, sliderMusic.getX() + sliderMusic.getWidth() + 50, y * 5, 50, 40, fontSize=30)
        outputSounds = TextBox(self.screen, sliderSounds.getX() + sliderSounds.getWidth() + 50, y * 7, 50, 40,
                               fontSize=30)
        running_options = True
        while running_options:
            self.screen.blit(bg, (0, 0))
            draw_text('Options', self.font, WHITE, self.screen,
                      WIDTH // 2 - len('Options') * button_width // 30, y * 3)

            mx, my = pg.mouse.get_pos()

            button_exit = pygame.Rect(x * 5, y * 14, button_width, button_height)
            button_save = pygame.Rect(x * 9, y * 14, button_width, button_height)

            if button_exit.collidepoint((mx, my)):
                if self.click:
                    running_options = False
            if button_save.collidepoint((mx, my)):
                if self.click:
                    running_options = False
                    self.audioplayer.set_sounds_volume(sliderSounds.getValue())
                    self.audioplayer.set_music_volume(sliderMusic.getValue())

            pygame.draw.rect(self.screen, LIGHTGREY, button_exit)
            pygame.draw.rect(self.screen, LIGHTGREY, button_save)

            draw_text('Exit', self.font, WHITE, self.screen,
                      x * 5 + button_width // 2 - len('Exit') * button_width // 30,
                      y * 14 + button_height // 2 - 11)
            draw_text('Save', self.font, WHITE, self.screen,
                      x * 9 + button_width // 2 - len('Save') * button_width // 30,
                      y * 14 + button_height // 2 - 11)

            self.click = False

            sliderMusic.listen(self.events())
            sliderMusic.draw()
            outputMusic.setText(sliderMusic.getValue())
            outputMusic.draw()

            sliderSounds.listen(self.events())
            sliderSounds.draw()
            outputSounds.setText(sliderSounds.getValue())
            outputSounds.draw()

            self.events()
            pg.display.update()
            self.clock.tick(FPS)

    def show_pause_screen(self):
        paused = True
        pg.mixer.music.pause()
        bg = pg.image.load(background_path('japan_menu.png'))
        bg = pg.transform.scale(bg, WINDOW_SIZE)
        x = (WIDTH - button_width) // 2
        y = HEIGHT // 16
        while paused:
            self.screen.blit(bg, (0, 0))
            draw_text('Pause', self.font, WHITE, self.screen,
                      WIDTH // 2 - len('Pause') * button_width // 30, y * 3)

            mx, my = pg.mouse.get_pos()

            button_unpause = pygame.Rect(x, y * 6, button_width, button_height)
            button_options = pygame.Rect(x, y * 8, button_width, button_height)
            button_main_menu = pygame.Rect(x, y * 10, button_width, button_height)

            if button_unpause.collidepoint((mx, my)):
                if self.click:
                    paused = False
                    pg.mixer.music.unpause()
            if button_options.collidepoint((mx, my)):
                if self.click:
                    self.click = False
                    self.show_options_screen()
            if button_main_menu.collidepoint((mx, my)):
                if self.click:
                    # paused = False
                    self.playing = False
                    self.click = False
                    self.show_menu_screen()
                    break

            pygame.draw.rect(self.screen, LIGHTGREY, button_unpause)
            pygame.draw.rect(self.screen, LIGHTGREY, button_options)
            pygame.draw.rect(self.screen, LIGHTGREY, button_main_menu)

            draw_text('Unpause', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Unpause') * button_width // 30,
                      y * 6 + button_height // 2 - 11)
            draw_text('Options', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Options') * button_width // 30,
                      y * 8 + button_height // 2 - 11)
            draw_text('Main menu', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Main menu') * button_width // 30,
                      y * 10 + button_height // 2 - 11)

            self.click = False
            self.events()
            pg.display.update()
            self.clock.tick(FPS)

    def show_death_screen(self):
        bg = pg.image.load(background_path('japan_menu.png'))
        bg = pg.transform.scale(bg, WINDOW_SIZE)
        x = (WIDTH - button_width) // 2
        y = HEIGHT // 16
        self.username_textbox.x = x
        self.username_textbox.y = y * 7
        while True:
            self.screen.blit(bg, (0, 0))
            draw_text('YOU DIED', self.font, WHITE, self.screen,
                      x + 30, y * 3)
            draw_text(f'Your score: {self.player.score}', self.font, WHITE, self.screen,
                      x + 12, y * 5)
            draw_text('Your name: ', self.font, WHITE, self.screen,
                      self.username_textbox.x - 180, y * 7)

            mx, my = pg.mouse.get_pos()
            button_send_results = pygame.Rect(x, y * 9, button_width, button_height)
            button_main_menu = pygame.Rect(x, y * 11, button_width, button_height)

            if button_send_results.collidepoint((mx, my)):
                if self.click:
                    # TODO send request method
                    # return to main screen after request
                    self.show_menu_screen()
                    break
            if button_main_menu.collidepoint((mx, my)):
                if self.click:
                    self.click = False
                    self.show_menu_screen()
                    break

            pygame.draw.rect(self.screen, LIGHTGREY, button_send_results)
            pygame.draw.rect(self.screen, LIGHTGREY, button_main_menu)

            draw_text('Send request', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Send request') * button_width // 30 - 10,
                      y * 9 + button_height // 2 - 11)
            draw_text('Main menu', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Main menu') * button_width // 30 - 15,
                      y * 11 + button_height // 2 - 11)

            txt_surface = self.font.render(self.username_text, False, BLACK)
            self.username_textbox.w = max(200, txt_surface.get_width() + 10)

            self.screen.blit(txt_surface, (self.username_textbox.x + 5, self.username_textbox.y + 5))
            pg.draw.rect(self.screen, WHITE, self.username_textbox, 2)

            self.click = False
            self.events()
            pg.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    # create the game object and show menu
    g = Game()
    g.show_menu_screen()
