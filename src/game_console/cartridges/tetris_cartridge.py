import time
from typing import List, TYPE_CHECKING
from cartridges.base_cartridge import GameCartridge
import config
import random
from console.controls import ControlsEvent, ControlsState

if TYPE_CHECKING:
    from console.game_console import GameConsole

# inspired by Javier Lopez's work
# https://javilop.com/gamedev/tetris-tutorial-in-c-platform-independent-focused-in-game-logic-for-beginners/

PIECE_DROP_PERIOD_S = 0.5 
PIECE_FAST_DOWN_PERIOD_S = 0.05 

def _rotate_piece(piece):
    """Rotate a piece 90 degrees clockwise."""
    return [list(row) for row in zip(*piece[::-1])]

PIECE_BLOCKS = 5
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
        self.__console = None
        self.__board = []
        self.__currPiecePosX = 0
        self.__currPiecePosY = 0
        self.__currPieceId = 0
        self.__currPieceRotation = 0
        self.__pieceLastDropTime = 0.0
        self.__pieceLastFastDownDropTime = 0.0
        self.__currPieceColor = (0,0,0)
    
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
        self.start_new_game()
    
    def start_new_game(self) -> None:
        self.__board = [[BoardBlock() for _ in range(config.MAIN_MATRIX_WIDTH)] for _ in range(config.MAIN_MATRIX_HEIGHT)]
        self.__pieceLastDropTime = 0.0
        self.__pieceLastFastDownDropTime = 0.0
        self.__console.play_music()
        self.create_new_piece()
        
    def create_new_piece(self) -> None:
        self.__currPieceId = random.randrange(len(PIECES))
        self.__currPieceRotation = random.randrange(4)
        self.__currPiecePosX = (config.MAIN_MATRIX_WIDTH // 2) - 2 
        self.__currPiecePosY = -2 
        self.__currPieceColor = random.choice(COLORS)
    
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
                        self.__board[j1][i1].set_color(self.__currPieceColor)
                        
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
             
    def delete_possible_lines(self):
        """Delete all the lines that should be removed."""
        for j in range(config.MAIN_MATRIX_HEIGHT):
            filled_count = 0
            for i in range(config.MAIN_MATRIX_WIDTH):
                if not self.__board[j][i].is_free():
                    filled_count += 1
            if filled_count == config.MAIN_MATRIX_WIDTH:
                self.__CLEAR_LINE_SOUND.play()
                self.delete_line(j)

    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        # Initialize timer on the first tick
        if self.__pieceLastDropTime == 0.0:
            self.__pieceLastDropTime = current_time

        should_update_main_display = False
        if controls_events:
            for event in controls_events:
                if event == ControlsEvent.BTN_LEFT_PRESSED:
                    if self.is_possible_movement(self.__currPiecePosX - 1, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation):
                        self.__currPiecePosX -= 1
                        should_update_main_display = True
                        # self.__MOVE_PIECE_SOUND.play()
                elif event == ControlsEvent.BTN_RIGHT_PRESSED:
                    if self.is_possible_movement(self.__currPiecePosX + 1, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation):
                        self.__currPiecePosX += 1
                        should_update_main_display = True
                        # self.__MOVE_PIECE_SOUND.play()
                elif event == ControlsEvent.BTN_DOWN_PRESSED:
                    # Drop piece down immediately
                    if self.is_possible_movement(self.__currPiecePosX, self.__currPiecePosY + 1, self.__currPieceId, self.__currPieceRotation):
                        self.__drop_the_piece()
                        should_update_main_display = True
                elif event == ControlsEvent.BTN_UP_PRESSED:
                    # Rotate the piece independently
                    next_rotation = (self.__currPieceRotation + 1) % 4
                    if self.is_possible_movement(self.__currPiecePosX, self.__currPiecePosY, self.__currPieceId, next_rotation):
                        self.__currPieceRotation = next_rotation
                        should_update_main_display = True
                        self.__ROTATE_PIECE_SOUND.play()

        if current_time - self.__pieceLastDropTime > PIECE_DROP_PERIOD_S:
            self.__drop_the_piece()
                    
            should_update_main_display = True
            self.__pieceLastDropTime = current_time
        
        if current_time - self.__pieceLastFastDownDropTime > PIECE_FAST_DOWN_PERIOD_S:
            if ControlsState.BTN_DOWN_HOLD in self.__console.get_active_control_states():
                self.__drop_the_piece()
                    
                should_update_main_display = True
                self.__pieceLastFastDownDropTime = current_time
            else:
                self.__pieceLastFastDownDropTime = 0.0
        
        if should_update_main_display:
            self.__console.draw_main_display(self.render_board())
            self.__console.commit_displays()

    def __drop_the_piece(self):
        if self.is_possible_movement(self.__currPiecePosX, self.__currPiecePosY + 1, self.__currPieceId, self.__currPieceRotation):
            self.__currPiecePosY += 1
        else:
            self.store_piece(self.__currPiecePosX, self.__currPiecePosY, self.__currPieceId, self.__currPieceRotation)
            self.__PIECE_FALLING_SOUND.play()
            self.delete_possible_lines()
                
            if self.is_game_over():
                self.__console.pause_music()
                self.__GAME_OVER_SOUND.play()
                time.sleep(3)
                self.start_new_game()
            else:
                self.create_new_piece()
            
    def deinit(self) -> None:
        print("TetrisCartridge deinitialized")
    
    def render_board(self) -> List[List[tuple]]:
        print(f"mPosX: {self.__currPiecePosX}, mPosY: {self.__currPiecePosY}, mPiece: {self.__currPieceId}, mRotation: {self.__currPieceRotation}, mTime1: {self.__pieceLastDropTime}, mColor: {self.__currPieceColor}")
        colored_board = [[block.get_color() for block in row] for row in self.__board]
        for i1, i2 in zip(range(self.__currPiecePosX, self.__currPiecePosX + PIECE_BLOCKS), range(PIECE_BLOCKS)):
            for j1, j2 in zip(range(self.__currPiecePosY, self.__currPiecePosY + PIECE_BLOCKS), range(PIECE_BLOCKS)):
                if PIECES[self.__currPieceId][self.__currPieceRotation][j2][i2] != 0:
                    if 0 <= i1 < config.MAIN_MATRIX_WIDTH and 0 <= j1 < config.MAIN_MATRIX_HEIGHT:
                        colored_board[j1][i1] = self.__currPieceColor
        return colored_board

    def force_update(self) -> None:
        self.__console.draw_main_display(self.render_board())
        self.__console.commit_displays()