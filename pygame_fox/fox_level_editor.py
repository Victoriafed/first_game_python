import pygame
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()

tile_size = 50
cols = 20
rw = 14

screen_width = tile_size * cols
screen_height = (tile_size * rw)

display = pygame.display.set_mode((screen_width, screen_height + 100))
pygame.display.set_caption('Level Editor')

bear_img = pygame.image.load('images/bear_gun.png').convert_alpha()
bg_img = pygame.image.load('images/background.jpg')
bs_img = pygame.image.load('images/blacksquare.png').convert_alpha()
crown_img = pygame.image.load('images/crownfull.png').convert_alpha()
exit_img = pygame.image.load('images/exit.png')
fox_crown_img = pygame.image.load('images/player_fox2.png').convert_alpha()
load_img = pygame.image.load('images/load.png')
log_img = pygame.image.load('images/log.png').convert_alpha()
save_img = pygame.image.load('images/save.png')
exit_level_img = pygame.image.load('images/door.png')

clicked = False
level = 1

font = pygame.font.SysFont('Futura', 30)

world_data = []
for row in range(14):
    r = [0] * 20
    world_data.append(r)

for tile in range(0, 20):
    world_data[0][tile] = 1
    world_data[13][tile] = 1
for tile in range(0, 14):
    world_data[tile][0] = 1
    world_data[tile][19] = 1


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    display.blit(img, (x, y))


def draw_grid():
    for x in range(21):
        pygame.draw.line(display, (255, 255, 255), (x * tile_size, 0),
                         (x * tile_size, screen_height))
    for y in range(14):
        pygame.draw.line(display, (255, 255, 255), (0, y * tile_size),
                         (screen_width, y * tile_size))


def draw_world():
    for row in range(14):
        for col in range(20):
            if world_data[row][col] > 0:
                if world_data[row][col] == 1:
                    img = pygame.transform.scale(bs_img,
                                                 (tile_size, tile_size))
                    display.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 2:
                    img = pygame.transform.scale(log_img, ((215, 40)))
                    display.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 3:
                    img = pygame.transform.scale(bear_img, (140, 140))
                    display.blit(img,
                                 (col * tile_size - 30, row * tile_size - 75))
                if world_data[row][col] == 4:
                    img = pygame.transform.scale(exit_level_img,
                                                 (tile_size, tile_size))
                    display.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 5:
                    img = pygame.transform.scale(crown_img, (
                    tile_size * 0.8, tile_size * 0.8))
                    display.blit(img, (col * tile_size + tile_size // 7,
                                       row * tile_size + tile_size // 4))
                if world_data[row][col] == 6:
                    img = pygame.transform.scale(log_img,
                                                 (tile_size * 2, tile_size))
                    display.blit(img, (col * tile_size, row * tile_size))
                if world_data[row][col] == 7:
                    img = pygame.transform.scale(log_img,
                                                 (tile_size * 2, tile_size))
                    display.blit(img, (col * tile_size, row * tile_size))


class Button():
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (175, 80))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        display.blit(self.image, (self.rect.x, self.rect.y))
        return action


save_button = Button(400, 705, save_img)
load_button = Button(600, 705, load_img)
exit_button = Button(800, 705, exit_img)

done = False
while not done:
    clock.tick(60)

    display.blit(bg_img, (0, 0))

    if exit_button.draw():
        done = True
    if save_button.draw():
        pickle_out = open(f'levels/level{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
        print('уровень сохранен')
    if load_button.draw():
        if path.exists(f'levels/level{level}_data'):
            pickle_in = open(f'levels/level{level}_data', 'rb')
            world_data = pickle.load(pickle_in)
        print('уровень загружен')

    draw_grid()
    draw_world()

    pygame.draw.rect(display, (0, 0, 0),
                     pygame.Rect(tile_size // 2, 710, 350, 50))
    draw_text(f'Level: {level}', font, (255, 255, 255), tile_size * 2, 710)
    draw_text('Press UP or DOWN to change level', font, (255, 255, 255),
              tile_size // 2,
              740)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
            pos = pygame.mouse.get_pos()
            x = pos[0] // tile_size
            y = pos[1] // tile_size
            if x < 20 and y < 14:
                if pygame.mouse.get_pressed()[0] == 1:
                    world_data[y][x] += 1
                    if world_data[y][x] > 7:
                        world_data[y][x] = 0
                    print(world_data[y][x])
                elif pygame.mouse.get_pressed()[2] == 1:
                    world_data[y][x] -= 1
                    if world_data[y][x] < 0:
                        world_data[y][x] = 7
                    print(world_data[y][x])
        if event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            elif event.key == pygame.K_DOWN and level > 1:
                level -= 1
    pygame.display.update()
pygame.quit()
