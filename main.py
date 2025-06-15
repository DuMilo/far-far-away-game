import pgzrun
from pgzero.builtins import clock
from pgz_tile_platformer_system import *


TILE_SIZE = 16
ROWS = 30
COLS = 20
WIDTH = TILE_SIZE * ROWS
HEIGHT = TILE_SIZE * COLS
TITLE = "Tão tão distante!"


camera_x = 0
camera_y = 750


platforms = build_tile_map("platformer_platforms.csv", TILE_SIZE)
obstacles = build_tile_map("platformer_obstacles.csv", TILE_SIZE)
coins = build_tile_map("platformer_coins.csv", TILE_SIZE)
backgrounds = build_tile_map("platformer_background.csv", TILE_SIZE)
enemies_1 = build_tile_map("platformer_enemies_1.csv", TILE_SIZE)
enemies_2 = build_tile_map("platformer_enemies_2.csv", TILE_SIZE)
diamonds = build_tile_map("platformer_diamonds.csv", TILE_SIZE)


player = Actor("idle_right_1")
player.bottomleft = (0, 1000)


player.velocity_x = 3
player.velocity_y = 0
gravity = 0.5
jump_velocity = -7


player.health = 5
player.is_on_ground = False
player.direction = 'right'
player.is_invincible = False
player.invincibility_timer = 0
game_over = False
score = 0
game_state = 'menu'
sound_on = True


hearts = []
for i in range(player.health):
    heart = Actor("tiles/tile_0042")
    heart.topright = (WIDTH - 10 - (i * (heart.width + 5)), 10)
    hearts.append(heart)

coin_ui_icon = Actor("tiles/tile_0002")
coin_ui_icon.topleft = (10, 10)


button_start = Actor("ui/start_button")
button_start.pos = (WIDTH / 2, HEIGHT / 2 - 10)
button_sound = Actor("ui/music_button")
button_sound.pos = (WIDTH / 2 + 210, HEIGHT / 2 + 130)
button_quit = Actor("ui/quit_button")
button_quit.pos = (WIDTH / 2, HEIGHT / 2 + 50)


JUMP_BUFFER_FRAMES = 8
player.jump_buffer_timer = 0
COYOTE_TIME_FRAMES = 6
player.coyote_timer = 0


walk_right_frames = [
    "walk_right_1", "walk_right_2", "walk_right_3", "walk_right_4",
    "walk_right_5", "walk_right_6"
]
walk_left_frames = [
    "walk_left_1", "walk_left_2", "walk_left_3", "walk_left_4",
    "walk_left_5", "walk_left_6"
]
idle_right_frames = [
    "idle_right_1", "idle_right_2", "idle_right_3", "idle_right_4"
]
idle_left_frames = [
    "idle_left_1", "idle_left_2", "idle_left_3", "idle_left_4"
]
hurt_right_frames = [
    "hurt_right_1", "hurt_right_2", "hurt_right_3", "hurt_right_4"
]
hurt_left_frames = [
    "hurt_left_1", "hurt_left_2", "hurt_left_3", "hurt_left_4"
]
attack_right_frames = [
    "attack_right_1", "attack_right_2", "attack_right_3",
    "attack_right_4"
]
attack_left_frames = [
    "attack_left_1", "attack_left_2", "attack_left_3",
    "attack_left_4"
]
enemie_1_frames = [
    "enemie_1_sprite_1", "enemie_1_sprite_2"
]
enemie_2_frames = [
    "enemie_2_sprite_1", "enemie_2_sprite_2"
]


player.animation_timer = 0
player.current_frame = 0
ANIMATION_SPEED = 5


music.play('down_under')


def on_music_end():
    if sound_on:
        music.play('down_under')


def draw_game():
    screen.clear()

    for background in backgrounds:
        pos = (background.left - camera_x, background.top - camera_y)
        screen.blit(background.image, pos)

    for platform in platforms:
        pos = (platform.left - camera_x, platform.top - camera_y)
        screen.blit(platform.image, pos)

    for obstacle in obstacles:
        pos = (obstacle.left - camera_x, obstacle.top - camera_y)
        screen.blit(obstacle.image, pos)

    for coin in coins:
        pos = (coin.left - camera_x, coin.top - camera_y)
        screen.blit(coin.image, pos)

    for enemy in enemies_1:
        pos = (enemy.left - camera_x, enemy.top - camera_y)
        screen.blit(enemy.image, pos)

    for enemy in enemies_2:
        pos = (enemy.left - camera_x, enemy.top - camera_y)
        screen.blit(enemy.image, pos)

    for diamond in diamonds:
        pos = (diamond.left - camera_x, diamond.top - camera_y)
        screen.blit(diamond.image, pos)

    if not player.is_invincible or player.animation_timer % 4 < 2:
        pos = (player.left - camera_x, player.top - camera_y)
        screen.blit(player.image, pos)

    coin_ui_icon.draw()
    score_text = f"x{score}"
    screen.draw.text(
        score_text,
        midleft=(coin_ui_icon.right + 6, coin_ui_icon.centery),
        color="white",
        fontsize=24,
        shadow=(1, 1),
        scolor="black"
    )

    for heart in hearts:
        heart.draw()

    if game_over:
        screen.draw.text(
            "Game Over!",
            center=(WIDTH / 2, HEIGHT / 2),
            color="red",
            fontsize=80,
            shadow=(2, 2),
            scolor="black"
        )


