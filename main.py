import sys

from pygame.locals import *

from entity.Player import Player
from tilemap import *

clock = pygame.time.Clock()  # set up the clock

pygame.init()  # initiate pygame

pygame.display.set_caption(TITLE)  # set the window name

WINDOW_SIZE = (WIDTH, HEIGHT)  # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen

display = pygame.Surface((WIDTH // 2, HEIGHT // 2))

bg = pygame.image.load("res/backgrounds/bg_mnt-valley.jpg")

map = Map("map.tmx")
camera = Camera(map.width, map.height)
player = Player(3, 26)  # x, y: start coord-s

bg_x = 0
bg_y = 0

while True:  # game loop
    player.update_scroll()
    display.blit(bg, (bg_x, bg_y))  # background move (actually no)

    # # big most backward rectangle
    # pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    # for background_object in background_objects:
    #     obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
    #                            background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
    #                            background_object[1][3])
    #     # color based on parallax coefficient
    #     if background_object[0] == 0.5:
    #         pygame.draw.rect(display, (14, 222, 150), obj_rect)  # brighter green
    #     else:  # 0.25
    #         pygame.draw.rect(display, (9, 91, 85), obj_rect)  # darker green

    tile_rects = map.blit_all_tiles(display, player.scroll)
    camera.update(player)
    player.update(tile_rects)

    display.blit(player.image, (player.rect.x - player.scroll[0], player.rect.y - player.scroll[1]))

    for event in pygame.event.get():  # event loop
        if event.type == QUIT:  # check for window quit
            pygame.quit()  # stop pygame
            sys.exit()  # stop script
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                player.moving_right = True
            if event.key == K_LEFT:
                player.moving_left = True
            if event.key == K_UP:
                if player.air_timer < 6:
                    player.y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                player.moving_right = False
            if event.key == K_LEFT:
                player.moving_left = False
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()  # update display
    clock.tick(60)  # maintain 60 fps
