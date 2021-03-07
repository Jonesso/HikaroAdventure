import pygame, sys
from pytmx.util_pygame import load_pygame

clock = pygame.time.Clock()  # set up the clock

from pygame.locals import *

pygame.init()  # initiate pygame

pygame.display.set_caption('Pygame Window')  # set the window name

WINDOW_SIZE = (1280, 720)  # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen

display = pygame.Surface((640, 360))

true_scroll = [50, 100]  # x, y

player_image = pygame.image.load('res/sprites/hero/run_1.png').convert()
player_image.set_colorkey((255, 255, 255))

player_rect = pygame.Rect(50, 300, player_image.get_width(), player_image.get_height())
test_rect = pygame.Rect(100, 100, 100, 50)

grass_image = pygame.image.load('res/blocks/grass.png')
dirt_image = pygame.image.load('res/blocks/dirt.png')

bg = pygame.image.load("res/backgrounds/bg_mnt-valley.jpg")

TILE_SIZE = 16


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


def get_tile_properties(tmxdata, x, y):
    world_x = x
    world_y = y
    tile_x = world_x // TILE_SIZE
    tile_y = world_y // TILE_SIZE
    try:
        properties = tmxdata.get_tile_properties(tile_x, tile_y, 0)
    except ValueError:
        properties = {"ground": 0}
    if properties is None:
        properties = {"ground": 0}
    return properties


tmxdata = load_pygame("res/maps/map.tmx")
world_offset = [0, 0]

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

bg_x = 0
bg_y = 0

while True:  # game loop

    true_scroll[0] += (player_rect.x - true_scroll[0] - WINDOW_SIZE[0] // 4) / 14
    true_scroll[1] += (player_rect.y - true_scroll[1] - WINDOW_SIZE[1] // 4) / 14
    scroll = true_scroll.copy()
    # for images to render correctly
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    display.blit(bg, (bg_x, bg_y))

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

    tile_rects = []
    for layer in tmxdata:
        for tile in layer.tiles():
            x = tile[0] * TILE_SIZE - scroll[0]
            y = tile[1] * TILE_SIZE - scroll[1]
            display.blit(tile[2], (x, y))
            if get_tile_properties(tmxdata, tile[0] * TILE_SIZE, tile[1] * TILE_SIZE)['ground']:
                tile_rects.append(pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
        bg_x -= 2
    if moving_left:
        player_movement[0] -= 2
        bg_x += 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    display.blit(player_image, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get():  # event loop
        if event.type == QUIT:  # check for window quit
            pygame.quit()  # stop pygame
            sys.exit()  # stop script
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()  # update display
    clock.tick(60)  # maintain 60 fps
