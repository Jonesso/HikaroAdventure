import sys
from pygame.locals import *
from entity.Player import Player
from tilemap import *


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

    def load_data(self, level_name):
        """
        Loading all data for chosen map (e.g. music, start coords)

        :param level_name: current level name without '.tmx'
        :type level_name: str
        """
        self.all_sprites = pg.sprite.Group()
        self.bg = pg.image.load("res/backgrounds/bg_mnt-valley.jpg")
        self.bg_x = self.bg_y = 0
        self.level_map = Map("{}.tmx".format(level_name), self.all_sprites)
        self.player = Player(self.all_sprites, 2, 36)  # x, y: start coord-s
        self.player.set_map(self.level_map)
        # TODO create a dict for levels and starting coords

        # Sounds
        # TODO choose bg_music by level
        pg.mixer.music.load('res/music/levels/bg_music.wav')
        pg.mixer.music.play(-1)  # -1 = repeat infinitely

    def new(self):
        """
        Setup for a new game, initialize variables
        """
        # Sounds
        pg.mixer.pre_init(44100, -16, 2, 512)  # frequency, size, amount of channels, buffer
        pg.mixer.set_num_channels(64)  # default is 8, which is not enough

        grass_sound = [pygame.mixer.Sound('res/music/sounds/grass_0.wav'),
                       pygame.mixer.Sound('res/music/sounds/grass_1.wav')]
        grass_sound[0].set_volume(0.2)
        grass_sound[1].set_volume(0.2)

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
        self.player.tile_rects = self.level_map.blit_all_tiles(self.display, self.player.scroll)
        self.all_sprites.update()

    def draw(self):
        """
        Draws sprites to the display, update pygame display
        """
        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                self.display.blit(pg.transform.flip(sprite.image, self.player.flip, False), (
                    self.player.rect.x - self.player.scroll[0], self.player.rect.y - self.player.scroll[1]))
        surf = pg.transform.scale(self.display, WINDOW_SIZE)
        self.screen.blit(surf, (0, 0))
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
                    pg.mixer.music.fadeout(1000)
                if event.key == K_e:
                    pg.mixer.music.play(-1)
                if event.key == K_ESCAPE:
                    self.playing = False
            if self.playing:
                self.player.update_event(event)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

    def show_menu_screen(self):
        bg = pg.image.load("res/backgrounds/japan_menu.png")
        bg = pg.transform.scale(bg, WINDOW_SIZE)
        x = WIDTH // 12
        y = HEIGHT // 16
        button_width = 200
        button_height = 50
        while True:
            self.screen.blit(bg, (0, 0))
            draw_text('Main menu', self.font, WHITE, self.screen, x, y * 2)

            mx, my = pg.mouse.get_pos()

            button_game = pygame.Rect(x, y * 4, button_width, button_height)
            button_options = pygame.Rect(x, y * 6, button_width, button_height)

            if button_game.collidepoint((mx, my)):
                if self.click:
                    self.show_game_screen("map")
            if button_options.collidepoint((mx, my)):
                if self.click:
                    self.show_options_screen()
            pygame.draw.rect(self.screen, LIGHTGREY, button_game)
            pygame.draw.rect(self.screen, LIGHTGREY, button_options)
            draw_text('Start', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Start') * button_width // 30,
                      y * 4 + button_height // 2 - 11)
            draw_text('Options', self.font, WHITE, self.screen,
                      x + button_width // 2 - len('Options') * button_width // 30,
                      y * 6 + button_height // 2 - 11)
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
        print("options")
        pass


# create the game object and show menu
g = Game()
g.show_menu_screen()
