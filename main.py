import pgzrun
from pgzero.builtins import clock, Actor, Rect, sounds, music, keys, keyboard
from pgz_tile_platformer_system import *


TILE_SIZE = 16
ROWS = 30
COLS = 20
WIDTH = TILE_SIZE * ROWS
HEIGHT = TILE_SIZE * COLS
TITLE = "Far far away!"
GRAVITY = 0.5


class Enemy(Actor):

    def __init__(self, image, pos, patrol_type, frames, speed=0.5, distance=30):
        super().__init__(image, pos)
        self.patrol_type = patrol_type
        self.frames = frames
        self.patrol_distance = distance
        self.animation_timer = 0
        self.current_frame = 0
        self.animation_speed = 8

        if self.patrol_type == 'vertical':
            self.velocity_y = speed
            self.patrol_start_y = self.y
        else: 
            self.velocity_x = speed
            self.patrol_start_x = self.x

    def update(self):
        self._patrol()
        self._animate()

    def _patrol(self):
        if self.patrol_type == 'vertical':
            self.y += self.velocity_y
            if abs(self.y - self.patrol_start_y) >= self.patrol_distance:
                self.velocity_y *= -1
        else: 
            self.x += self.velocity_x
            if abs(self.x - self.patrol_start_x) >= self.patrol_distance:
                self.velocity_x *= -1
    
    def _animate(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

class Player(Actor):

    def __init__(self, image, pos, frames):
        super().__init__(image, pos)
        self.frames = frames
        self.velocity_x = 3
        self.velocity_y = 0
        self.jump_velocity = -7
        self.health = 5
        self.is_on_ground = False
        self.direction = 'right'
        self.is_invincible = False
        self.invincibility_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.is_moving_horizontally = False

        self.animation_timer = 0
        self.current_frame = 0
        self.animation_speed = 5
        self.attack_duration = 20
        self.attack_cooldown_max = 30
        
        self.jump_buffer_frames = 8
        self.jump_buffer_timer = 0
        self.coyote_time_frames = 6
        self.coyote_timer = 0
    
    def update(self, platforms, all_enemies):
        self._handle_input()
        self._update_timers()
        self._handle_attack(all_enemies)
        self._apply_gravity_and_collisions(platforms)
        self._check_enemy_collisions(all_enemies)
        self._animate()

    def _handle_input(self):
        self.is_moving_horizontally = False
        if not self.is_attacking:
            if keyboard.left and self.left > 0:
                self.x -= self.velocity_x
                self.direction = 'left'
                self.is_moving_horizontally = True
            
            if keyboard.right and self.right < WIDTH:
                self.x += self.velocity_x
                self.direction = 'right'
                self.is_moving_horizontally = True
    
    def handle_key_down(self, key):
        if key == keys.UP:
            self.jump_buffer_timer = self.jump_buffer_frames
            if sound_on:
                sounds.sfx_jump.play()
        
        if key == keys.D and not self.is_attacking and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown = self.attack_cooldown_max
            if sound_on:
                sounds.sfx_attack.play()
    
    def _update_timers(self):
        if self.jump_buffer_timer > 0: self.jump_buffer_timer -= 1
        if self.coyote_timer > 0: self.coyote_timer -= 1
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.is_invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False

    def _handle_attack(self, all_enemies):
        if not self.is_attacking:
            return
            
        self.attack_timer -= 1
        hitbox_x = self.right if self.direction == 'right' else self.left - 24
        attack_hitbox = Rect(hitbox_x, self.top, 24, self.height)
        
        for enemy_list in all_enemies:
            for enemy in enemy_list[:]:
                if enemy.colliderect(attack_hitbox):
                    enemy_list.remove(enemy)
        
        if self.attack_timer <= 0:
            self.is_attacking = False
            
    def _apply_gravity_and_collisions(self, platforms):
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            self.velocity_y = self.jump_velocity
            self.is_on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
        
        self.y += self.velocity_y
        self.velocity_y += GRAVITY

        self.is_on_ground = False
        if self.velocity_y >= 0:
            indices = self.collidelistall(platforms)
            for platform_index in indices:
                platform = platforms[platform_index]
                if self.bottom <= platform.top + self.velocity_y:
                    self.bottom = platform.top
                    self.velocity_y = 0
                    self.is_on_ground = True
                    self.coyote_timer = self.coyote_time_frames
                    break

    def _check_enemy_collisions(self, all_enemies):
        if self.is_invincible or self.is_attacking:
            return
        
        for enemy_list in all_enemies:
            if self.collidelist(enemy_list) != -1:
                self.take_damage()
                break
    
    def take_damage(self):
        global game_over
        if not self.is_invincible:
            self.health -= 1
            self.is_invincible = True
            self.invincibility_timer = 90
            self.velocity_y = self.jump_velocity * 0.6
            if sound_on:
                sounds.sfx_hurt.play()
            if hearts:
                hearts.pop()
            if self.health <= 0:
                game_over = True
                clock.schedule_unique(quit, 5.0)
    
    def _animate(self):
        self.animation_timer += 1
        
        if self.is_attacking:
            frames = self.frames['attack_right'] if self.direction == 'right' else self.frames['attack_left']
            frame_index = (self.attack_duration - self.attack_timer) // (self.attack_duration // len(frames))
            self.image = frames[frame_index]
        elif self.is_invincible:
            frames = self.frames['hurt_right'] if self.direction == 'right' else self.frames['hurt_left']
            frame_index = self.animation_timer // 15 % len(frames)
            self.image = frames[frame_index]
        elif self.is_moving_horizontally and self.is_on_ground:
            frames = self.frames['walk_right'] if self.direction == 'right' else self.frames['walk_left']
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.image = frames[self.current_frame]
        elif self.is_on_ground:
            frames = self.frames['idle_right'] if self.direction == 'right' else self.frames['idle_left']
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.image = frames[self.current_frame]



platforms = build_tile_map("platformer_platforms.csv", TILE_SIZE)
coins = build_tile_map("platformer_coins.csv", TILE_SIZE)
backgrounds = build_tile_map("platformer_background.csv", TILE_SIZE)
diamond_map = build_tile_map("platformer_diamonds.csv", TILE_SIZE)
enemies_map_1 = build_tile_map("platformer_enemies_1.csv", TILE_SIZE)
enemies_map_2 = build_tile_map("platformer_enemies_2.csv", TILE_SIZE)


player_frames = {
    'walk_right': ["walk_right_1", "walk_right_2", "walk_right_3", "walk_right_4", "walk_right_5", "walk_right_6"],
    'walk_left': ["walk_left_1", "walk_left_2", "walk_left_3", "walk_left_4", "walk_left_5", "walk_left_6"],
    'idle_right': ["idle_right_1", "idle_right_2", "idle_right_3", "idle_right_4"],
    'idle_left': ["idle_left_1", "idle_left_2", "idle_left_3", "idle_left_4"],
    'hurt_right': ["hurt_right_1", "hurt_right_2", "hurt_right_3", "hurt_right_4"],
    'hurt_left': ["hurt_left_1", "hurt_left_2", "hurt_left_3", "hurt_left_4"],
    'attack_right': ["attack_right_1", "attack_right_2", "attack_right_3", "attack_right_4"],
    'attack_left': ["attack_left_1", "attack_left_2", "attack_left_3", "attack_left_4"]
}
enemie_1_frames = ["enemie_1_sprite_1", "enemie_1_sprite_2"]
enemie_2_frames = ["enemie_2_sprite_1", "enemie_2_sprite_2"]


player = Player("idle_right_1", pos=(100, 1000), frames=player_frames)
player.bottomleft = (0, 1000)

enemies_1 = [Enemy(enemie_1_frames[0], e.pos, 'vertical', enemie_1_frames) for e in enemies_map_1]
enemies_2 = [Enemy(enemie_2_frames[0], e.pos, 'horizontal', enemie_2_frames, speed=0.8, distance=50) for e in enemies_map_2]
all_enemy_lists = [enemies_1, enemies_2]


camera_x, camera_y = 0, 750
game_over, game_won = False, False
score = 0
game_state = 'menu'
sound_on, music_on = True, True


hearts = [Actor("tiles/tile_0042", topright=(WIDTH - 10 - (i * 37), 10)) for i in range(player.health)]
coin_ui_icon = Actor("tiles/tile_0002", topleft=(10, 10))
title_name = Actor("ui/title_name", pos=(WIDTH / 2, HEIGHT / 2 - 100))
button_start = Actor("ui/start_button", pos=(WIDTH / 2, HEIGHT / 2 - 10))
button_sound = Actor("ui/music_button", pos=(WIDTH / 2 + 210, HEIGHT / 2 + 130))
button_quit = Actor("ui/quit_button", pos=(WIDTH / 2, HEIGHT / 2 + 50))

music.play('down_under')


def on_music_end():
    if music_on:
        music.play('down_under')

def draw():
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        draw_game()

def update():
    if game_state == 'playing':
        update_game()

def on_key_down(key):
    if game_state == 'playing' and not game_over:
        player.handle_key_down(key)

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == 'menu':
        if button_start.collidepoint(pos): game_state = 'playing'
        if button_quit.collidepoint(pos): quit()
        if button_sound.collidepoint(pos):
            music_on = not music_on
            if music_on:
                button_sound.image = 'ui/music_button'
                music.unpause()
            else:
                button_sound.image = 'ui/no_music_button'
                music.pause()


def draw_game():
    screen.clear()
    

    for drawable_list in [backgrounds, platforms, coins, enemies_1, enemies_2, diamond_map]:
        for item in drawable_list:
            screen.blit(item.image, (item.left - camera_x, item.top - camera_y))
    
    if not player.is_invincible or player.animation_timer % 4 < 2:
        screen.blit(player.image, (player.left - camera_x, player.top - camera_y))


    coin_ui_icon.draw()
    screen.draw.text(f"x{score}", midleft=(coin_ui_icon.right + 6, coin_ui_icon.centery), color="white", fontsize=24, shadow=(1,1), scolor="black")
    for heart in hearts: heart.draw()

    if game_over:
        screen.draw.text("Game Over!", center=(WIDTH / 2, HEIGHT / 2), color="red", fontsize=80, shadow=(2,2), scolor="black")
        sounds.game_over.play()
    if game_won:
        screen.draw.text("You Won!", center=(WIDTH / 2, HEIGHT / 2), color="yellow", fontsize=80, shadow=(2,2), scolor="black")
        sounds.win.play()

def draw_menu():
    screen.clear()
    screen.fill("black")
    title_name.draw()
    button_start.draw()
    button_sound.draw()
    button_quit.draw()

def update_game():
    global camera_x, camera_y, score, game_over, game_won

    if game_over or game_won:
        return

    
    player.update(platforms, all_enemy_lists)
    for enemy in enemies_1: enemy.update()
    for enemy in enemies_2: enemy.update()

    
    global coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1
            if sound_on: sounds.sfx_coin.play()
            
    for diamond in diamond_map[:]:
        if player.colliderect(diamond):
            game_won = True
            clock.schedule_unique(quit, 5.0)
            break
    

    target_x = player.x - WIDTH / 2
    target_y = player.y - HEIGHT / 2
    camera_x += (target_x - camera_x) * 0.05
    camera_y += (target_y - camera_y) * 0.05

pgzrun.go()