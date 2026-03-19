from typing import List, TYPE_CHECKING
from cartridges.base_cartridge import GameCartridge
import config
from console.controls import ControlsEvent

if TYPE_CHECKING:
    from console.game_console import GameConsole


class TestCartridge(GameCartridge):
    
    def __init__(self):
        self.console = None
        self.__i = 0
    
    def init(self, game_console: 'GameConsole') -> None:
        self.console = game_console
        print("TestCartridge initialized")
    
    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        if controls_events:
            print(controls_events)
            if ControlsEvent.BTN_LEFT_PRESSED:
                self.__i = self.__i - 1
                if self.__i < 0:
                    self.__i = config.MAIN_MATRIX_PIX_COUNT - 1
            if ControlsEvent.BTN_RIGHT_PRESSED:
                self.__i = self.__i + 1
                if self.__i >= config.MAIN_MATRIX_PIX_COUNT:
                    self.__i = 0
            
    
    def deinit(self) -> None:
        """Clean up the test cartridge."""
        print("TestCartridge deinitialized")
