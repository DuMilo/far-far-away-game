import pgzrun
from pgz_tile_system import *

TILE_SIZE = 16
ROWS = 30
COLS = 20
WIDTH = TILE_SIZE * ROWS
HEIGHT = TILE_SIZE * COLS
TITLE = "Tão tão distante!"

platforms = build_tile_map("platformer_platforms.csv", TILE_SIZE)
obstacles = build_tile_map("platformer_obstacles.csv", TILE_SIZE)
coins = build_tile_map("platformer_coins.csv", TILE_SIZE)
backgrounds = build_tile_map("platformer_background.csv", TILE_SIZE)

player = Actor("player_right")
player.bottomleft = (0, 256)

player.velocity_x = 3
player.velocity_y = 0
gravity = 0.5
jump_velocity = -7

player.is_on_ground = False
player.direction = 'right'

JUMP_BUFFER_FRAMES = 8
player.jump_buffer_timer = 0
COYOTE_TIME_FRAMES = 6
player.coyote_timer = 0

walk_right_frames = ["walk_right_1", "walk_right_2", "walk_right_3", "walk_right_4", "walk_right_5", "walk_right_6"]
walk_left_frames = ["walk_left_1", "walk_left_2", "walk_left_3", "walk_left_4", "walk_left_5", "walk_left_6"]
idle_right_image = "player_right"
idle_left_image = "player_left"

player.animation_timer = 0
player.current_frame = 0
ANIMATION_SPEED = 5

def draw():
    screen.clear()

    for background in backgrounds:
        background.draw()
        
    for platform in platforms:
        platform.draw()

    for obstacle in obstacles:
        obstacle.draw()

    for coin in coins:
        coin.draw()

    player.draw()

def update():
    is_moving_horizontally = False

    if keyboard.left and player.left > 0:
        player.x -= player.velocity_x
        player.direction = 'left'
        is_moving_horizontally = True
        
        player.animation_timer += 1
        if player.animation_timer >= ANIMATION_SPEED:
            player.animation_timer = 0
            player.current_frame = (player.current_frame + 1) % len(walk_left_frames)
            player.image = walk_left_frames[player.current_frame]

    if keyboard.right and player.right < WIDTH:
        player.x += player.velocity_x
        player.direction = 'right'
        is_moving_horizontally = True

        player.animation_timer += 1
        if player.animation_timer >= ANIMATION_SPEED:
            player.animation_timer = 0
            player.current_frame = (player.current_frame + 1) % len(walk_right_frames)
            player.image = walk_right_frames[player.current_frame]

    if player.jump_buffer_timer > 0:
        player.jump_buffer_timer -= 1
    if player.coyote_timer > 0:
        player.coyote_timer -= 1

    if player.jump_buffer_timer > 0 and player.coyote_timer > 0:
        player.velocity_y = jump_velocity
        player.is_on_ground = False
        player.coyote_timer = 0
        player.jump_buffer_timer = 0

    player.y += player.velocity_y
    player.velocity_y += gravity

    player.is_on_ground = False
    
    if player.velocity_y >= 0:
        colliding_platforms_indices = player.collidelistall(platforms)

        for platform_index in colliding_platforms_indices:
            platform = platforms[platform_index]
            if player.bottom <= platform.top + player.velocity_y:
                player.bottom = platform.top
                player.velocity_y = 0
                player.is_on_ground = True
                player.coyote_timer = COYOTE_TIME_FRAMES
                break

    if not is_moving_horizontally and player.is_on_ground:
        if player.direction == 'right':
            player.image = idle_right_image
        else:
            player.image = idle_left_image

def on_key_down(key):
    if key == keys.UP:
        player.jump_buffer_timer = JUMP_BUFFER_FRAMES

pgzrun.go()