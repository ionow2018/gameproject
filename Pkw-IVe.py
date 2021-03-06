import pygame
import os
import sys
import random


def end_screen():  # заставка в случае победы или поражения
    place, scores = load_record("pkw-stat.txt", my.total_score)
    ins = ""
    if place > 0:
        ins = "и занял " + str(place) + " место, "
    victor_text = ["VICTORY", "",
                   "Ты уничтожил " + str(my.enemies_counter) + " врагов",
                   "и успешно закончил игру,",
                   "набрав " + str(my.total_score) +
                   " очков,",
                   ins + " поздравляем!",
                   "", "Escape - возврат в меню"]
    defeat_text = ["ПОРАЖЕНИЕ", "",
                   "Ты набрал  " + str(my.total_score) + " очков " + ins + ",",
                   "уничтожив " + str(my.enemies_counter) +
                   " врагов, но они оказались сильнее.",
                   "Удачи в следующий раз.",
                   "", "Escape - возврат в меню"]
    fon = pygame.transform.scale(load_image('new_fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    if victory:
        text = victor_text
        pygame.mixer.music.load('data/ff.mp3')
        pygame.mixer.music.play()
    else:
        text = defeat_text
        pygame.mixer.music.load('data/doom.mp3')
        pygame.mixer.music.play()
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


def generate_level(level):  # генерация уровня
    x, y = -1, -1
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
    return x, y


def load_image(name, colorkey=None):  # загрузка изображения
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        image = image.convert_alpha()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        return None


def load_level(filename):  # загрузка уровня
    filename = "data/" + filename
    # Читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        #  В первой строке - счет, кол-во врагов и скорость их появления
        sc_en = level_map[0].split()
        score = int(sc_en[0])
        enemies_max = int(sc_en[1])
        spawn_hold = int(sc_en[2])
        level_map.pop(0)

        # Подсчитываем максимальную длину
        max_width = max(map(len, level_map))

        # Дополняем каждую строку пустыми клетками ('.')
        return score, enemies_max, spawn_hold,\
            list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except Exception as e:
        print(e)
        return None


def load_record(filename, new=-1):  # загрузка таблицы рекордов
    place = -1
    filename = "data/" + filename
    scores = []
    try:
        with open(filename, 'r') as mapFile:
            scores = [int(line.strip()) for line in mapFile]
        mapFile.close()
    except Exception:
        print('Cannot load record table: ', filename)
    if new > 0:
        i = -1
        for i, line in enumerate(scores):
            if new > line and place < 0:
                place = i + 1
        if i < 0:
            place = 1
            scores.append(new)
        else:
            if place < 0:
                place = i + 2
                scores.append(new)
            else:
                scores.append(new)
                scores.sort(reverse=True)
        # print(i, place, scores)
        if 0 < place < 6:
            if len(scores) == 6:
                del scores[-1]
            f = open(filename, 'w')
            for line in scores:
                f.write(str(line) + "\n")
        else:
            place = -1
    return place, scores


def load_state():  # загрузка состояния(здоровья и т.д.)
    filename = "data/pkw-save.txt"
    try:
        f = open(filename, mode="r")
        str1 = int(f.readline())
        str2 = f.readline()
        # print(str2)
        return str1, str2
    except Exception as e:
        print(e)
        return -1, ""


def printscreen():  # интерфейс с очками и здоровьем
    text = font.render("Очки", True, (0, 255, 0))
    screen.blit(text, [wt - tile_width * 2, ht])
    text = font.render(str(my.points), True, (0, 255, 0))
    w = text.get_rect()[2]
    screen.blit(text, [wt - w, ht])
    text = font.render("Здоровье", True, (0, 255, 0))
    screen.blit(text, [wt - tile_width * 2, ht + tile_width])
    text = font.render(str(my.health), True, (0, 255, 0))
    w = text.get_rect()[2]
    screen.blit(text, [wt - w, ht + tile_width])


def save_state():  # сохранение состояния
    filename = "data/pkw-save.txt"
    f = open(filename, mode="w")
    f.write(str(level_number) + "\n")
    string = str(my.x) + " " +\
        str(my.y) + " " +\
        str(my.health) + " " +\
        str(my.points) + " " +\
        str(my.enemies_counter) + " " +\
        str(my.total_score)
    f.write(string)


def start_screen():  # начальная заставка
    intro__text = ["НАЧАЛО", "",
                   "Убивай все кружки.",
                   "Движение - стрелками,",
                   "пробел - пауза.",
                   "стрельба - мышью.",
                   "F5, Ctrl-S - сохранение",
                   "F9, Ctrl-L - загрузка"]
    fon = pygame.transform.scale(load_image('new_fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    pygame.mixer.music.load('data/test.mp3')
    pygame.mixer.music.play()
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in intro__text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    x0 = 25
    x1 = 245
    x2 = 640
    y0 = 565
    Button(x0, y0)
    Button(x1, y0)
    Button(x2, y0)
    button_group.draw(screen)
    string_rendered = font.render("Начать", 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = y0 + 30
    intro_rect.x = x0 + 45
    screen.blit(string_rendered, intro_rect)
    string_rendered = font.render("Загрузить", 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = y0 + 30
    intro_rect.x = x1 + 30
    screen.blit(string_rendered, intro_rect)
    string_rendered = font.render("Выход", 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = y0 + 30
    intro_rect.x = x2 + 45
    screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.KEYDOWN:
            #     print(event.key)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
                for button in button_group:
                    button.kill()
                return True  # начинаем игру
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                for button in button_group:
                    button.kill()
                return False  # загружаем игру
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_MINUS:
                pygame.mixer.music.stop()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_PLUS:
                pygame.mixer.music.play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                xm, ym = event.pos
                if y0 < ym < y0 + 80:
                    if x0 < xm < x0 + 160:
                        for button in button_group:
                            button.kill()
                        return True  # начинаем игру
                    elif x1 < xm < x1 + 160:
                        for button in button_group:
                            button.kill()
                        return False  # загружаем игру
                    elif x2 < xm < x2 + 160:
                        pygame.quit()
                        sys.exit()
        pygame.display.flip()
        clock.tick(fps)


def terminate(nexit):  # функция выхода
    if victory or defeat:
        end_screen()
    if not nexit:
        pygame.quit()
        sys.exit()
    return True


class Tile(pygame.sprite.Sprite):  # класс тайла
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall(Tile):  # класс стены(унаследован от обычного тайла)
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.add(walls_group)
        self.x = pos_x
        self.y = pos_y


class Shooter(pygame.sprite.Sprite):  # класс стрелка и врага
    def __init__(self, x, y, image, group, health=30, health_max=30,
                 shoot=5, speed=50, limit=180, accuracy=9):
        super().__init__(group, all_sprites)
        self.id = random.randint(1, 10000000)
        self.image = image
        self.rect = self.image.get_rect()
        self.hw = self.rect[2] // 2
        self.hh = self.rect[3] // 2
        self.dx = random.randint(-100, 100) / 100
        self.dy = (1 - self.dx ** 2) ** 0.5
        if random.randint(0, 1) == 0:
            self.dy = - self.dy
        # Отодвигаем от краев:
        if x < self.hw:
            x = self.hw
            self.dx = abs(self.dx)
        elif x >= width - self.hw:
            x = width - self.hw
            self.dx = -abs(self.dx)
        if y < self.hh:
            y = self.hh
            self.dy = abs(self.dy)
        elif y >= height - self.hh:
            y = height - self.hh
            self.dy = -abs(self.dy)
        self.x = x
        self.y = y
        self.rect.centerx = x
        self.rect.centery = y
        self.health = health
        self.points = health
        self.health_max = health_max
        self.bullet = 10
        self.shoot_speed = shoot
        self.speed = speed
        self.radius = (self.hw + self.hh) // 2
        self.limit = limit
        # self.accuracy = accuracy
        # При создании на пересечении со стеной:
        if pygame.sprite.spritecollideany(self, walls_group):
            self.health = 0
            collided = True
            self.kill()

    def draw(self):
        ret = False
        if self.health <= 0:
            # Если убили - очки в зачет
            my.points += self.points
            my.total_score += self.points
            my.enemies_counter += 1
            self.kill()
            sound1.play()
            ret = True
        return ret

    def move(self):  # передвижение
        self.x += self.speed / fps * self.dx
        self.rect.centerx = self.x
        if self.x <= self.hw or self.x >= width - self.hw:
            # проверка, не соприкасается ли с краями поля
            self.dx = - self.dx
        self.y += self.speed / fps * self.dy
        self.rect.centery = self.y
        if self.y <= self.hh or self.y >= height - self.hh:
            # проверка, не соприкасается ли с краями поля
            self.dy = - self.dy
        if pygame.sprite.spritecollideany(self, walls_group):
            # проверка, не соприкасается ли со стенами
            for wall in walls_group:
                if pygame.sprite.collide_circle_ratio(0.9)(self, wall):
                    if True:
                        wx = wall.x * tile_width
                        wx1 = (wall.x + 1) * tile_width
                        wy = wall.y * tile_height
                        wy1 = (wall.y + 1) * tile_height
                        if self.dx < 0 and (wx < self.x - self.hw < wx1 and
                                            not wx < self.x < wx1):
                            self.dx = abs(self.dx)
                            self.x += self.speed / fps * self.dx
                            self.rect.centerx = self.x
                        elif self.dx > 0 and (wx < self.x + self.hw < wx1 and
                                              not wx < self.x < wx1):
                            self.dx = - abs(self.dx)
                            self.x += self.speed / fps * self.dx
                            self.rect.centerx = self.x
                        elif self.dy > 0 and (wy < self.y + self.hh < wy1 and
                                              not wy < self.y < wy1):
                            self.dy = - abs(self.dy)
                            self.y += self.speed / fps * self.dy
                            self.rect.centery = self.y
                        elif self.dy < 0 and (wy < self.y - self.hh < wy1 and
                                              not wy < self.y < wy1):
                            self.dy = abs(self.dy)
                            self.y += self.speed / fps * self.dy
                            self.rect.centery = self.y

    def shoot(self, enemy_x, enemy_y):  # стрельба
        hyp = ((self.x - enemy_x) ** 2 + (self.y - enemy_y) ** 2) ** 0.5
        if self.health > 0 and hyp < self.limit * 2.5:
            return Bullet(self.x, self.y, enemy_x, enemy_y, red_bullet_image,
                          self.limit, 5, self.id)
        else:
            return None

    def hit(self, pwr):  # если попала пуля
        self.health -= pwr


class Player(Shooter):
    # класс игрока, унаследованный от Shooter, с изменениями характеристик
    def __init__(self, x, y, image, group, health=30, health_max=30,
                 shoot=5, speed=50):
        super().__init__(x, y, image, group, health, health_max, shoot, speed)
        self.dx = 0
        self.dy = 0
        self.id = 0
        self.points = 0
        self.enemies_counter = 0
        self.total_score = 0
        self.right = True
        self.down = True

    def draw(self):
        ret = False
        if self.health <= 0:
            # pygame.mixer.music.load('data/rb.mp3')
            # pygame.mixer.music.play()
            ret = True
        return ret


class Bullet(pygame.sprite.Sprite):  # класс пули
    def __init__(self, x, y, xtarget, ytarget, image, limit=350, power=9,
                 shooter_number=0, speed=200, shooter_radius=20):
        super().__init__(all_bullets, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.radius = max(self.rect[2], self.rect[3])
        self.shooter_radius = shooter_radius
        self.shooter_number = shooter_number
        self.show = True
        self.distance = ((xtarget - x) ** 2 + (ytarget - y) ** 2) ** 0.5
        if self.distance > 0:
            self.dx = (xtarget - x) / self.distance  # определение смещения
            self.dy = (ytarget - y) / self.distance
        else:
            self.dx = 1
            self.dy = 1
            self.show = False
        self.x0 = x
        self.y0 = y
        self.x = x + (shooter_radius + self.radius) * self.dx
        self.y = y + (shooter_radius + self.radius) * self.dy
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.limit = limit
        self.power = power
        self.speed = speed
        self.ranged = False

    def draw(self):  # проверка нужна ли отрисовка
        if self.distance > self.limit:
            self.show = False
            self.kill()

    def move(self):  # смещение
        hyp = ((self.x - self.x0) ** 2 + (self.y - self.y0) ** 2) ** 0.5
        self.distance = hyp
        self.x += self.speed / fps * self.dx
        self.y += self.speed / fps * self.dy
        self.rect.centerx = self.x
        self.rect.centery = self.y
        if pygame.sprite.spritecollideany(self, walls_group):  # попала в стену
            self.show = False
            self.kill()
        if self.show:
            if pygame.sprite.spritecollideany(self, player_group):
                # если пуля попала в игрока
                if self.ranged:  # если улетела от стрелка
                    self.show = False
                    for player in player_group:
                        if pygame.sprite.collide_circle(self, player):
                            player.hit(self.power)
                    self.kill()
            else:
                if self.shooter_number == 0:
                    self.ranged = True
            if pygame.sprite.spritecollideany(self, all_enemies):
                # если пуля попала во врага
                if self.ranged:
                    self.show = False
                    for enemy in all_enemies:
                        if pygame.sprite.collide_circle(self, enemy):
                            enemy.hit(self.power)
                    self.kill()
            elif self.shooter_number != 0:
                self.ranged = True
        else:
            self.kill()


class Button(pygame.sprite.Sprite):  # класс кнопки
    def __init__(self, pos_x, pos_y):
        super().__init__(button_group)
        self.image = load_image("button.png")
        self.rect = self.image.get_rect().move(pos_x, pos_y)


pygame.init()
size = width, height = 850, 650
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 60
bullets = []
spawn_counter = 0
spawn_hold = 0
enemy_shoots = 0
enemies_max = 0
enemies = []
limits = int(height // 2 * 1.2)
tile_width = tile_height = 50

player_image = load_image('mar2.png')
enemy_image = load_image('enemy.png')
bullet_image = load_image('bullet.png')
red_bullet_image = load_image('redbullet.png')
tile_images = {'wall': load_image('walll.png'),
               'empty': load_image('floor.png')}
button_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
player_group = pygame.sprite.Group()

min_distance = 100
sound1 = pygame.mixer.Sound('data/shoot.wav')
# звук смерти противника(он есть, но из-за музыки его не слышно)
# sound2 = pygame.mixer.Sound('data/rb.mp3')
font = pygame.font.Font(None, 22)
level_name = "Pkw-level"
while True:
    start = start_screen()
    level_number = 0
    pause = False
    levels = True  # если нормально загружен уровень
    repeat = False  # если не первый уровень
    victory = False
    defeat = False
    finita = False
    while levels:  # Пока можно загружать уровни
        if repeat:  # Не первый уровень
            level_number += 1
            enemies_counter = my.enemies_counter
            total_score = my.total_score
            for sprite in all_sprites:
                sprite.kill()
            enemies = []
        else:
            enemies_counter = 0
            total_score = 0
            repeat = True
        rez = load_level(level_name + str(level_number) + ".txt")
        if rez is not None:  # Если смогли загрузить очередной уровень
            score, enemies_max, spawn_hold, level = rez
        else:
            if level_number > 0:
                victory = True
            finita = terminate(True)
            levels = False
        if not finita:
            widthN, heightN = generate_level(level)
            if widthN > 0:  # В файле нормальное описание уровня
                my = Player(width // 2, height // 2, player_image,
                            player_group, 120, 120, 5, 100)
                my.enemies_counter = enemies_counter  # Убитые враги за игру
                my.total_score = total_score          # Подсчет очков за игру
                wt = (widthN + 0.8) * tile_width      # Отступы для отображения
                ht = tile_height / 2                  # счета и здоровья
                running = True
                if not start:  # загрузка сохранённой игры из файла
                    start = True
                    level_number, sd_str = load_state()
                    if level_number >= 0:
                        for sprite in all_sprites:
                            sprite.kill()
                        enemies = []
                        args = sd_str.split()
                        x_my = float(args[0])
                        y_my = float(args[1])
                        health = int(args[2])
                        points = int(args[3])
                        enemies_counter = int(args[4])
                        total_score = int(args[5])
                        full_name = level_name + str(level_number) + ".txt"
                        rez = load_level(full_name)
                        score, enemies_max, spawn_hold, level = rez
                        widthN, heightN = generate_level(level)
                        if widthN > 0:
                            my = Player(x_my, y_my, player_image, player_group,
                                        health, 120, 5, 100)
                            my.enemies_counter = enemies_counter
                            my.total_score = total_score
                            wt = (widthN + 0.8) * tile_width
                            ht = tile_height / 2
                        my.points = points
                        my.enemies_counter = enemies_counter
                        my.total_score = total_score
                    else:
                        level_number = 0
                while running:
                    screen.fill((255, 255, 255))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            terminate(False)
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pause = False
                            x0, y0 = event.pos
                            dstn = ((x0 - my.x) ** 2 + (y0 - my.y) ** 2) ** 0.5
                            if dstn > 0:  # Щелчок не по самому себе
                                bullets.append(Bullet(my.x, my.y, x0, y0,
                                               bullet_image, limits, 20))
                        if event.type == pygame.ACTIVEEVENT:
                            if event.state == 6:  # Если свернуть игру - пауза
                                if event.gain == 0:
                                    pause = True
                                elif event.gain == 1:
                                    pause = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP:
                                my.dy = -1
                                if my.down:
                                    my.down = False
                            if event.key == pygame.K_DOWN:
                                my.dy = 1
                                if not my.down:
                                    my.down = True
                            if event.key == pygame.K_LEFT:
                                if my.right:
                                    my.image =\
                                        pygame.transform.flip(my.image, 1, 0)
                                    my.right = False
                                my.dx = -1
                            if event.key == pygame.K_RIGHT:
                                if not my.right:
                                    my.image =\
                                        pygame.transform.flip(my.image, 1, 0)
                                    my.right = True
                                my.dx = 1
                            if event.key == pygame.K_ESCAPE:  # Выход
                                terminate(False)
                            if event.key == pygame.K_KP_MINUS:
                                pygame.mixer.music.stop()
                            if event.key == pygame.K_KP_PLUS:
                                pygame.mixer.music.play()
                            if event.key == pygame.K_SPACE:
                                # Пауза / продолжение игры
                                pause = not pause
                            k_mod = pygame.key.get_mods()
                            if event.key == pygame.K_s and\
                                (k_mod == pygame.KMOD_LCTRL or
                                 k_mod == pygame.KMOD_RCTRL) or\
                                    event.key == pygame.K_F5:
                                # Сохранение состояния по F5 или Ctrl-S
                                save_state()
                            if event.key == pygame.K_l and\
                                (k_mod == pygame.KMOD_LCTRL or
                                 k_mod == pygame.KMOD_RCTRL) or\
                                    event.key == pygame.K_F9:
                                # Загрузка состояния по F9 или Ctrl-L
                                level_number, sd_str = load_state()
                                if level_number is not None:
                                    for sprite in all_sprites:
                                        sprite.kill()
                                    enemies = []
                                    args = sd_str.split()
                                    x_my = float(args[0])
                                    y_my = float(args[1])
                                    health = int(args[2])
                                    points = int(args[3])
                                    enemies_counter = int(args[4])
                                    total_score = int(args[5])
                                    full_name = level_name + str(level_number)
                                    rez = load_level(full_name + ".txt")
                                    score, enemies_max, spawn_hold, level = rez
                                    widthN, heightN = generate_level(level)
                                    if widthN > 0:
                                        my = Player(x_my, y_my, player_image,
                                                    player_group, health,
                                                    120, 5, 100)
                                        my.enemies_counter = enemies_counter
                                        my.total_score = total_score
                                        wt = (widthN + 0.8) * tile_width
                                        ht = tile_height / 2
                                    my.points = points
                                    my.enemies_counter = enemies_counter
                                    my.total_score = total_score
                        elif event.type == pygame.KEYUP:
                            if event.key == pygame.K_UP:
                                if my.dy < 0 or (my.dy > 0 and not my.down):
                                    my.dy = 0
                            if event.key == pygame.K_DOWN:
                                if my.dy > 0 or (my.dy < 0 and my.down):
                                    my.dy = 0
                            if event.key == pygame.K_LEFT:
                                if my.dx < 0 or (my.dx > 0 and not my.right):
                                    my.dx = 0
                            if event.key == pygame.K_RIGHT:
                                if my.dx > 0 or (my.dx < 0 and my.right):
                                    my.dx = 0
                    all_sprites.draw(screen)
                    if not pause:
                        my.move()
                        if my.draw():  # Уровень здоровья = 0 - поражение
                            defeat = True
                            finita = terminate(True)
                            running = False
                            levels = False
                        else:
                            if len(enemies) < enemies_max and\
                               spawn_counter % spawn_hold == 0:
                                spawn_counter = 0
                                collide = True
                                while collide:
                                    correct = False
                                    while not correct:
                                        x_enemy = random.randint(0, width)
                                        y_enemy = random.randint(0, height)
                                        # Враг возник не очень близко к игроку:
                                        hyp = ((x_enemy - my.x) ** 2 +
                                               (y_enemy - my.y) ** 2) ** 0.5
                                        if hyp >= min_distance:
                                            correct = True
                                    enemy = Shooter(x_enemy, y_enemy,
                                                    enemy_image, all_enemies)
                                    if enemy.health > 0:
                                        # Враг появляется на пустом месте
                                        collide = False
                                enemies.append(enemy)
                            for i, enemy in enumerate(enemies):
                                enemy.move()
                                if (enemy_shoots + i * 15) % 40 == 0:
                                    enemy.shoot(my.x, my.y)
                            for i in range(len(enemies) - 1, -1, -1):
                                if enemies[i].draw():
                                    enemies.pop(i)
                            for bullet in all_bullets:
                                bullet.move()
                                bullet.draw()
                            enemy_shoots += 1
                            spawn_counter += 1
                            if my.points > score:
                                my.points = 0
                                running = False
                    printscreen()
                    clock.tick(fps)
                    pygame.display.flip()
            else:
                levels = False
