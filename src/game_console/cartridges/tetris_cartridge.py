import time
from typing import List, TYPE_CHECKING

from cartridges.base_cartridge import GameCartridge
import config
import random
from console.controls import ControlsEvent

if TYPE_CHECKING:
    from console.game_console import GameConsole

# inspired by Javier Lopez's work
# https://javilop.com/gamedev/tetris-tutorial-in-c-platform-independent-focused-in-game-logic-for-beginners/

BASE_DROP_INTERVAL_S = 0.50
MIN_DROP_INTERVAL_S = 0.08
SPEED_FACTOR_PER_LEVEL = 0.90
LINES_PER_LEVEL = 10
PIECE_BLOCKS = 5

def _rotate_piece(piece):
    """Rotate a piece 90 degrees clockwise."""
    return [list(row) for row in zip(*piece[::-1])]

def _generate_pieces():
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
            rotations.append(_rotate_piece(rotations[-1]))
        all_pieces.append(rotations)
    return all_pieces

PIECES = _generate_pieces()
COLORS = [
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0x00),
    (0x00, 0x00, 0xff),
    (0x00, 0xff, 0xff),
    (0xff, 0x00, 0xff),
    (0xff, 0xff, 0x00),
    (0xff, 0xff, 0xff)
]

class BoardBlock():
    def __init__(self):
        self.__state = None

    def is_free(self) -> bool:
        return self.__state == None
    
    def is_filled(self) -> bool:
        return not self.is_free()
    
    def set_color(self, color: tuple[int,int,int]) -> None:
        self.__state = color
    
    def get_color(self) -> tuple[int,int,int]:
        return self.__state if self.__state else (0,0,0)

