import time
import math
import config
from enum import Enum, auto
from typing import List, Tuple, TYPE_CHECKING
from console.controls import ControlsEvent, ControlsState
from cartridges.base_cartridge import GameCartridge

if TYPE_CHECKING:
    from console.game_console import GameConsole

BALL_COLOR = (255, 255, 255)
P1_COLOR = (0, 255, 255)
P2_COLOR = (255, 0, 255)
SPEED_INDICATOR_COLOR = (255, 165, 0)
PADDLE_SIZE = 4

INITIAL_INTERVAL_S = 0.5
INTERVAL_DECREMENT_S = 0.02
MIN_INTERVAL_S = 0.05
BREAK_BETWEEN_GAMES_S = 3

class GameState(Enum):
    WAITING_START = auto()
    PLAYING = auto()
    SCORED = auto()

class PongCartridge(GameCartridge):
    def __init__(self):
        self.__console = None
        self.__state = GameState.WAITING_START
        self.__p1_y = 0
        self.__p2_y = 0
        self.__ball_x = 0
        self.__ball_y = 0
        self.__ball_dx = 1
        self.__ball_dy = 1
        self.__p1_score = 0
        self.__p2_score = 0
        self.__interval = INITIAL_INTERVAL_S
        self.__last_move_time = 0.0
        self.__scored_time = 0.0

    def init(self, game_console: 'GameConsole') -> None:
        self.__console = game_console
        self.__BEEP_SOUND = self.__console.load_sound("ping_pong_8bit_beeep.ogg")
        self.__PEEEEEP_SOUND = self.__console.load_sound("ping_pong_8bit_peeeeeep.ogg")
        self.__PLOP_SOUND = self.__console.load_sound("ping_pong_8bit_plop.ogg")
        self.__state = GameState.WAITING_START
        print("PongCartridge initialized")
        self.start_new_game()

    def start_new_game(self) -> None:
        self.__p1_score = 0
        self.__p2_score = 0
        self.__reset_round()
        self.__state = GameState.PLAYING
        self.force_update()

    def __reset_round(self):
        self.__p1_y = (config.MAIN_MATRIX_HEIGHT - PADDLE_SIZE) // 2
        self.__p2_y = (config.MAIN_MATRIX_HEIGHT - PADDLE_SIZE) // 2
        self.__ball_x = config.MAIN_MATRIX_WIDTH // 2
        self.__ball_y = config.MAIN_MATRIX_HEIGHT // 2
        self.__ball_dx = 1 if (self.__p1_score + self.__p2_score) % 2 == 0 else -1
        self.__ball_dy = 1
        self.__interval = INITIAL_INTERVAL_S
        self.__last_move_time = time.perf_counter()
        self.__BEEP_SOUND.play()

    def force_update(self) -> None:
        self.__render_board()
        self.__render_speed()
        self.__render_score()

    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        if self.__state == GameState.WAITING_START:
            return

        if self.__state == GameState.SCORED:
            if current_time - self.__scored_time > BREAK_BETWEEN_GAMES_S:
                self.__reset_round()
                self.__state = GameState.PLAYING
            else:
                self.force_update()
                self.__console.commit_displays()
                return

        # Continuous paddle movement based on held buttons
        active_states = self.__console.get_active_control_states()
        
        # P1 uses LEFT (up) and DOWN (down)
        if ControlsState.BTN_LEFT_HOLD in active_states:
            self.__p1_y = max(0, self.__p1_y - 1)
        if ControlsState.BTN_DOWN_HOLD in active_states:
            self.__p1_y = min(config.MAIN_MATRIX_HEIGHT - PADDLE_SIZE, self.__p1_y + 1)

        # P2 uses UP (up) and RIGHT (down)
        if ControlsState.BTN_UP_HOLD in active_states:
            self.__p2_y = max(0, self.__p2_y - 1)
        if ControlsState.BTN_RIGHT_HOLD in active_states:
            self.__p2_y = min(config.MAIN_MATRIX_HEIGHT - PADDLE_SIZE, self.__p2_y + 1)

        if current_time - self.__last_move_time >= self.__interval:
            self.__ball_x += self.__ball_dx
            self.__ball_y += self.__ball_dy

            # Wall collision (top and bottom)
            if self.__ball_y < 0:
                self.__ball_y = 1
                self.__ball_dy *= -1
                self.__PLOP_SOUND.play()
            elif self.__ball_y >= config.MAIN_MATRIX_HEIGHT:
                self.__ball_y = config.MAIN_MATRIX_HEIGHT - 2
                self.__ball_dy *= -1
                self.__PLOP_SOUND.play()

            # P1 Paddle collision (left side)
            if self.__ball_x == 1 and self.__p1_y - 1 <= self.__ball_y < self.__p1_y + PADDLE_SIZE + 1:
                self.__ball_dx = 1
                self.__interval = max(MIN_INTERVAL_S, self.__interval - INTERVAL_DECREMENT_S)
                self.__PLOP_SOUND.play()
                
            # P2 Paddle collision (right side)
            elif self.__ball_x == config.MAIN_MATRIX_WIDTH - 2 and self.__p2_y - 1 <= self.__ball_y < self.__p2_y + PADDLE_SIZE + 1:
                self.__ball_dx = -1
                self.__interval = max(MIN_INTERVAL_S, self.__interval - INTERVAL_DECREMENT_S)
                self.__PLOP_SOUND.play()

            # Score conditions
            elif self.__ball_x < 0:
                self.__p2_score += 1
                self.__scored_time = current_time
                self.__state = GameState.SCORED
                self.__PEEEEEP_SOUND.play()
            elif self.__ball_x >= config.MAIN_MATRIX_WIDTH:
                self.__p1_score += 1
                self.__scored_time = current_time
                self.__state = GameState.SCORED
                self.__PEEEEEP_SOUND.play()

            self.__last_move_time = current_time

        self.force_update()
        self.__console.commit_displays()

    def __render_board(self) -> None:
        board = [[(0, 0, 0) for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]

        # Draw ball
        if 0 <= self.__ball_y < config.MAIN_MATRIX_HEIGHT and 0 <= self.__ball_x < config.MAIN_MATRIX_WIDTH:
            board[self.__ball_y][self.__ball_x] = BALL_COLOR
        
        # Draw P1 Paddle
        for i in range(PADDLE_SIZE):
            if 0 <= self.__p1_y + i < config.MAIN_MATRIX_HEIGHT:
                board[self.__p1_y + i][0] = P1_COLOR
                
        # Draw P2 Paddle
        for i in range(PADDLE_SIZE):
            if 0 <= self.__p2_y + i < config.MAIN_MATRIX_HEIGHT:
                board[self.__p2_y + i][config.MAIN_MATRIX_WIDTH - 1] = P2_COLOR

        self.__console.draw_main_display(board)

    def __render_speed(self) -> None:
        board = [[(0, 0, 0) for _ in range(config.SECONDARY_MATRIX_WIDTH)] for _ in range(config.SECONDARY_MATRIX_HEIGHT)]
        
        current_time = time.perf_counter()
        if self.__state == GameState.SCORED:
            is_visible = (int((current_time - self.__scored_time) * 10) % 2) == 0
            if not is_visible:
                self.__console.draw_secondary_display(board)
                return
            glow = 1.0
        else:
            glow = 0.5 + 0.5 * math.sin(current_time * 5)
            
        speed_fraction = 1.0 - (self.__interval - MIN_INTERVAL_S) / (INITIAL_INTERVAL_S - MIN_INTERVAL_S)
        speed_fraction = max(0.0, min(1.0, speed_fraction))
        
        h = 1.0 + speed_fraction * (config.SECONDARY_MATRIX_HEIGHT - 1.0)
        color = SPEED_INDICATOR_COLOR
        
        for y in range(config.SECONDARY_MATRIX_HEIGHT):
            if y < int(h):
                brightness = 1.0
            elif y == int(h):
                brightness = h - int(h)
            else:
                brightness = 0.0
                
            c = (int(color[0] * brightness * glow), int(color[1] * brightness * glow), int(color[2] * brightness * glow))
            for x in range(config.SECONDARY_MATRIX_WIDTH):
                board[config.SECONDARY_MATRIX_HEIGHT - y - 1][x] = c
                
        self.__console.draw_secondary_display(board)

    def __render_score(self) -> None:
        text = f"{min(99, self.__p1_score):02d}{min(99, self.__p2_score):02d}"
        self.__console.set_segment_display_text(text)
        self.__console.set_segment_display_colon(0x02) # Centre colon

    def deinit(self) -> None:
        self.__console.set_segment_display_colon(0x00) # Reset colon
        print("PongCartridge deinitialized")