def draw_menu():
    screen.clear()
    screen.fill("black")
    screen.draw.text(
        TITLE,
        center=(WIDTH / 2, HEIGHT / 2 - 100),
        color="white",
        fontsize=60
    )
    button_start.draw()
    button_sound.draw()
    button_quit.draw()


def draw():
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()


def update_game():
    global camera_x, camera_y, score, game_over

    if game_over:
        return

    is_moving_horizontally = False

    if keyboard.left and player.left > 0:
        player.x -= player.velocity_x
        player.direction = 'left'
        is_moving_horizontally = True
    
    if keyboard.right and player.right < WIDTH:
        player.x += player.velocity_x
        player.direction = 'right'
        is_moving_horizontally = True

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

    if player.is_invincible:
        player.invincibility_timer -= 1
        if player.invincibility_timer <= 0:
            player.is_invincible = False
    else:
        if player.collidelist(obstacles) != -1:
            player.health -= 1
            player.is_invincible = True
            player.invincibility_timer = 90
            player.velocity_y = jump_velocity * 0.6
            if sound_on:
                sounds.sfx_hurt.play()
            if hearts:
                hearts.pop()

            if player.health <= 0:
                game_over = True
                clock.schedule_unique(quit, 3.0)

    player.is_on_ground = False
    if player.velocity_y >= 0:
        indices = player.collidelistall(platforms)
        for platform_index in indices:
            platform = platforms[platform_index]
            if player.bottom <= platform.top + player.velocity_y:
                player.bottom = platform.top
                player.velocity_y = 0
                player.is_on_ground = True
                player.coyote_timer = COYOTE_TIME_FRAMES
                break

    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
            if sound_on:
                sounds.sfx_coin.play()

    player.animation_timer += 1
    if player.is_invincible:
        if player.direction == 'right':
            frame_index = (
                player.animation_timer // 15 % len(hurt_right_frames)
            )
            player.image = hurt_right_frames[frame_index]
        else:
            frame_index = (
                player.animation_timer // 15 % len(hurt_left_frames)
            )
            player.image = hurt_left_frames[frame_index]

    elif is_moving_horizontally and player.is_on_ground:
        if player.animation_timer >= ANIMATION_SPEED:
            player.animation_timer = 0
            if player.direction == 'right':
                player.current_frame = (
                    (player.current_frame + 1) % len(walk_right_frames)
                )
                player.image = walk_right_frames[player.current_frame]
            else:
                player.current_frame = (
                    (player.current_frame + 1) % len(walk_left_frames)
                )
                player.image = walk_left_frames[player.current_frame]

    elif player.is_on_ground:
        if player.animation_timer >= ANIMATION_SPEED:
            player.animation_timer = 0
            if player.direction == 'right':
                player.current_frame = (
                    (player.current_frame + 1) % len(idle_right_frames)
                )
                player.image = idle_right_frames[player.current_frame]
            else:
                player.current_frame = (
                    (player.current_frame + 1) % len(idle_left_frames)
                )
                player.image = idle_left_frames[player.current_frame]

    target_x = player.x - WIDTH / 2
    target_y = player.y - HEIGHT / 2

    camera_x += (target_x - camera_x) * 0.05
    camera_y += (target_y - camera_y) * 0.05


def update():
    if game_state == 'playing':
        update_game()


def on_key_down(key):
    global game_state
    if game_state == 'playing':
        if key == keys.UP and not game_over:
            player.jump_buffer_timer = JUMP_BUFFER_FRAMES
            if sound_on:
                sounds.sfx_jump.play()


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == 'menu':
        if button_start.collidepoint(pos):
            game_state = 'playing'
        
        if button_quit.collidepoint(pos):
            quit()
        
        if button_sound.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                button_sound.image = 'ui/music_button'
                music.unpause()
            else:
                button_sound.image = 'ui/no_music_button'
                music.pause()


pgzrun.go()