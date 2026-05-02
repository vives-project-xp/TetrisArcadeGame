import time
from enum import Enum, auto
from typing import List, TYPE_CHECKING

from cartridges.base_cartridge import GameCartridge
import config
import random
from console.controls import ControlsEvent, ControlsState

if TYPE_CHECKING:
    from console.game_console import GameConsole

# inspired by Javier Lopez's work
# https://javilop.com/gamedev/tetris-tutorial-in-c-platform-independent-focused-in-game-logic-for-beginners/

BASE_DROP_INTERVAL_S = 0.50
MIN_DROP_INTERVAL_S = 0.08
SPEED_FACTOR_PER_LEVEL = 0.90
LINES_PER_LEVEL = 10
PIECE_FAST_DOWN_PERIOD_S = 0.1
GAME_OVER_CURTAIN_STEP_S = 0.06
GAME_OVER_FINAL_BLINK_S = 0.4
OFF = (0, 0, 0)
RED = (0xFF, 0x00, 0x00)

def __rotate_piece(piece):
    """Rotate a piece 90 degrees clockwise."""
    return [list(row) for row in zip(*piece[::-1])]

PIECE_BLOCKS = 5
def __generate_pieces():
    """Generates 4 rotations for each of the 7 pieces respecting the pivot at (2, 2)."""
    base_pieces = [
        # 0: Square
        [
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,2,1,0],
            [0,0,1,1,0],
            [0,0,0,0,0]
        ],
        # 1: I
        [
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,1,2,1,1],
            [0,0,0,0,0],
            [0,0,0,0,0]
        ],
        # 2: L
        [
            [0,0,0,0,0],
            [0,0,1,0,0],
            [0,0,2,0,0],
            [0,0,1,1,0],
            [0,0,0,0,0]
        ],
        # 3: L mirrored
        [
            [0,0,0,0,0],
            [0,0,1,0,0],
            [0,0,2,0,0],
            [0,1,1,0,0],
            [0,0,0,0,0]
        ],
        # 4: N
        [
            [0,0,0,0,0],
            [0,0,0,1,0],
            [0,0,2,1,0],
            [0,0,1,0,0],
            [0,0,0,0,0]
        ],
        # 5: N mirrored
        [
            [0,0,0,0,0],
            [0,0,1,0,0],
            [0,0,2,1,0],
            [0,0,0,1,0],
            [0,0,0,0,0]
        ],
        # 6: T
        [
            [0,0,0,0,0],
            [0,0,1,0,0],
            [0,0,2,1,0],
            [0,0,1,0,0],
            [0,0,0,0,0]
        ]
    ]
    
    all_pieces = []
    for piece in base_pieces:
        rotations = [piece]
        for _ in range(3):
            rotations.append(__rotate_piece(rotations[-1]))
        all_pieces.append(rotations)
    return all_pieces

PIECES = __generate_pieces()
COLORS = [
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0x00),
    (0x00, 0x00, 0xff),
    (0x00, 0xff, 0xff),
    (0xff, 0x00, 0xff),
    (0xff, 0xff, 0x00),
    (0xff, 0xff, 0xff)
]

class GameState(Enum):
    WAITING_START = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class BoardBlock():
    def __init__(self):
        self.__state = None

    def is_free(self) -> bool:
        return self.__state == None
    
    def is_filled(self) -> bool:
        return not self.is_free()
    
    def set_color(self, color: tuple[int,int,int] | None) -> None:
        self.__state = color
    
    def get_color(self) -> tuple[int,int,int]:
        return self.__state if self.__state else (0,0,0)

