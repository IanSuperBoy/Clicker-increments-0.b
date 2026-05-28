import pygame
import sys
import math
import os

# Инициализация Pygame
pygame.init()

# Попытка импортировать звук (если не установлен pygame.mixer, будет работать без звука)
try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False

# Константы
WIDTH, HEIGHT = 1200, 700
BACKGROUND_COLOR = (30, 30, 40)
CIRCLE_COLOR = (200, 100, 200)
CIRCLE_HOVER_COLOR = (225, 125, 225)
TEXT_COLOR = (255, 255, 255)
CIRCLE_RADIUS = 120
FPS = 60
AVAILABLE_FPS = [6, 8, 12, 20, 30, 40, 60, 90, 120, 144, 180, 240, 300, 400, 560, 720]

# Константы улучшений
UPGRADE_BTN_WIDTH = 200
UPGRADE_BTN_HEIGHT = 70
UPGRADES = {
    'click': {
        'name': 'Усиление клика',
        'base_cost': 10,
        'cost_multiplier': 1.8,
        'effect': 1.5,  # добавляет +1 к множителю клика
        'level': 0,
        'description': '+1 к множителю клика'
    },
    'auto': {
        'name': 'Автокликер',
        'base_cost': 40,
        'cost_multiplier': 2,
        'effect': 1,  # добавляет +1 очко в секунду
        'level': 0,
        'description': '+1 очко в секунду'
    },
    'exp': {
        'name': 'Exponent',
        'base_cost': 1000,
        'cost_multiplier': 1,
        'effect': 0.05,  # добавляет +1 очко в секунду
        'level': 0,
        'description': '+1 очко в секунду'
    }
}

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker increments 0.α")
clock = pygame.time.Clock()

# Шрифты
main_font = pygame.font.Font(None, 74)
big_font = pygame.font.Font(None, 48)
medium_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Переменные игры
click_count = 0
click_multiplier = 1
click_exponent = 1
auto_income = 0
last_auto_time = pygame.time.get_ticks()
sound_enabled = True
fps_index = AVAILABLE_FPS.index(FPS)


# Загрузка звуковых файлов
def load_sound(file_path):
    """Загружает звуковой файл, если он существует"""
    try:
        if os.path.exists(file_path):
            return pygame.mixer.Sound(file_path)
        else:
            print(f"Файл не найден: {file_path}")
            return None
    except:
        print(f"Ошибка загрузки звука: {file_path}")
        return None


# Укажите пути к вашим MP3 файлам
SOUND_CLICK = load_sound("click.mp3")  # Звук клика
SOUND_UPGRADE = load_sound("upgrade.mp3")  # Звук улучшения

# Звуковые эффекты с использованием MP3 файлов
def play_click_sound():
    if not sound_enabled:
        return

    if SOUND_CLICK:
        try:
            SOUND_CLICK.play()
        except:
            pass
    else:
        # Альтернатива: если файл не загружен, используем простой звук через pygame
        try:
            sample_rate = 44100
            duration = 0.1
            frequency = 440
            samples = int(sample_rate * duration)
            waves = []
            for i in range(samples):
                value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                waves.append([value, value])
            sound = pygame.sndarray.make_sound(waves)
            sound.play()
        except:
            pass


def play_upgrade_sound():
    if not sound_enabled:
        return

    if SOUND_UPGRADE:
        try:
            SOUND_UPGRADE.play()
        except:
            pass
    else:
        # Альтернатива: если файл не загружен, используем простой звук через pygame
        try:
            sample_rate = 44100
            duration = 0.2
            frequency = 880
            samples = int(sample_rate * duration)
            waves = []
            for i in range(samples):
                value = int(32767 * 0.4 * math.sin(2 * math.pi * frequency * i / sample_rate))
                waves.append([value, value])
            sound = pygame.sndarray.make_sound(waves)
            sound.play()
        except:
            pass


# Функции для улучшений
def get_upgrade_cost(upgrade_type):
    """Возвращает текущую стоимость улучшения"""
    upgrade = UPGRADES[upgrade_type]
    if upgrade_type == "exp":
        return 1000000 ** ((((click_exponent ** 1.5) * 3.5) - 2) / 3)
    else:
        return int(upgrade['base_cost'] * (upgrade['cost_multiplier'] ** upgrade['level']))


def buy_upgrade(upgrade_type):
    """Покупка улучшения"""
    global click_count, click_multiplier, auto_income, click_exponent

    upgrade = UPGRADES[upgrade_type]
    cost = get_upgrade_cost(upgrade_type)

    if click_count >= cost:
        click_count -= cost
        upgrade['level'] += 1

        if upgrade_type == 'click':
            click_multiplier *= upgrade['effect']
        elif upgrade_type == 'auto':
            auto_income += upgrade['effect']
        elif upgrade_type == 'exp':
            click_exponent += upgrade['effect']

        play_upgrade_sound()
        return True
    return False


