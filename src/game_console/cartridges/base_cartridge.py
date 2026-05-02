from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from console.game_console import GameConsole
    from console.controls import ControlsEvent


class GameCartridge(ABC):
    """Abstract base class for game cartridges."""
    
    @abstractmethod
    def init(self, game_console: 'GameConsole') -> None:
        """
        Initialize the game cartridge.
        
        Args:
            game_console: Reference to the GameConsole instance
        """
        pass

    @abstractmethod
    def force_update(self) -> None:
        """
        Force the update of all displays, for example after game unpause.
        """
        pass
    
    @abstractmethod
    def start_new_game(self) -> None:
        """
        Starts the game itself or restarts it in case it already runs.
        """
        pass
    
    @abstractmethod
    def tick(self, current_time: float, controls_events: List['ControlsEvent']) -> None:
        """
        Update game state for the current frame.
        
        Args:
            current_time: Current game time in seconds
            controls_events: List of control events that occurred this frame
        """
        pass
    
    @abstractmethod
    def deinit(self) -> None:
        """
        Clean up resources when removing the cartridge.
        """
        pass

    def can_enter_screensaver(self) -> bool:
        """
        Returns whether the console may switch to screensaver mode right now.
        """
        return True
