import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()

tile_size = 50
down = 526
screen_width = 1000
screen_height = 700
game_over = 0
level = 1
main_menu = True
done = False
max_levels = 10
score = 0

display = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('Fox game')


font_score = pygame.font.SysFont('Bauhaus 93', 30)
white = (255, 255, 255)
blue = (0, 0, 255)

# можно улчучшить загрузку изображений
bg_img = pygame.image.load('images/background.jpg')
bs_img = pygame.image.load('images/blacksquare.png').convert_alpha()
crow_bg_img = pygame.image.load('images/crow_bg.png')
crown_img = pygame.image.load('images/crownfull.png').convert_alpha()
fox_img = pygame.image.load('images/player_fox.png').convert_alpha()
fox_crown_img = pygame.image.load('images/player_fox2.png').convert_alpha()
fox_jump_img = pygame.image.load('images/player_fox3.png').convert_alpha()
bear_img = pygame.image.load('images/bear_gun.png').convert_alpha()
dead_img = pygame.image.load('images/gameover.jpg').convert_alpha()
log_img = pygame.image.load('images/log.png').convert_alpha()
restart_img = pygame.image.load('images/restart.png')
start_img = pygame.image.load('images/start.png')
exit_img = pygame.image.load('images/exit.png')
exit_level_img = pygame.image.load('images/door.png')

pygame.mixer.music.load('sounds/bg_music.mp3')
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1, 0.0, 5000)
crown_fx = pygame.mixer.Sound('sounds/crown.wav')
crown_fx.set_volume(0.5)
dead_fx = pygame.mixer.Sound('sounds/dead.wav')
dead_fx.set_volume(0.3)

class Button():
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (175, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        display.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        step = 5
        dx, dy = 0, 0
        col_thresh = 20

        if game_over == 0:
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE] and self.jumped == False:
                self.boost = -15
                self.jumped = True
                if self.direction == -1:
                    self.image = self.image_jump_left
                else:
                    self.image = self.image_jump_right
            if not pressed[pygame.K_SPACE]:
                self.jumped = False
                if self.direction == -1:
                    self.image = self.image_left
                else:
                    self.image = self.image_right
            if pressed[pygame.K_LEFT]:
                dx -= step
                self.direction = -1
                self.image = self.image_left
            if pressed[pygame.K_RIGHT]:
                dx += step
                self.direction = 1
                self.image = self.image_right

            if self.direction == 1 and not self.jumped:
                self.image = self.image_right

            self.boost += 1
            if self.boost > 10:
                self.boost = 10
            dy += self.boost

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(
                        self.rect.x + dx, self.rect.y, self.width, self.height
                ):
                    dx = 0
                if tile[1].colliderect(
                        self.rect.x, self.rect.y + dy, self.width, self.height
                ):
                    if self.boost < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.boost = 0
                    elif self.boost >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.boost = 0
                        self.in_air = False

            if self.rect.y + dy + self.height > down:
                dy = down - self.rect.y - self.height

            if pygame.sprite.spritecollide(self, bear_group, False):
                game_over = -1
                dead_fx.play()
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y,
                                             self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy,
                                             self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

        self.rect.x += dx
        self.rect.y += dy

        display.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.image_crown = pygame.transform.scale(fox_crown_img, (80, 95))
        self.dead_image = pygame.transform.scale(dead_img, (500, 500))
        self.image_left = pygame.transform.scale(fox_img, (60, 75))
        self.image_right = pygame.transform.flip(self.image_left, True,
                                                 False)
        self.image_jump_left = pygame.transform.scale(fox_jump_img,
                                                      (80, 95))
        self.image_jump_right = pygame.transform.flip(self.image_jump_left,
                                                      True, False)
        self.image = self.image_right
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.boost = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []
        self.line = pygame.draw.line(display, (255, 255, 255), (0, 525),
                                     (1000, 525), 2)

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(bs_img,
                                                 (50, 50))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(log_img,
                                                 (215, 40))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    bear = Enemy(col_count * tile_size + 15,
                                 row_count * tile_size - 75)
                    bear_group.add(bear)
                if tile == 4:
                    exit = Exit(col_count * tile_size, row_count * tile_size - 35)
                    exit_group.add(exit)
                if tile == 5:
                    crown = Crown((col_count * tile_size + tile_size // 4), row_count * tile_size + tile_size //  2)
                    crown_group.add(crown)
                if tile == 6:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 7:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            display.blit(tile[0], tile[1])

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(log_img, (100, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Crown(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(crown_img,
                                            (tile_size * 0.8, tile_size * 0.8))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bear_img, (140, 140))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.image = pygame.transform.scale(exit_level_img, (
            60, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, down)
bear_group = pygame.sprite.Group()
crown_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

if path.exists(f'levels/level{level}_data'):
    pickle_in = open(f'levels/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


def reset_level(level):
    player.reset(100, screen_height - 130)
    bear_group.empty()
    exit_group.empty()
    platform_group.empty()
    if path.exists(f'levels/level{level}_data'):
        pickle_in = open(f'levels/level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    display.blit(img, (x, y))


start_button = Button(screen_width // 2 - 88, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 - 88, screen_height // 2 + 77, exit_img)
restart_button = Button(screen_width // 2 - 88, screen_height // 2,
                        restart_img)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            if event.key == pygame.K_RETURN:
                main_menu = False

    clock.tick(60)

    game_over = player.update(game_over)

    if main_menu:
        display.blit(crow_bg_img, (0, 0))
        if exit_button.draw():
            done = True
        if start_button.draw():
            main_menu = False
    else:
        display.blit(bg_img, (0, 0))
        world.draw()
        game_over = player.update(game_over)

        if game_over == 0:
            bear_group.update()
            bear_group.draw(display)
            exit_group.draw(display)
            crown_group.draw(display)
            platform_group.update()
            platform_group.draw(display)
            if pygame.sprite.spritecollide(player, crown_group, True):
                score += 1
                crown_fx.play()
            img = pygame.transform.scale(crown_img, (30, 30))
            display.blit(img, (52, 50))
            draw_text('x'+ str(score), font_score, white, 85, 60)

        if game_over == -1:
            display.fill((0, 0, 0))
            draw_text('GAME OVER', pygame.font.SysFont('Bauhaus 93', 100), (215, 125, 49), screen_width // 2 - 220, 230)
            draw_text(f'Your score: {score}', pygame.font.SysFont('Bauhaus 93', 50),
                      (80, 125, 42), screen_width // 2 - 100, 300)
            if exit_button.draw():
                done = True
            if restart_button.draw():
                player.reset(100, screen_height - 130)
                game_over = 0
                score = 0

        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                game_over = 2

        if game_over == 2:
            display.fill((0, 0, 0))
            draw_text(f'You WINN!',
                      pygame.font.SysFont('Bauhaus 93', 100),
                      (255, 69, 0), screen_width // 2 - 100, 200)
            draw_text(f'Your score: {score}',
                      pygame.font.SysFont('Bauhaus 93', 50),
                      (80, 125, 42), screen_width // 2 - 100, 300)
            if exit_button.draw():
                done = True

    pygame.display.update()

pygame.quit()