def get_auto_income():
    """Возвращает доход от автокликера в секунду"""
    return auto_income


def update_auto_income():
    """Обновляет доход от автокликера"""
    global click_count, last_auto_time

    current_time = pygame.time.get_ticks()
    time_passed = current_time - last_auto_time

    if time_passed >= 1000 / FPS:  # Каждую секунду
        frames = time_passed // (1000 / FPS)
        click_count += (click_multiplier * frames * auto_income) ** click_exponent / FPS
        last_auto_time = current_time


# Кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color

    def draw(self, screen, font, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)

        # Отрисовка текста с переносом строк
        lines = self.text.split('\n')
        y_offset = self.rect.centery - (len(lines) - 1) * 12
        for line in lines:
            text_surface = font.render(line, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 25

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# Создание кнопок
circle_x = WIDTH // 2
circle_y = HEIGHT // 2 - 50

# Кнопки улучшений
click_upgrade_btn = Button(
    20, 20, UPGRADE_BTN_WIDTH, UPGRADE_BTN_HEIGHT,
    "Усиление клика\nУровень 0",
    (100, 100, 100), (120, 120, 120)
)

auto_upgrade_btn = Button(
    20, 100, UPGRADE_BTN_WIDTH, UPGRADE_BTN_HEIGHT,
    "Автокликер\nУровень 0",
    (100, 100, 100), (120, 120, 120)
)

exp_upgrade_btn = Button(
    20, 180, UPGRADE_BTN_WIDTH, UPGRADE_BTN_HEIGHT,
    "Автокликер\nУровень 0",
    (100, 100, 100), (120, 120, 120)
)

# Кнопка звука
sound_btn = Button(
    WIDTH - 120, 20, 100, 50,
    "Sound: ON",
    (70, 130, 70), (90, 150, 90)
)

fps_btn = Button(
    WIDTH - 120, 80, 100, 50,
    "Change FPS",
    (130, 70, 130), (150, 90, 150)
)


def draw_circle(mouse_pos):
    """Рисует круг с простым градиентом через несколько слоев"""
    distance = ((mouse_pos[0] - circle_x) ** 2 + (mouse_pos[1] - circle_y) ** 2) ** 0.5
    is_hover = distance < CIRCLE_RADIUS

    # Выбираем цвета в зависимости от наведения
    if is_hover:
        outer_color = CIRCLE_HOVER_COLOR
        inner_color = (200, 90, 200)
        glow_color = (200, 110, 200)
    else:
        outer_color = CIRCLE_COLOR
        inner_color = (180, 90, 180)
        glow_color = (200, 80, 200)

    # Рисуем внешнее свечение
    for i in range(5, 0, -1):
        alpha = 50 // i
        glow_surface = pygame.Surface((CIRCLE_RADIUS * 2 + i * 2, CIRCLE_RADIUS * 2 + i * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color, alpha),
                           (CIRCLE_RADIUS + i, CIRCLE_RADIUS + i), CIRCLE_RADIUS + i)
        screen.blit(glow_surface, (circle_x - CIRCLE_RADIUS - i, circle_y - CIRCLE_RADIUS - i))

    # Рисуем основной круг
    pygame.draw.circle(screen, outer_color, (circle_x, circle_y), CIRCLE_RADIUS)

    # Рисуем внутренний круг (градиентный эффект)
    pygame.draw.circle(screen, inner_color, (circle_x, circle_y), CIRCLE_RADIUS - 20)

    # Рисуем центральный блик
    if is_hover:
        center_bright = (200, 60, 200)
    else:
        center_bright = (170, 60, 170)
    pygame.draw.circle(screen, center_bright, (circle_x, circle_y), CIRCLE_RADIUS - 50)

    # Рисуем обводку
    pygame.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), CIRCLE_RADIUS, 3)