class TetrisCartridge(GameCartridge):
    def __init__(self):
        self.console = None
        self.__board = []
        self.mPosX = 0
        self.mPosY = 0
        self.mPiece = 0
        self.mRotation = 0
        self.mTime1 = 0.0
        self.mColor = (0,0,0)
        self.lines_cleared_total = 0
        self.level = 1
        self.score = 0
        self.high_score = 0
        self.curr_drop_interval = 0
    
    def init(self, game_console: 'GameConsole') -> None:
        self.console = game_console
        self.console.play_music("tetris_theme.mp3")
        print("TetrisCartridge initialized")
        self.start_new_game()
    
    def start_new_game(self) -> None:
        self.__board = [[BoardBlock() for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
        self.mTime1 = 0.0
        self.lines_cleared_total = 0
        self.level = 1
        self.score = 0
        self.create_new_piece()
        self.curr_drop_interval = BASE_DROP_INTERVAL_S

    def create_new_piece(self) -> None:
        self.mPiece = random.randrange(len(PIECES))
        self.mRotation = random.randrange(4)
        self.mPosX = (config.MAIN_MATRIX_WIDTH // 2) - 2 
        self.mPosY = -2 
        self.mColor = random.choice(COLORS)
    
    def is_possible_movement(self, pX: int, pY: int, pPiece: int, pRotation: int) -> bool:
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

    def store_piece(self, pX: int, pY: int, pPiece: int, pRotation: int):
        """Store each block of the piece into the board."""
        for i1, i2 in zip(range(pX, pX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            for j1, j2 in zip(range(pY, pY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                if PIECES[pPiece][pRotation][j2][i2] != 0:
                    if 0 <= i1 < config.MAIN_MATRIX_WIDTH and 0 <= j1 < config.MAIN_MATRIX_HEIGHT:
                        self.__board[j1][i1].set_color(self.mColor)
                        
    def is_game_over(self) -> bool:
        """Check if game is over because a piece reached the top."""
        # If the first line has blocks, then game over
        for i in range(config.MAIN_MATRIX_WIDTH):
            if not self.__board[0][i].is_free():
                return True
        return False
        
    def delete_line(self, pY: int):
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
             
    def delete_possible_lines(self) -> int:
        removed = 0
        for j in range(config.MAIN_MATRIX_HEIGHT):
            filled_count = 0
            for i in range(config.MAIN_MATRIX_WIDTH):
                if not self.__board[j][i].is_free():
                    filled_count += 1
            if filled_count == config.MAIN_MATRIX_WIDTH:
                self.delete_line(j)
                removed += 1
        return removed

    def _recalculate_level(self) -> None:
        self.level = 1 + (self.lines_cleared_total // LINES_PER_LEVEL)
        self.curr_drop_interval = max(
            MIN_DROP_INTERVAL_S,
            BASE_DROP_INTERVAL_S * (SPEED_FACTOR_PER_LEVEL ** (self.level - 1))
        )

    def _add_score_for_line_clear(self, cleared_lines: int) -> None:
        table = {1: 40, 2: 100, 3: 300, 4: 1200}
        self.score += table.get(cleared_lines, 1200) * self.level
        if self.score > self.high_score:
            self.high_score = self.score

    def _score_for_4digit_display(self, value: int) -> int:
        return min(value, 9999)

    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        # Initialize timer on the first tick
        if self.mTime1 == 0.0:
            self.mTime1 = current_time

        should_update_main_display = False
        if controls_events:
            for event in controls_events:
                if event == ControlsEvent.BTN_LEFT_PRESSED:
                    if self.is_possible_movement(self.mPosX - 1, self.mPosY, self.mPiece, self.mRotation):
                        self.mPosX -= 1
                        should_update_main_display = True
                elif event == ControlsEvent.BTN_RIGHT_PRESSED:
                    if self.is_possible_movement(self.mPosX + 1, self.mPosY, self.mPiece, self.mRotation):
                        self.mPosX += 1
                        should_update_main_display = True
                elif event == ControlsEvent.BTN_DOWN_PRESSED:
                    # Drop piece down immediately
                    if self.is_possible_movement(self.mPosX, self.mPosY + 1, self.mPiece, self.mRotation):
                        self.mPosY += 1
                        should_update_main_display = True
                elif event == ControlsEvent.BTN_UP_PRESSED:
                    # Rotate the piece independently
                    next_rotation = (self.mRotation + 1) % 4
                    if self.is_possible_movement(self.mPosX, self.mPosY, self.mPiece, next_rotation):
                        self.mRotation = next_rotation
                        should_update_main_display = True
                # elif event == ControlsEvent.BTN_A_PRESSED:
                #     # Drop the piece down as far as possible
                #     while self.is_possible_movement(self.mPosX, self.mPosY, self.mPiece, self.mRotation):
                #         self.mPosY += 1
                #     self.mPosY -= 1 # Step back to the valid position
                    
                #     self.store_piece(self.mPosX, self.mPosY, self.mPiece, self.mRotation)
                #     self.delete_possible_lines()
                #     if self.is_game_over():
                #         # Reset board map
                #         self.__board = [[BoardBlock() for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
                #         self.create_new_piece()
                #     else:
                #         self.create_new_piece()

        if current_time - self.mTime1 >= self.curr_drop_interval:
            cleared = 0
            if self.is_possible_movement(self.mPosX, self.mPosY + 1, self.mPiece, self.mRotation):
                self.mPosY += 1
            else:
                self.store_piece(self.mPosX, self.mPosY, self.mPiece, self.mRotation)
                cleared = self.delete_possible_lines()
            
            if cleared > 0:
                self.lines_cleared_total += cleared
                self._recalculate_level()
                self._add_score_for_line_clear(cleared)
            
            if self.is_game_over():
                time.sleep(1)
                self.start_new_game()
            else:
                self.create_new_piece()
            
            should_update_main_display = True
            self.mTime1 = current_time
        
        if should_update_main_display:
            self.console.draw_main_display(self.render_board())
            self.console.commit_displays()
            
    def deinit(self) -> None:
        print("TetrisCartridge deinitialized")
    
    def render_board(self) -> List[List[tuple]]:
        print(f"mPosX: {self.mPosX}, mPosY: {self.mPosY}, mPiece: {self.mPiece}, mRotation: {self.mRotation}, mTime1: {self.mTime1}, mColor: {self.mColor}")
        colored_board = [[block.get_color() for block in row] for row in self.__board]
        PIECE_BLOCKS = 5
        for i1, i2 in zip(range(self.mPosX, self.mPosX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            for j1, j2 in zip(range(self.mPosY, self.mPosY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                if PIECES[self.mPiece][self.mRotation][j2][i2] != 0:
                    if 0 <= i1 < config.MAIN_MATRIX_WIDTH and 0 <= j1 < config.MAIN_MATRIX_HEIGHT:
                        colored_board[j1][i1] = self.mColor
        return colored_board
