from typing import List, TYPE_CHECKING
from cartridges.base_cartridge import GameCartridge
from console.controls import ControlsEvent

if TYPE_CHECKING:
    from console.game_console import GameConsole


class TestCartridge(GameCartridge):
    
    def __init__(self):
        self.console = None
        print("TestCartridge initialized")
    
    def init(self, game_console: 'GameConsole') -> None:
        self.console = game_console
    
    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        if controls_events:
            print(controls_events)
    
    def deinit(self) -> None:
        """Clean up the test cartridge."""
        print("TestCartridge deinitialized")
        if self.console:
            self.console.led_matrix.clear()
            self.console.led_matrix.show()
