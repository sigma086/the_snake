import sys
from random import randint
 
import pygame as pg
 
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
 
# Цвета:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (93, 216, 228)
 
# Цвет фона:
BOARD_BACKGROUND_COLOR = BLACK
 
# Цвет границы ячейки:
BORDER_COLOR = CYAN
 
# Цвет яблока:
APPLE_COLOR = RED
 
# Цвет змейки:
SNAKE_COLOR = GREEN
 
# Скорость движения змейки:
SPEED = 10
 
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
 
# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')
 
# Настройка времени:
clock = pg.time.Clock()
 
 
class GameObject:
    """Базовый класс для всех игровых объектов.
 
    Содержит общие атрибуты (позиция, цвет), метод отрисовки ячейки
    и заготовку метода draw.
    """
 
    def __init__(self, position=CENTER, body_color=None):
        """Инициализирует базовые атрибуты объекта.
 
        Args:
            position: Позиция объекта на игровом поле (кортеж координат).
                      По умолчанию — центр экрана.
            body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color
 
    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку на игровом поле.
 
        Args:
            position: Координаты ячейки в виде кортежа (x, y).
            color: Цвет заливки ячейки. Если не указан, используется
                   body_color объекта.
        """
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)
 
    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране.
 
        Должен быть переопределён в дочерних классах.
 
        Raises:
            NotImplementedError: Если метод не переопределён в дочернем классе.
        """
        raise NotImplementedError(
            f'Метод draw не реализован в классе {type(self).__name__}.'
        )
 
 
class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле.
 
    Яблоко появляется в случайном месте поля. После того как змейка
    его съедает, яблоко перемещается в новое случайное место.
    """
 
    def __init__(self, body_color=APPLE_COLOR, occupied=None):
        """Инициализирует яблоко: задаёт цвет и случайную позицию.
 
        Args:
            body_color: Цвет яблока в формате RGB.
                        По умолчанию — красный.
            occupied: Список занятых позиций (например, сегменты змейки),
                      чтобы яблоко не появилось внутри змейки.
        """
        super().__init__(body_color=body_color)
        self.randomize_position(occupied=occupied)
 
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
        self.draw_cell(self.position)
 
 
class Snake(GameObject):
    """Класс, описывающий змейку и её поведение.
 
    Управляет движением змейки, её отрисовкой и обработкой событий.
    Змейка представлена списком координат сегментов тела.
    """
 
    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует начальное состояние змейки.
 
        Args:
            body_color: Цвет змейки в формате RGB.
                        По умолчанию — зелёный.
        """
        super().__init__(position=CENTER, body_color=body_color)
        self.reset()
 
    def update_direction(self, new_direction):
        """Обновляет направление движения змейки.
 
        Args:
            new_direction: Новое направление движения (кортеж из двух чисел).
        """
        self.direction = new_direction
 
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
        self.last = (
            self.positions.pop() if len(self.positions) > self.length
            else None
        )
 
    def draw(self):
        """Отрисовывает змейку на экране и затирает след хвоста."""
        for position in self.positions[1:]:
            self.draw_cell(position)
 
        # Отрисовка головы змейки:
        self.draw_cell(self.get_head_position())
 
        # Затирание последнего сегмента:
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
 
    def get_head_position(self):
        """Возвращает позицию головы змейки.
 
        Returns:
            Кортеж с координатами головы змейки (первый элемент positions).
        """
        return self.positions[0]
 
    def reset(self):
        """Сбрасывает змейку в начальное состояние.
 
        Восстанавливает исходные значения всех атрибутов змейки.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None
 
 
def handle_keys(snake):
    """Обрабатывает нажатия клавиш для изменения направления движения змейки.
 
    Args:
        snake: Объект змейки, направление которой нужно изменить.
    """
    directions = {
        pg.K_UP: (UP, DOWN),
        pg.K_DOWN: (DOWN, UP),
        pg.K_LEFT: (LEFT, RIGHT),
        pg.K_RIGHT: (RIGHT, LEFT),
    }
 
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif event.key in directions:
                new_dir, opposite = directions[event.key]
                if snake.direction != opposite:
                    snake.update_direction(new_dir)
 
 
def main():
    """Основная функция игры. Содержит игровой цикл."""
    pg.init()
 
    snake = Snake()
    apple = Apple(occupied=snake.positions)
 
    screen.fill(BOARD_BACKGROUND_COLOR)
 
    while True:
        clock.tick(SPEED)
 
        # Обработка нажатий клавиш и обновление направления:
        handle_keys(snake)
 
        # Движение змейки:
        snake.move()
 
        # Проверка: съела ли змейка яблоко или столкнулась с собой:
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied=snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(occupied=snake.positions)
 
        # Отрисовка объектов:
        apple.draw()
        snake.draw()
 
        # Обновление экрана:
        pg.display.update()
 
 
if __name__ == '__main__':
    main()