class TetrisCartridge(GameCartridge):
    def __init__(self):
        self.__console = None
        self.__board = []
        self.__state = GameState.WAITING_START
        self.__currPiecePosX = 0
        self.__currPiecePosY = 0
        self.__currPieceId = 0
        self.__currPieceRotation = 0
        self.__pieceLastDropTime = 0.0
        self.__pieceLastFastDownDropTime = 0.0
        self.__currPieceColor = (0,0,0)
        self.__nextPieceId = 0
        self.__nextPieceRotation = 0
        self.__nextPieceColor = (0,0,0)
        self.__lines_cleared_total = 0
        self.__level = 1
        self.__score = 0
        self.__high_score = 0
        self.__curr_drop_interval = 0
        self.__game_over_started_at = 0.0
        self.__game_over_render_state = None
    
    def init(self, game_console: 'GameConsole') -> None:
        self.__console = game_console
        self.__console.load_music("tetris_theme.mp3")
        self.__console.set_music_volume(0.15)
        self.__MOVE_PIECE_SOUND = self.__console.load_sound("move_piece.wav")
        self.__CLEAR_LINE_SOUND = self.__console.load_sound("clear_line.mp3")
        self.__PIECE_FALLING_SOUND = self.__console.load_sound("piece_falling.mp3")
        self.__ROTATE_PIECE_SOUND = self.__console.load_sound("rotate_piece.wav")
        self.__GAME_OVER_SOUND = self.__console.load_sound("tetris_game_over.mp3")
        print("TetrisCartridge initialized")
        self.__state = GameState.WAITING_START
        self.force_update()
    
    def start_new_game(self) -> None:
        self.__board = [[BoardBlock() for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
        self.__state = GameState.PLAYING
        self.__pieceLastDropTime = 0.0
        self.__lines_cleared_total = 0
        self.__level = 1
        self.__score = 0
        self.__pieceLastFastDownDropTime = 0.0
        self.__game_over_started_at = 0.0
        self.__game_over_render_state = None

        self.__nextPieceId = random.randrange(len(PIECES))
        self.__nextPieceRotation = random.randrange(4)
        self.__nextPieceColor = random.choice(COLORS)

        self.__console.replay_music()
        self.__create_new_piece()
        self.__curr_drop_interval = BASE_DROP_INTERVAL_S

        self.force_update()

    def __create_new_piece(self) -> None:
        self.__currPieceId = self.__nextPieceId
        self.__currPieceRotation = self.__nextPieceRotation
        self.__currPieceColor = self.__nextPieceColor

        self.__nextPieceId = random.randrange(len(PIECES))
        self.__nextPieceRotation = random.randrange(4)
        self.__nextPieceColor = random.choice(COLORS)

        self.__currPiecePosX = (config.MAIN_MATRIX_WIDTH // 2) - 2 
        self.__currPiecePosY = -2
    
    def __is_possible_movement(self, pX: int, pY: int, pPiece: int, pRotation: int) -> bool:
        """
        Check if the piece can be stored at this position without any collision.
        
        Args:
            pX: horizontal position in blocks
            pY: vertical position in blocks
            pPiece: index of the piece in PIECES list
            pRotation: index of the piece rotation
        Returns:
            whether the movement is possible
        """
        # for (int i1 = pX, i2 = 0; i1 < pX + PIECE_BLOCKS; i1++, i2++)
        for i1, i2 in zip(range(pX, pX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            # for (int j1 = pY, j2 = 0; j1 < pY + PIECE_BLOCKS; j1++, j2++)
            for j1, j2 in zip(range(pY, pY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                # Check if piece has a block here
                if PIECES[pPiece][pRotation][j2][i2] != 0:
                    # Check board limits
                    if i1 < 0 or i1 >= config.MAIN_MATRIX_WIDTH or j1 >= config.MAIN_MATRIX_HEIGHT:
                        return False
                    # Check collision with placed blocks (only if within board vertically)
                    if j1 >= 0 and not self.__board[j1][i1].is_free():
                        return False
        return True

    def __store_piece(self, pX: int, pY: int, pPiece: int, pRotation: int):
        """Store each block of the piece into the board."""
        for i1, i2 in zip(range(pX, pX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            for j1, j2 in zip(range(pY, pY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                if PIECES[pPiece][pRotation][j2][i2] != 0:
                    if 0 <= i1 < config.MAIN_MATRIX_WIDTH and 0 <= j1 < config.MAIN_MATRIX_HEIGHT:
                        self.__board[j1][i1].set_color(self.__currPieceColor)
                        
    def __is_game_over(self) -> bool:
        """Check if game is over because a piece reached the top."""
        # If the first line has blocks, then game over
        for i in range(config.MAIN_MATRIX_WIDTH):
            if not self.__board[0][i].is_free():
                return True
        return False
        
    def __delete_line(self, pY: int):
        """Delete a line of the board by moving all above lines down."""
        for j in range(pY, 0, -1):
            for i in range(config.MAIN_MATRIX_WIDTH):
                # Copy the colored state of the block above
                if not self.__board[j-1][i].is_free():
                    self.__board[j][i].set_color(self.__board[j-1][i].get_color())
                else:
                    self.__board[j][i].set_color(None) # set free
                    
        # Clear the top-most row since it has no row above it
        for i in range(config.MAIN_MATRIX_WIDTH):
             self.__board[0][i].set_color(None)
             
    def __delete_possible_lines(self) -> int:
        removed = 0
        for j in range(config.MAIN_MATRIX_HEIGHT):
            filled_count = 0
            for i in range(config.MAIN_MATRIX_WIDTH):
                if not self.__board[j][i].is_free():
                    filled_count += 1
            if filled_count == config.MAIN_MATRIX_WIDTH:
                self.__CLEAR_LINE_SOUND.play()
                self.__delete_line(j)
                removed += 1
        return removed

    def __recalculate_level(self) -> None:
        self.__level = 1 + (self.__lines_cleared_total // LINES_PER_LEVEL)
        self.__curr_drop_interval = max(
            MIN_DROP_INTERVAL_S,
            BASE_DROP_INTERVAL_S * (SPEED_FACTOR_PER_LEVEL ** (self.__level - 1))
        )

    def __add_score_for_line_clear(self, cleared_lines: int) -> None:
        table = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.__score += table.get(cleared_lines, 1200) * self.__level
        if self.__score > self.__high_score:
            self.__high_score = self.__score

    def __score_for_4digit_display(self, value: int) -> str:
        return str(min(value, 9999))

    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        if self.__state == GameState.WAITING_START:
            return

        if self.__state == GameState.GAME_OVER:
            self.__tick_game_over(current_time)
            return

        # Initialize timer on the first tick
        if self.__pieceLastDropTime == 0.0:
            self.__pieceLastDropTime = current_time

        should_update_main_display = False
        score_at_tick_start = self.__score
        if controls_events:
            for event in controls_events:
                if event == ControlsEvent.BTN_LEFT_PRESSED:
                    if self.__is_possible_movement(self.__currPiecePosX - 1, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation):
                        self.__currPiecePosX -= 1
                        should_update_main_display = True
                        # self.__MOVE_PIECE_SOUND.play()
                elif event == ControlsEvent.BTN_RIGHT_PRESSED:
                    if self.__is_possible_movement(self.__currPiecePosX + 1, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation):
                        self.__currPiecePosX += 1
                        should_update_main_display = True
                        # self.__MOVE_PIECE_SOUND.play()
                elif event == ControlsEvent.BTN_DOWN_PRESSED:
                    # Drop piece down immediately
                    if self.__is_possible_movement(self.__currPiecePosX, self.__currPiecePosY + 1, self.__currPieceId, self.__currPieceRotation):
                        self.__drop_the_piece(current_time)
                        should_update_main_display = True
                elif event == ControlsEvent.BTN_UP_PRESSED:
                    # Rotate the piece independently
                    next_rotation = (self.__currPieceRotation + 1) % 4
                    if self.__is_possible_movement(self.__currPiecePosX, self.__currPiecePosY, self.__currPieceId, next_rotation):
                        self.__currPieceRotation = next_rotation
                        should_update_main_display = True
                        self.__ROTATE_PIECE_SOUND.play()

        if current_time - self.__pieceLastDropTime > self.__curr_drop_interval:
            self.__drop_the_piece(current_time)
            should_update_main_display = True
            self.__pieceLastDropTime = current_time
        
        if current_time - self.__pieceLastFastDownDropTime > PIECE_FAST_DOWN_PERIOD_S:
            if ControlsState.BTN_DOWN_HOLD in self.__console.get_active_control_states():
                self.__drop_the_piece(current_time)
                    
                should_update_main_display = True
                self.__pieceLastFastDownDropTime = current_time
            else:
                self.__pieceLastFastDownDropTime = 0.0

        if self.__state != GameState.PLAYING:
            return

        should_update_score_display = score_at_tick_start != self.__score
        
        if should_update_main_display:
            self.__console.draw_main_display(self.__render_main_display_contents())
            self.__console.draw_secondary_display(self.__render_next_piece_display_contents())

        if should_update_score_display:
            self.__update_score_display()

        if should_update_main_display or should_update_score_display:
            self.__console.commit_displays()

    def __drop_the_piece(self, current_time: float) -> None:
        if self.__is_possible_movement(self.__currPiecePosX, self.__currPiecePosY + 1, self.__currPieceId, self.__currPieceRotation):
            self.__currPiecePosY += 1
        else:
            self.__store_piece(self.__currPiecePosX, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation)
            self.__PIECE_FALLING_SOUND.play()
            cleared = self.__delete_possible_lines()
            if cleared > 0:
                self.__lines_cleared_total += cleared
                self.__recalculate_level()
                self.__add_score_for_line_clear(cleared)
                
            if self.__is_game_over():
                self.__enter_game_over_state(current_time)
            else:
                self.__create_new_piece()
            
    def deinit(self) -> None:
        print("TetrisCartridge deinitialized")

    def can_enter_screensaver(self) -> bool:
        return self.__state != GameState.PLAYING
    
    def __render_main_display_contents(self) -> List[List[tuple]]:
        # print(f"mPosX: {self.__currPiecePosX}, mPosY: {self.__currPiecePosY}, mPiece: {self.__currPieceId}, mRotation: {self.__currPieceRotation}, mTime1: {self.__pieceLastDropTime}, mColor: {self.__currPieceColor}")
        colored_board = [[block.get_color() for block in row] for row in self.__board]
        for i1, i2 in zip(range(self.__currPiecePosX, self.__currPiecePosX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            for j1, j2 in zip(range(self.__currPiecePosY, self.__currPiecePosY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                if PIECES[self.__currPieceId][self.__currPieceRotation][j2][i2] != 0:
                    if 0 <= i1 < config.MAIN_MATRIX_WIDTH and 0 <= j1 < config.MAIN_MATRIX_HEIGHT:
                        colored_board[j1][i1] = self.__currPieceColor
        return colored_board

    def __render_next_piece_display_contents(self) -> List[List[tuple]]:
        display = [[(0, 0, 0) for _ in range(5)] for _ in range(5)]
        
        for y in range(PIECE_BLOCKS):
            for x in range(PIECE_BLOCKS):
                if PIECES[self.__nextPieceId][self.__nextPieceRotation][y][x] != 0:
                    display[y][x] = self.__nextPieceColor
                    
        return display
    
    def __update_score_display(self) -> None:
        self.__console.set_segment_display_text(self.__score_for_4digit_display(self.__score), True)

    def force_update(self) -> None:
        if self.__state == GameState.WAITING_START:
            self.__console.fill_main_display(OFF)
            self.__console.fill_secondary_display(OFF)
            self.__console.set_segment_display_text("----")
        elif self.__state == GameState.GAME_OVER:
            self.__draw_game_over_displays(time.perf_counter())
        else:
            self.__console.draw_main_display(self.__render_main_display_contents())
            self.__console.draw_secondary_display(self.__render_next_piece_display_contents())
            self.__update_score_display()
        self.__console.commit_displays()

    def __enter_game_over_state(self, current_time: float) -> None:
        self.__state = GameState.GAME_OVER
        self.__game_over_started_at = current_time
        self.__game_over_render_state = None
        self.__console.pause_music()
        self.__GAME_OVER_SOUND.play()
        self.__draw_game_over_displays(current_time)
        self.__console.commit_displays()

    def __tick_game_over(self, current_time: float) -> None:
        render_state = self.__get_game_over_render_state(current_time)
        if render_state == self.__game_over_render_state:
            return

        self.__draw_game_over_displays(current_time)
        self.__console.commit_displays()

    def __get_game_over_render_state(self, current_time: float) -> tuple[str, int]:
        elapsed = max(0.0, current_time - self.__game_over_started_at)
        curtain_rows = int(elapsed / GAME_OVER_CURTAIN_STEP_S) + 1
        if curtain_rows <= config.MAIN_MATRIX_HEIGHT:
            return ("curtain", curtain_rows)
        blink_visible = int((elapsed - (config.MAIN_MATRIX_HEIGHT * GAME_OVER_CURTAIN_STEP_S)) / GAME_OVER_FINAL_BLINK_S) % 2 == 0
        return ("final", 1 if blink_visible else 0)

    def __draw_game_over_displays(self, current_time: float) -> None:
        render_state = self.__get_game_over_render_state(current_time)
        self.__game_over_render_state = render_state
        self.__console.draw_main_display(self.__render_game_over_main_display(render_state))
        self.__console.draw_secondary_display(self.__render_game_over_secondary_display(render_state))
        self.__update_score_display()

    def __render_game_over_main_display(self, render_state: tuple[str, int]) -> List[List[tuple]]:
        mode, value = render_state
        if mode == "curtain":
            return [
                [RED if row_index < value else OFF for _ in range(config.MAIN_MATRIX_WIDTH)]
                for row_index in range(config.MAIN_MATRIX_HEIGHT)
            ]
        if not value:
            return [
                [OFF for _ in range(config.MAIN_MATRIX_WIDTH)]
                for _ in range(config.MAIN_MATRIX_HEIGHT)
            ]

        pattern = [
            "..........",
            "..........",
            "..........",
            ".###..###.",
            ".###..###.",
            "#.....#...",
            "#.....#...",
            "#.....#...",
            "#.....#...",
            "#.##..#.##",
            "#.##..#.##",
            "#..#..#..#",
            "#..#..#..#",
            "#..#..#..#",
            "#..#..#..#",
            ".###..###.",
            ".###..###.",
            "..........",
            "..........",
            "..........",
        ]
        return [
            [RED if cell == "#" else OFF for cell in row]
            for row in pattern
        ]

    def __render_game_over_secondary_display(self, render_state: tuple[str, int]) -> List[List[tuple]]:
        mode, value = render_state
        if mode == "curtain":
            return [
                [RED if row_index < min(value, config.SECONDARY_MATRIX_HEIGHT) else OFF for _ in range(config.SECONDARY_MATRIX_WIDTH)]
                for row_index in range(config.SECONDARY_MATRIX_HEIGHT)
            ]

        pattern = [
            "#...#",
            ".#.#.",
            "..#..",
            ".#.#.",
            "#...#",
        ]
        return [
            [RED if cell == "#" else OFF for cell in row]
            for row in pattern
        ]
