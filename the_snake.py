from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр экрана:
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов.

    Содержит общие атрибуты (позиция, цвет) и заготовку метода draw.
    """

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовые атрибуты объекта.

        Args:
            position: Позиция объекта на игровом поле (кортеж координат).
                      По умолчанию — центр экрана.
            body_color: Цвет объекта в формате RGB.
        """
        self.position = position if position is not None else CENTER
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране.

        Должен быть переопределён в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле.

    Яблоко появляется в случайном месте поля. После того как змейка
    его съедает, яблоко перемещается в новое случайное место.
    """

    def __init__(self):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied=None):
        """Устанавливает случайное положение яблока на игровом поле.

        Координаты выбираются так, чтобы яблоко оказалось в пределах
        игрового поля и не совпадало с занятыми позициями.

        Args:
            occupied: Список занятых позиций (например, сегменты змейки).
        """
        occupied = occupied or []
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if (x, y) not in occupied:
                self.position = (x, y)
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение.

    Управляет движением змейки, её отрисовкой и обработкой событий.
    Змейка представлена списком координат сегментов тела.
    """

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        super().__init__(position=CENTER, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки на одну ячейку в текущем направлении.

        Добавляет новую голову в начало списка позиций и удаляет
        последний элемент, если длина змейки не увеличилась.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране и затирает след хвоста."""
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки:
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента:
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки.

        Returns:
            Кортеж с координатами головы змейки (первый элемент positions).
        """
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние.

        Восстанавливает исходные значения всех атрибутов змейки
        и очищает экран.
        """
        self.length = 1
        self.positions = [CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления движения змейки.

    Args:
        game_object: Объект змейки, направление которой нужно изменить.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры. Содержит игровой цикл."""
    pygame.init()

    snake = Snake()
    apple = Apple()

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        # Обработка нажатий клавиш:
        handle_keys(snake)

        # Обновление направления движения:
        snake.update_direction()

        # Движение змейки:
        snake.move()

        # Проверка: съела ли змейка яблоко:
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied=snake.positions)

        # Проверка столкновения змейки с собой:
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied=snake.positions)

        # Отрисовка объектов:
        apple.draw()
        snake.draw()

        # Обновление экрана:
        pygame.display.update()


if __name__ == '__main__':
    main()
