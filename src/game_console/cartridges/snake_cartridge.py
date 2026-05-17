import math
import time
import random
import config
from enum import Enum, auto
from typing import List, Tuple, TYPE_CHECKING
from console.controls import ControlsEvent
from cartridges.base_cartridge import GameCartridge

if TYPE_CHECKING:
    from console.game_console import GameConsole

class GameState(Enum):
    WAITING_START = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

WRAP_EDGES = True
STARTING_SPEED = 0.4
SPEED_INCREMENT = 0.02
MIN_SPEED = 0.05
ANIMATION_DURATION = 1.0

class SnakeCartridge(GameCartridge):
    def __init__(self):
        self.__console = None
        self.__state = GameState.WAITING_START
        self.__snake: List[Tuple[int, int]] = []
        self.__dir = Direction.UP
        self.__next_dir = Direction.UP
        self.__apple: Tuple[int, int] = (0, 0)
        self.__last_move_time = 0.0
        self.__speed = STARTING_SPEED
        self.__animation_start_time = 0.0
        self.__is_animating_score = False

    def init(self, game_console: 'GameConsole') -> None:
        self.__console = game_console
        self.__EAT_SOUND = self.__console.load_sound("snake_eat.ogg")
        self.__DIE_SOUND = self.__console.load_sound("snake_die.mp3")
        self.__state = GameState.WAITING_START
        self.force_update()

    def start_new_game(self) -> None:
        self.__snake = [(config.MAIN_MATRIX_WIDTH // 2, config.MAIN_MATRIX_HEIGHT // 2)]
        self.__dir = Direction.UP
        self.__next_dir = Direction.UP
        self.__spawn_apple()
        self.__state = GameState.PLAYING
        self.__speed = STARTING_SPEED
        self.__last_move_time = time.perf_counter()
        self.__is_animating_score = False
        self.force_update()

    def force_update(self) -> None:
        self.__render_board()
        self.__render_score()

    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        if self.__state == GameState.WAITING_START:
            return

        if self.__state == GameState.GAME_OVER:
            is_visible = (int(current_time * 4) % 2) == 0
            if is_visible:
                self.__render_board()
            else:
                board = [[(0, 0, 0) for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
                self.__console.draw_main_display(board)
            self.__console.commit_displays()
            return

        for event in controls_events:
            if event == ControlsEvent.BTN_UP_PRESSED and self.__dir != Direction.DOWN:
                self.__next_dir = Direction.UP
            elif event == ControlsEvent.BTN_DOWN_PRESSED and self.__dir != Direction.UP:
                self.__next_dir = Direction.DOWN
            elif event == ControlsEvent.BTN_LEFT_PRESSED and self.__dir != Direction.RIGHT:
                self.__next_dir = Direction.LEFT
            elif event == ControlsEvent.BTN_RIGHT_PRESSED and self.__dir != Direction.LEFT:
                self.__next_dir = Direction.RIGHT

        if current_time - self.__last_move_time >= self.__speed:
            self.__dir = self.__next_dir
            head_x, head_y = self.__snake[0]
            
            if self.__dir == Direction.UP:
                head_y += 1
            elif self.__dir == Direction.DOWN:
                head_y -= 1
            elif self.__dir == Direction.LEFT:
                head_x -= 1
            elif self.__dir == Direction.RIGHT:
                head_x += 1

            if WRAP_EDGES:
                head_x %= config.MAIN_MATRIX_WIDTH
                head_y %= config.MAIN_MATRIX_HEIGHT
            else:
                if head_x < 0 or head_x >= config.MAIN_MATRIX_WIDTH or head_y < 0 or head_y >= config.MAIN_MATRIX_HEIGHT:
                    self.__state = GameState.GAME_OVER
                    self.__DIE_SOUND.play()
                    return

            new_head = (head_x, head_y)
            if new_head in self.__snake:
                self.__state = GameState.GAME_OVER
                self.__DIE_SOUND.play()
                return

            self.__snake.insert(0, new_head)
            if new_head == self.__apple:
                self.__EAT_SOUND.play()
                self.__spawn_apple()
                self.__speed = max(MIN_SPEED, self.__speed - SPEED_INCREMENT)
                self.__is_animating_score = True
                self.__animation_start_time = current_time
            else:
                self.__snake.pop()

            self.__last_move_time = current_time

        self.force_update()
        
        # Apple glow & secondary display animation
        apple_brightness = int(127 + 128 * math.sin(current_time * 5))
        self.__render_apple(apple_brightness)
        
        if self.__is_animating_score:
            if current_time - self.__animation_start_time > ANIMATION_DURATION:
                self.__is_animating_score = False
                self.__console.fill_secondary_display((0, 0, 0))
            else:
                c = int(255 * (1 - (current_time - self.__animation_start_time) / ANIMATION_DURATION))
                self.__console.fill_secondary_display((0, c, c))

        self.__console.commit_displays()

    def __spawn_apple(self) -> None:
        while True:
            x = random.randrange(config.MAIN_MATRIX_WIDTH)
            y = random.randrange(config.MAIN_MATRIX_HEIGHT)
            if (x, y) not in self.__snake:
                self.__apple = (x, y)
                break

    def __render_board(self) -> None:
        board = [[(0, 0, 0) for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
        for i, (x, y) in enumerate(self.__snake):
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            board[y][x] = color
        self.__console.draw_main_display(board)
        
    def __render_apple(self, brightness: int) -> None:
        board = [[(0, 0, 0) for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
        for i, (x, y) in enumerate(self.__snake):
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            board[y][x] = color
        board[self.__apple[1]][self.__apple[0]] = (brightness, 0, 0)
        self.__console.draw_main_display(board)

    def __render_score(self) -> None:
        self.__console.set_segment_display_text(str(len(self.__snake)), True)

    def deinit(self) -> None:
        pass