def draw_stats():
    """Рисует статистику"""
    # Счетчик кликов
    text = main_font.render(str(math.floor(click_count)) + "$", True, TEXT_COLOR)
    text_rect = text.get_rect(center=(circle_x, circle_y - 200))
    screen.blit(text, text_rect)

    # Информация о множителе клика
    SCM = math.floor(click_multiplier * 1000) / 1000
    click_info = medium_font.render(f"Multiplier: x{SCM}", True, (255, 100, 100))
    screen.blit(click_info, (circle_x - click_info.get_width() // 2, circle_y + CIRCLE_RADIUS + 10))

    # Информация об автокликере
    if auto_income > 0:
        auto_info = medium_font.render(f"{auto_income} clicks/sec", True, (100, 100, 255))
        screen.blit(auto_info, (circle_x - auto_info.get_width() // 2, circle_y + CIRCLE_RADIUS + 35))

    if click_exponent > 1:
        exp_info = medium_font.render(f"$ gain raised by {click_exponent}", True, (230, 50, 230))
        screen.blit(exp_info, (circle_x - exp_info.get_width() // 2, circle_y + CIRCLE_RADIUS + 60))

    # Подсказка
    hint = small_font.render("Hotkeys: ESC - Exit, F - Change FPS", True, TEXT_COLOR)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

    hint2 = small_font.render(f"FPS: {FPS}", True, TEXT_COLOR)
    screen.blit(hint2, (circle_x - hint2.get_width() // 2, circle_y + CIRCLE_RADIUS + 230))


def update_upgrade_buttons():
    """Обновляет текст и цвет кнопок улучшений"""
    click_upgrade = UPGRADES['click']
    auto_upgrade = UPGRADES['auto']
    exp_upgrade = UPGRADES["exp"]

    click_cost = get_upgrade_cost('click')
    auto_cost = get_upgrade_cost('auto')
    exp_cost = get_upgrade_cost('exp')

    # Кнопка усиления клика
    click_upgrade_btn.text = f"*1.5 multiplier\nLevel {click_upgrade['level']} | {click_cost}$"
    if click_count >= click_cost:
        click_upgrade_btn.color = (50, 150, 50)
        click_upgrade_btn.hover_color = (70, 170, 70)
    else:
        click_upgrade_btn.color = (240, 100, 100)
        click_upgrade_btn.hover_color = (240, 120, 120)

    # Кнопка автокликера
    auto_upgrade_btn.text = f"+1 clicks/sec\nLevel {auto_upgrade['level']} | {auto_cost}$"
    if click_count >= auto_cost:
        auto_upgrade_btn.color = (50, 150, 50)
        auto_upgrade_btn.hover_color = (70, 170, 70)
    else:
        auto_upgrade_btn.color = (240, 100, 100)
        auto_upgrade_btn.hover_color = (240, 120, 120)

    exp_upgrade_btn.text = f"+^0.05 exponent\nLevel {exp_upgrade['level']} | {math.floor(exp_cost)}$"
    if click_count >= exp_cost:
        exp_upgrade_btn.color = (50, 150, 50)
        exp_upgrade_btn.hover_color = (70, 170, 70)
    else:
        exp_upgrade_btn.color = (240, 100, 100)
        exp_upgrade_btn.hover_color = (240, 120, 120)

    # Кнопка звука
    sound_btn.text = f"Sound: {'ON' if sound_enabled else 'OFF'}"
    if sound_enabled:
        sound_btn.color = (70, 130, 70)
        sound_btn.hover_color = (90, 150, 90)
    else:
        sound_btn.color = (130, 70, 70)
        sound_btn.hover_color = (150, 90, 90)


def check_click(mouse_pos):
    """Проверяет клик по кругу"""
    global click_count
    distance = ((mouse_pos[0] - circle_x) ** 2 + (mouse_pos[1] - circle_y) ** 2) ** 0.5
    if distance < CIRCLE_RADIUS:
        click_count += click_multiplier ** click_exponent
        play_click_sound()
        return True
    return False


def draw_floating_text():
    """Отрисовывает эффект всплывающего текста (упрощенная версия)"""
    # В реальной игре здесь можно добавить анимацию
    pass


# Главный игровой цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # Обновление автокликера
    update_auto_income()

    # Обновление кнопок
    update_upgrade_buttons()

    def change_fps():
        """Изменяет FPS на следующее значение в списке"""
        global FPS, fps_index, clock
        fps_index = (fps_index + 1) % len(AVAILABLE_FPS)
        FPS = AVAILABLE_FPS[fps_index]
        # Пересоздаем clock для применения новых FPS
        clock = pygame.time.Clock()
        play_click_sound()  # Звук для обратной связи
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if click_upgrade_btn.is_clicked(mouse_pos):
                    buy_upgrade('click')
                elif auto_upgrade_btn.is_clicked(mouse_pos):
                    buy_upgrade('auto')
                elif exp_upgrade_btn.is_clicked(mouse_pos):
                    buy_upgrade('exp')
                elif sound_btn.is_clicked(mouse_pos):
                    sound_enabled = not sound_enabled
                elif fps_btn.is_clicked(mouse_pos):
                    change_fps()
                else:
                    check_click(mouse_pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_f:  # Горячая клавиша F для смены FPS
                change_fps()


    # Отрисовка
    screen.fill(BACKGROUND_COLOR)

    # Рисуем кнопки
    click_upgrade_btn.draw(screen, small_font, mouse_pos)
    auto_upgrade_btn.draw(screen, small_font, mouse_pos)
    exp_upgrade_btn.draw(screen, small_font, mouse_pos)
    sound_btn.draw(screen, small_font, mouse_pos)
    fps_btn.draw(screen, small_font, mouse_pos)

    # Рисуем круг
    draw_circle(mouse_pos)

    # Рисуем статистику
    draw_stats()

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

# Завершение игры
pygame.quit()
sys.exit()