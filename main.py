from constants import *
import random
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def draw_label(screen, x, y, text, font_size, color=GREEN):
    font = pygame.font.Font(None, font_size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def get_info():
    with open('data/info.txt', 'r') as file:
        lines = file.readlines()
        info = []
        for i in range(6):
            info.append(int(lines[i].strip()))
        return info


def write_info(money: int, best_score: int, ship_lvl: int, ufo_lvl: int, arrow_lvl: int, gravitator_lvl: int):
    with open('data/info.txt', 'w') as file:
        file.write(str(money) + '\n')
        file.write(str(best_score) + '\n')
        file.write(str(ship_lvl) + '\n')
        file.write(str(ufo_lvl) + '\n')
        file.write(str(arrow_lvl) + '\n')
        file.write(str(gravitator_lvl) + '\n')


class Player(pygame.sprite.Sprite):
    def __init__(self, y, level=1, lives=1, collided_obstacle=False, collided_portal=False):
        super().__init__()
        self.image = pygame.Surface([THICK, THICK])
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = y
        self.velocity = 0
        self.lives = lives
        self.collided_obstacle = collided_obstacle
        self.collided_portal = collided_portal
        self.level = level

    def update(self, high_border, lower_border, obstacles, portals):
        if pygame.sprite.collide_mask(self, high_border):
            self.rect.y = high_border.rect.y + self.rect.height
        if pygame.sprite.collide_mask(self, lower_border):
            self.rect.y = lower_border.rect.y - self.rect.height
        self.rect.y += self.velocity
        if not pygame.sprite.spritecollideany(self, obstacles) and self.collided_obstacle:
            self.collided_obstacle = False
        if not pygame.sprite.spritecollideany(self, portals) and self.collided_portal:
            self.collided_portal = False

    def collide(self, obstacles, portals, player_mods, info):
        if pygame.sprite.spritecollideany(self, obstacles) and not self.collided_obstacle:
            self.collided_obstacle = True
            self.lives -= 1
        if pygame.sprite.spritecollideany(self, portals) and not self.collided_portal:
            self.collided_portal = True
            self.lives += 1
            mods = player_mods.copy()
            mods.remove(self.__class__)
            self.__class__ = random.choice(mods)
            i = mods.index(self.__class__)
            self.__init__(self.rect.y, info[i + 2], self.lives, self.collided_obstacle, self.collided_portal)


class Ship(Player):
    def __init__(self, y, level=1, lives=1, collided_obstacle=False, collided_portal=False):
        super().__init__(y, level, lives, collided_obstacle, collided_portal)
        self.image.fill(PLAYER_COLORS[0])
        self.btn_hold = False

    def activate(self):
        self.btn_hold = True

    def deactivate(self):
        self.btn_hold = False

    def update(self, high_border, lower_border, obstacles, portals):
        if self.btn_hold and self.velocity > -15:
            self.velocity -= 0.5 * round(self.level ** 0.5, 1)
        elif not self.btn_hold and self.velocity < 15:
            self.velocity += 0.5 * round(self.level ** 0.5, 1)
        super().update(high_border, lower_border, obstacles, portals)
        if pygame.sprite.collide_mask(self, high_border):
            self.velocity = 0
        if pygame.sprite.collide_mask(self, lower_border):
            self.velocity = 0


class UFO(Player):
    def __init__(self, y, level=1, lives=1, collided_obstacle=False, collided_portal=False):
        super().__init__(y, level, lives, collided_obstacle, collided_portal)
        self.image.fill(PLAYER_COLORS[1])

    def update(self, high_border, lower_border, obstacles, portals):
        super().update(high_border, lower_border, obstacles, portals)
        if self.velocity < 15:
            self.velocity += 0.5 * round(self.level ** 0.5, 1)
        if pygame.sprite.collide_mask(self, high_border):
            self.velocity = 0
        if pygame.sprite.collide_mask(self, lower_border):
            self.velocity = 0

    def activate(self):
        self.velocity = -10 * round(self.level ** 0.5, 1)

    def deactivate(self):
        pass


class Arrow(Player):
    def __init__(self, y, level=1, lives=1, collided_obstacle=False, collided_portal=False):
        super().__init__(y, level, lives, collided_obstacle, collided_portal)
        self.image.fill(PLAYER_COLORS[2])
        self.velocity = 8 * round(self.level ** 0.5, 1)

    def activate(self):
        self.velocity = -8 * round(self.level ** 0.5, 1)

    def deactivate(self):
        self.velocity = 8 * round(self.level ** 0.5, 1)

    def update(self, high_border, lower_border, obstacles, portals):
        super().update(high_border, lower_border, obstacles, portals)
        if pygame.sprite.collide_mask(self, high_border):
            self.velocity = 0
        if pygame.sprite.collide_mask(self, lower_border):
            self.velocity = 0


class Gravitator(Player):
    def __init__(self, y, level=1, lives=1, collided_obstacle=False, collided_portal=False):
        super().__init__(y, level, lives, collided_obstacle, collided_portal)
        self.image.fill(PLAYER_COLORS[3])
        self.acceleration = 0.5 * round(self.level ** 0.5, 1)

    def activate(self):
        self.acceleration = -self.acceleration

    def deactivate(self):
        pass

    def update(self, high_border, lower_border, obstacles, portals):
        super().update(high_border, lower_border, obstacles, portals)
        if pygame.sprite.collide_mask(self, high_border):
            self.velocity = 0
        if pygame.sprite.collide_mask(self, lower_border):
            self.velocity = 0
        self.velocity += self.acceleration


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        form = random.choice(FORMS)
        self.image = pygame.Surface(form)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(THICK, HEIGHT - form[1]) // 60 * 60

    def update(self, velocity):
        self.rect.x -= velocity


class Portal(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.image = pygame.Surface((10, 120))
        self.image.fill(PINK)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = y

    def update(self, velocity):
        self.rect.x -= velocity


class Border(pygame.sprite.Sprite):
    def __init__(self, high=True):
        super().__init__()
        self.image = pygame.Surface((WIDTH, THICK))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        if high:
            self.rect.y = 0
        else:
            self.rect.y = HEIGHT - THICK


class Coin(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.image = load_image('coin.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH
        self.rect.y = y
        self.grabbed = False
        self.k = 0

    def update(self, velocity, players):
        if pygame.sprite.spritecollideany(self, players):
            self.grabbed = True
        self.rect.x -= velocity
        if self.grabbed:
            self.rect.y -= 10
            self.rect.x += velocity + 5
            self.image.set_alpha(255 - self.k)
            self.k += 10


class Button:
    def __init__(self, text, x, y, color=WHITE, second_color=RED):
        super().__init__()
        self.font = pygame.font.Font(None, 70)
        self.text = text
        self.color = color
        self.second_color = second_color
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.rect.x = x
        self.rect.y = y

    # чтоб когда наводились горела красным
    def pointed(self, pos):
        if (self.rect.x <= pos[0] <= self.rect.x + self.rect.width and
                self.rect.y <= pos[1] <= self.rect.y + self.rect.height):
            self.rendered_text = self.font.render(self.text, True, self.second_color)
        else:
            self.rendered_text = self.font.render(self.text, True, self.color)

    def clicked(self, pos):
        if (self.rect.x <= pos[0] <= self.rect.x + self.rect.width and
                self.rect.y <= pos[1] <= self.rect.y + self.rect.height):
            return True
        else:
            return False

    def draw(self, screen):
        screen.blit(self.rendered_text, (self.rect.x, self.rect.y))


def menu():
    # добавление необходимых переменных
    info = get_info()
    upgrade_buttons = []
    running = True

    # первоначальная настройка
    pygame.init()
    pygame.mouse.set_visible(True)
    pygame.display.set_caption("Game menu")
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    clock = pygame.time.Clock()

    # добавление фона и кнопки плей
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    play_button = Button('play', WIDTH / 2 - 45, HEIGHT - 100, GREEN)

    # добавление кнопок улучшения
    for i in range(4):
        level = info[i + 2]
        if level <= 3:
            upgrade_button = Button('upgrade', i * 425 + 160, 625)
            upgrade_buttons.append(upgrade_button)

    # основной цикл игры
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                write_info(*info)
                running = False
            if event.type == pygame.MOUSEMOTION:
                play_button.pointed(event.pos)
                for button in upgrade_buttons:
                    button.pointed(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.clicked(event.pos):
                    game()
                for button in upgrade_buttons:
                    if button.clicked(event.pos):
                        i = upgrade_buttons.index(button)
                        if info[0] >= info[i + 2] ** 2 * 50 and info[i + 2] <= 3:
                            info[0] -= info[i + 2] ** 2 * 50
                            info[i + 2] += 1
                            write_info(*info)
        # обновление
        pygame.display.update()

        # отрисовка всего меню
        screen.blit(fon, (0, 0))

        for i in range(4):
            level = info[i + 2]
            pygame.draw.rect(screen, GREEN, ((i * 425 + 55, 100), (400, 600)), 5)
            pygame.draw.rect(screen, PLAYER_COLORS[i], ((i * 425 + 165, 200), (180, 180)))
            draw_label(screen, i * 425 + 155, 400, f'level: {level} / 4', 60)
            if level <= 3:
                draw_label(screen, i * 425 + 100, 575, f'upgrade price: {level ** 2 * 50}', 50, WHITE)
            else:
                draw_label(screen, i * 425 + 200, 575, 'MAX', 70, WHITE)

        draw_label(screen, (WIDTH - 400) / 2, 10, 'CUBEPACK JOYRIDE', 60, WHITE)
        draw_label(screen, 10, 10, f'MONEY: {info[0]}', 60, WHITE)
        draw_label(screen, WIDTH - 300, 10, f'BEST: {info[1]}', 60, WHITE)
        play_button.draw(screen)
        for i in range(len(upgrade_buttons)):
            if info[i + 2] <= 3:
                upgrade_buttons[i].draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # выход
    pygame.quit()
    sys.exit()


def game():
    # добавление необходимых переменных
    info = get_info()
    player_mods = [Ship, UFO, Arrow, Gravitator]
    list_of_obstacles = []
    velocity = VELOCITY
    score = 0
    is_coin_taken = False
    paused = False
    running = True

    # первоначальная настройка
    pygame.init()
    pygame.display.set_caption("Cubepack joyride")
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    clock = pygame.time.Clock()

    obstacles = pygame.sprite.Group()
    portals = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    players = pygame.sprite.Group()
    borders = pygame.sprite.Group()

    resume_button = Button('RESUME', WIDTH / 2 - 125, HEIGHT / 2, GREEN)
    menu_button = Button('MENU', WIDTH / 2 - 95, HEIGHT / 2 - 100, GREEN)

    # функция для рендера игры
    def render():
        screen.fill(BLACK)
        screen.blit(player.image, player.rect)
        obstacles.draw(screen)
        borders.draw(screen)
        portals.draw(screen)
        coins.draw(screen)
        draw_label(screen, WIDTH - 220, 0, f'score: {score}', 50)
        draw_label(screen, 30, 10, f'lives: {player.lives}', 50)
        draw_label(screen, WIDTH - 220, 40, f'best: {info[1]}', 30)
        draw_label(screen, 800, 10, f'money: {info[0]}', 50)

    # добавление игрока
    player = Ship(HEIGHT - THICK * 2, info[2])
    players.add(player)

    # добавление границ
    high_border = Border(True)
    borders.add(high_border)
    lower_border = Border(False)
    borders.add(lower_border)

    # добавление 1-го препятствия
    first_obstacle = Obstacle()
    list_of_obstacles.append(first_obstacle)
    obstacles.add(first_obstacle)

    # основной цикл игры
    while running:
        if paused:
            # сделать курсор видимым
            pygame.mouse.set_visible(True)

            # проверка ивентов
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:
                    resume_button.pointed(event.pos)
                    menu_button.pointed(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_button.clicked(event.pos):
                        write_info(*info)
                        menu()
                    if resume_button.clicked(event.pos):
                        paused = False
            # отрисовка
            render()
            resume_button.draw(screen)
            menu_button.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

        else:
            # проверка жив ли игрок
            if player.lives == 0:
                write_info(*info)
                menu()

            # проверка ивентов
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.activate()
                if event.type == pygame.MOUSEBUTTONUP:
                    player.deactivate()

            # сделать курсор видимым
            pygame.mouse.set_visible(False)

            # проверка столкновений игрока
            player.collide(obstacles, portals, player_mods, info)

            # спавн препятствий
            last_obstacle = list_of_obstacles[len(list_of_obstacles) - 1]
            if last_obstacle.rect.x < WIDTH - random.choice(SPACES):
                obstacle = Obstacle()
                list_of_obstacles.append(obstacle)
                obstacles.add(obstacle)

            # спавн порталов
            if len(obstacles) / (len(portals) + 1) == FREQUENCY_OF_PORTALS:
                y = random.randint(THICK, HEIGHT - 3 * THICK) // THICK * THICK
                portal = Portal(y)
                portal.rect.x += 10 * THICK
                portals.add(portal)

            # спавн монет
            if (len(obstacles) / (len(coins) + len(portals) + 1) == FREQUENCY_OF_COINS and len(obstacles) %
                    FREQUENCY_OF_PORTALS != 0):
                y = random.randint(THICK, HEIGHT - 2 * THICK) // THICK * THICK
                coin = Coin(y)
                coin.rect.x += 10 * THICK
                coins.add(coin)
                is_coin_taken = False

            # обновление игры
            obstacles.update(velocity)
            portals.update(velocity)
            coins.update(velocity, players)
            player.update(high_border, lower_border, obstacles, portals)
            velocity += ACCELERATION
            score = (-first_obstacle.rect.x + WIDTH) // 100
            if pygame.sprite.spritecollideany(player, coins) and not is_coin_taken:
                is_coin_taken = True
                info[0] += 1
            if info[1] < score:
                info[1] = score

            # отрисовка
            render()

            pygame.display.flip()
            clock.tick(FPS)

    # выход
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    menu()
